#!/usr/bin/env python3
"""
5 Minūtes Latvijā — Unsubscribe Server
Handles one-click unsubscribe links embedded in every newsletter email.

Deploy free on Railway or Render. Set environment variable:
  UNSUB_SECRET — any long random string (e.g. output of: python3 -c "import secrets; print(secrets.token_hex(32))")

Endpoint:
  GET /unsubscribe?token=<signed_token>
  → Removes subscriber, shows confirmation page.
"""

import os
import json
import hmac
import hashlib
import base64
from datetime import datetime
from flask import Flask, request, abort

app = Flask(__name__)

SUBSCRIBERS_FILE = "subscribers.json"
SECRET = os.environ.get("UNSUB_SECRET", "change-this-secret")


# ─── Token helpers ─────────────────────────────────────────────────────────

def make_token(email: str) -> str:
    """Generate a signed unsubscribe token for an email address."""
    email_b64 = base64.urlsafe_b64encode(email.encode()).decode()
    sig = hmac.new(SECRET.encode(), email.encode(), hashlib.sha256).hexdigest()[:16]
    return f"{email_b64}.{sig}"


def verify_token(token: str) -> str | None:
    """Verify token and return the email, or None if invalid."""
    try:
        email_b64, sig = token.rsplit(".", 1)
        email = base64.urlsafe_b64decode(email_b64.encode()).decode()
        expected_sig = hmac.new(SECRET.encode(), email.encode(), hashlib.sha256).hexdigest()[:16]
        if hmac.compare_digest(sig, expected_sig):
            return email
    except Exception:
        pass
    return None


# ─── Subscriber helpers ─────────────────────────────────────────────────────

def load_subscribers() -> dict:
    if not os.path.exists(SUBSCRIBERS_FILE):
        return {"subscribers": []}
    with open(SUBSCRIBERS_FILE, "r") as f:
        return json.load(f)


def remove_subscriber(email: str) -> bool:
    """Remove subscriber by email. Returns True if found and removed."""
    data = load_subscribers()
    original_count = len(data["subscribers"])
    data["subscribers"] = [
        s for s in data["subscribers"]
        if (s if isinstance(s, str) else s.get("email", "")).lower() != email.lower()
    ]
    removed = len(data["subscribers"]) < original_count
    if removed:
        data["updated"] = datetime.now().isoformat()
        with open(SUBSCRIBERS_FILE, "w") as f:
            json.dump(data, f, indent=2)
    return removed


# ─── Routes ────────────────────────────────────────────────────────────────

@app.route("/unsubscribe")
def unsubscribe():
    token = request.args.get("token", "")
    email = verify_token(token)

    if not email:
        return _page(
            title="Saite nav derīga",
            headline="Saite nav derīga vai ir novecojusi.",
            body="Ja vēlaties atrakstīties, atbildiet uz jebkuru 5 Minūtes Latvijā e-pastu ar vārdu <strong>atrakstīties</strong>.",
            success=False
        ), 400

    removed = remove_subscriber(email)

    if removed:
        return _page(
            title="Atrakstīšanās veiksmīga",
            headline="Jūs esat atrakstīts.",
            body=f"Adrese <strong>{email}</strong> ir noņemta no saraksta. Vairs nesaņemsiet 5 Minūtes Latvijā izdevumus.",
            success=True
        )
    else:
        return _page(
            title="Adrese nav atrasta",
            headline="Adrese nav atrasta.",
            body=f"Adrese <strong>{email}</strong> netika atrasta abonentu sarakstā. Iespējams, esat jau atrakstīts.",
            success=False
        )


@app.route("/health")
def health():
    return {"status": "ok"}, 200


def _page(title: str, headline: str, body: str, success: bool) -> str:
    accent = "#9e1c20"
    return f"""<!DOCTYPE html>
<html lang="lv">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} · 5 Minūtes Latvijā</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&family=Inter:wght@400;500&display=swap');
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    background: #e8e4da;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 40px 20px;
    font-family: Georgia, 'Times New Roman', serif;
  }}
  .card {{
    background: #fbf9f3;
    max-width: 520px;
    width: 100%;
    box-shadow: 0 2px 32px rgba(0,0,0,0.07);
  }}
  .top-rule {{ height: 3px; background: {accent}; }}
  .inner {{ padding: 48px 52px 52px; }}
  .brand {{
    font-family: 'Inter', sans-serif;
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: {accent};
    margin-bottom: 32px;
    display: block;
  }}
  h1 {{
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 32px;
    font-weight: 700;
    color: #1a1a1a;
    line-height: 1.2;
    margin-bottom: 18px;
    letter-spacing: -0.5px;
  }}
  p {{
    font-size: 16px;
    line-height: 1.7;
    color: #444;
  }}
  .rule {{ height: 1px; background: #d0ccc0; margin: 32px 0; }}
  .back {{
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #888;
    text-decoration: none;
  }}
</style>
</head>
<body>
<div class="card">
  <div class="top-rule"></div>
  <div class="inner">
    <span class="brand">5 Minūtes Latvijā</span>
    <h1>{headline}</h1>
    <p>{body}</p>
    <div class="rule"></div>
    <a class="back" href="/">← Atpakaļ</a>
  </div>
</div>
</body>
</html>"""


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
