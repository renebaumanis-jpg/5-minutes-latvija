#!/usr/bin/env python3
"""
Subscriber management CLI for 5 Min Latvija.

Usage:
  python manage_subscribers.py add someone@email.com
  python manage_subscribers.py remove someone@email.com
  python manage_subscribers.py list
  python manage_subscribers.py import emails.txt
"""

import json
import sys
import os
from datetime import datetime

SUBSCRIBERS_FILE = "subscribers.json"


def load() -> dict:
    if not os.path.exists(SUBSCRIBERS_FILE):
        return {"subscribers": [], "updated": ""}
    with open(SUBSCRIBERS_FILE, "r") as f:
        return json.load(f)


def save(data: dict) -> None:
    data["updated"] = datetime.now().isoformat()
    with open(SUBSCRIBERS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add(email: str) -> None:
    email = email.strip().lower()
    if "@" not in email or "." not in email:
        print(f"✗ Invalid email: {email}")
        return

    data = load()
    existing = [s if isinstance(s, str) else s.get("email", "") for s in data["subscribers"]]

    if email in existing:
        print(f"⚠️  Already subscribed: {email}")
        return

    data["subscribers"].append({
        "email": email,
        "subscribed_at": datetime.now().isoformat()
    })
    save(data)
    print(f"✓ Added: {email} ({len(data['subscribers'])} total subscribers)")

    # Send welcome email if Gmail env vars are set
    if os.environ.get("GMAIL_ADDRESS") and os.environ.get("GMAIL_APP_PASSWORD"):
        try:
            from send_welcome import send_welcome
            send_welcome(email)
        except Exception as e:
            print(f"  (Welcome email failed: {e} — send manually: python send_welcome.py {email})")
    else:
        print(f"  (No Gmail env vars — send welcome manually: python send_welcome.py {email})")


def remove(email: str) -> None:
    email = email.strip().lower()
    data = load()
    original_count = len(data["subscribers"])
    
    data["subscribers"] = [
        s for s in data["subscribers"]
        if (s if isinstance(s, str) else s.get("email", "")).lower() != email
    ]
    
    if len(data["subscribers"]) < original_count:
        save(data)
        print(f"✓ Removed: {email} ({len(data['subscribers'])} subscribers remaining)")
    else:
        print(f"⚠️  Not found: {email}")


def list_subscribers() -> None:
    data = load()
    subs = data.get("subscribers", [])
    
    if not subs:
        print("No subscribers yet.")
        print("Add some: python manage_subscribers.py add email@example.com")
        return
    
    print(f"📧 {len(subs)} subscriber(s):")
    print("-" * 40)
    for s in subs:
        if isinstance(s, dict):
            date = s.get("subscribed_at", "")[:10]
            print(f"  {s['email']}  (joined {date})")
        else:
            print(f"  {s}")


def import_from_file(filepath: str) -> None:
    """Import emails from a plain text file (one email per line)."""
    if not os.path.exists(filepath):
        print(f"✗ File not found: {filepath}")
        return
    
    with open(filepath, "r") as f:
        emails = [line.strip() for line in f if line.strip()]
    
    print(f"Importing {len(emails)} emails from {filepath}...")
    for email in emails:
        add(email)


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "add" and len(sys.argv) >= 3:
        add(sys.argv[2])
    elif command == "remove" and len(sys.argv) >= 3:
        remove(sys.argv[2])
    elif command == "list":
        list_subscribers()
    elif command == "import" and len(sys.argv) >= 3:
        import_from_file(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
