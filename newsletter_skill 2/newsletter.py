#!/usr/bin/env python3
"""
5 Minūtes Latvijā — Weekly Newsletter Generator + Sender
Premium Latvian digital newspaper delivered every Tuesday at 10:00 EET.
Covers the previous Monday–Sunday news cycle only.
"""

import os
import json
import hmac
import hashlib
import base64
import anthropic
from datetime import datetime, timedelta
from send_gmail import send_single


SYSTEM_PROMPT = """You are the editor-in-chief of a premium modern Latvian digital newspaper delivered by email every Tuesday at 10:00.

This is NOT a generic newsletter. This is a curated, internet-native, modern Latvian weekly briefing designed to make readers feel: informed, ahead of everyone else, culturally updated, connected to Latvia, smarter in under 5 minutes.

AUDIENCE: ALL Latvians — students, young professionals, families, entrepreneurs, creatives, athletes, normal people who want a faster, cleaner way to understand what happened last week.

═══════════════════════════════════════════
TONE — CALIBRATED
═══════════════════════════════════════════

Write like a SENIOR NEWSPAPER EDITOR with taste. Confident, observational, lightly edged where it earns it.

The writing should feel:
- premium, intelligent, calm, modern, natural
- sharp where precision lands a point
- occasionally witty (rarely, never forced)
- restrained — confidence comes from accuracy, not volume

The writing must NEVER feel:
- dramatic ("Latvija ir oficiāli iegājusi laikmetā…" — NO)
- punchline-driven ("Rēķins jau parādās." / "Sākas spēle no jauna." — NO)
- "trying to sound cool" (sarcastic kickers, ironic asides, forced rule-of-three closings)
- bloggy ("Vārīt, filtrēt vai pieņemt…" — NO)

CONCLUSION LINES ("Secinājums:") should be ONE crisp observation — observational, sometimes lightly edged, NEVER a punchline. Aim for the precision of a senior editor's print column closer. Examples of the right register:
- "Tas vairs nav abstrakta drošības diskusija."
- "Atbilde ir budžetā, nevis paziņojumos."
- "Cipari runā skaļāk par solījumiem."

Examples of what to AVOID (too punchline-y):
- "Beigas. Cauri."
- "Rēķins jau parādās."
- "Spēle sākas no jauna."

The bite comes from observation, not flourish. If a closing line feels like it's reaching for a mic-drop, cut it and write the plain version.

═══════════════════════════════════════════
DATE LOGIC — STRICT
═══════════════════════════════════════════

The newsletter is sent Tuesday at 10:00. Coverage window is the **PREVIOUS Monday through Sunday only**. The user prompt will give you the exact date range — respect it strictly.

Do NOT include:
- News from the current Monday or Tuesday morning (the day before / day of sending)
- Stale news older than the previous week
- News you cannot date-verify

If a story broke this Monday or this morning, save it for next week.

═══════════════════════════════════════════
LANGUAGE — NATURAL MODERN LATVIAN
═══════════════════════════════════════════

Write the entire newsletter in Latvian.

Use natural Latvian. Avoid:
- Direct translations from English that sound awkward ("Briselei tikko nodota nauda" — instead: "Latvija saņēmusi … no ES fonda" or "Latvijai piešķirti …")
- Anglicisms unless they're genuinely standard ("startup" is fine; "freelanceris" is fine; many tech terms are fine)
- Folksy phrasings ("filtra krūku" → "ūdens filtrs" or "filtrēšanas krūze")
- Forced humor that won't translate cleanly

When in doubt, say it plainly. Latvian editorial prose values precision over flourish.

═══════════════════════════════════════════
EDITORIAL RULE
═══════════════════════════════════════════

Your job is NOT to summarize random news. Your job is to FILTER and select ONLY the most important, culturally relevant, discussed, useful, conversation-worthy stories. Every story must answer: "Why should someone in Latvia actually care?"

Skip: random crime stories, filler politics, minor scandals, repetitive government statements, low-impact local incidents, gossip, ragebait, conspiracy framing, unverified rumors.

Prioritize: economic changes, salary trends, inflation, housing, AI / technology, internet culture, major Latvian achievements (any field), policy with real impact, defence / security developments, cultural moments, major events.

SOURCES TO CROSS-REFERENCE:
Latvian: Delfi, TVNET, LSM, Diena, Ir.lv, NRA, Labs of Latvia, Baltic News Network, CSP statistics, Bank of Latvia, Riga municipality, government announcements, Latvian Reddit / Twitter / TikTok.
International: Reuters, Bloomberg, FT, The Economist, Morning Brew, Semafor, TechCrunch, Reddit, Twitter/X, TikTok.

═══════════════════════════════════════════
SPORTS — NATURAL BALANCE, NEVER FOOTBALL-DEFAULT
═══════════════════════════════════════════

Check ALL major Latvian sports each week BEFORE choosing what to cover. Then write about whatever actually had a notable event that week — not a forced rotation.

Disciplines to scan weekly:
- Basketball (national team, Euroleague/EuroCup Latvian players, NBL)
- Hockey (national team, Latvian NHL/KHL players, Dinamo)
- Tennis (Ostapenko, Sevastova, Marcinkēvičs and other Latvian ATP/WTA results)
- Olympic sports (luge, bobsled, skeleton, athletics, weightlifting — Latvia has strong athletes)
- Combat sports (MMA, boxing, Latvian fighters internationally)
- Motorsports
- Major Baltic competitions

If basketball had a major game and hockey had nothing — lead with basketball. If a Latvian tennis player won a tournament — that may be the only sports item that week. Don't force balance for its own sake; let the week's actual events decide.

Virslīga football appears ONLY if something culturally exceptional happened (a record, a viral moment, a national-level controversy). Otherwise skip it entirely.

If nothing major happened in Latvian sports that week, write ONE short item. Never pad.

═══════════════════════════════════════════
VISUAL / FORMATTING
═══════════════════════════════════════════

This is a modern digital newspaper. Use:
- Clean section dividers, strong typography hierarchy
- Generous whitespace, minimalism
- Short, declarative sentences

Do NOT use:
- Emojis (anywhere, ever)
- Loud internet slang
- Startup-style bullet-point chaos
- Excessive bold or italic emphasis

═══════════════════════════════════════════
OUTPUT STRUCTURE — FOLLOW EXACTLY
═══════════════════════════════════════════

# 5 Minūtes Latvijā

*Par ko Latvija runāja šonedēļ.*

---

## LATVIJAS GALVENIE STĀSTI

[Exactly 5 stories from the coverage week. For each:]

### [N]. [Clean headline in Latvian]

**Kas notika:** (2–3 sentences. Plain. Factual.)
**Kāpēc tas svarīgi:** (1–2 sentences. Real-life impact.)
**Ko cilvēki saka:** (1 sentence. Public sentiment.)
**Secinājums:** (ONE crisp observation. Lightly edged where it earns it. Never a punchline.)

---

## EKONOMIKA & IESPĒJAS

[Exactly 2 short items on money / salaries / inflation / startups / AI / work / housing. Plain prose. Who benefits, who loses, why it matters to ordinary Latvians.]

### [Headline]
[Body paragraph]

### [Headline]
[Body paragraph]

---

## INTERNETS & KULTŪRA

[ONE viral discussion, trend, internet debate, creator moment, or cultural conversation from the coverage week. Slightly lighter — but still restrained, premium. No cringe humor.]

### [Headline]
[2–3 short paragraphs.]

---

## SPORTS & MOMENTI

[Whatever Latvian sports actually mattered last week. Balanced naturally — if one discipline dominated, lead with it. One to two short paragraphs total. Never pad.]

### [Headline]
[Short paragraph]

---

## KO DARĪT ŠONEDĒĻ

[ONE genuinely interesting event happening THIS week or weekend. Include city, date, time / price, who it's for, why it matters. No generic events.]

### [Event name]
**[City] · [Date] · [Time / Price]**
[2–3 sentence recommendation in editor's voice.]

---

## ĀTRIE JAUNUMI

[5–8 one-line updates on transportation, prices, tech, weather, startup launches, infrastructure, public warnings, airline news, AI tools, sports moments. Each item one clean sentence on its own line.]

---

## NEDĒĻAS NOVĒROJUMS

**Novērojums:** [One observation about what's actually happening beneath the news.]

**Prognoze:** [One specific, grounded prediction.]

**Sekot līdzi:** [One trend worth watching.]

═══════════════════════════════════════════
FINAL QUALITY GATE
═══════════════════════════════════════════

Before outputting, silently verify:
- Tone is confident with observational edge — never dramatic, never trying-too-hard
- Every "Secinājums:" is a crisp observation, not a punchline
- Latvian reads naturally, not translated-from-English
- Stories are from the correct coverage week only
- Sports section reflects what actually happened that week (not forced football)
- No emojis, no startup energy, no forced humor
- Length is 4–6 minute read, dense, no filler

If any check fails — REWRITE before outputting.

OUTPUT: Return ONLY the newsletter in markdown, in Latvian. No preamble, no commentary. Just the newsletter.
"""


LATVIAN_WEEKDAYS = {
    0: "Pirmdiena", 1: "Otrdiena", 2: "Trešdiena", 3: "Ceturtdiena",
    4: "Piektdiena", 5: "Sestdiena", 6: "Svētdiena"
}

LATVIAN_MONTHS = {
    1: "janvāris", 2: "februāris", 3: "marts", 4: "aprīlis",
    5: "maijs", 6: "jūnijs", 7: "jūlijs", 8: "augusts",
    9: "septembris", 10: "oktobris", 11: "novembris", 12: "decembris"
}

LATVIAN_MONTHS_GENITIVE = {
    1: "janvāra", 2: "februāra", 3: "marta", 4: "aprīļa",
    5: "maija", 6: "jūnija", 7: "jūlija", 8: "augusta",
    9: "septembra", 10: "oktobra", 11: "novembra", 12: "decembra"
}


def format_latvian_date(dt: datetime) -> str:
    """E.g. 'Otrdiena, 12. maijs 2026'."""
    return f"{LATVIAN_WEEKDAYS[dt.weekday()]}, {dt.day}. {LATVIAN_MONTHS[dt.month]} {dt.year}"


def format_latvian_date_short(dt: datetime) -> str:
    """E.g. '12. maijs 2026'."""
    return f"{dt.day}. {LATVIAN_MONTHS[dt.month]} {dt.year}"


def get_coverage_window(send_date: datetime) -> tuple[datetime, datetime]:
    """
    For a Tuesday send date, coverage is the previous Monday through Sunday.
    Tuesday 12 May → Monday 4 May ... Sunday 10 May.
    """
    days_since_monday = send_date.weekday()  # Tue = 1
    coverage_end = (send_date - timedelta(days=days_since_monday + 1)).replace(
        hour=23, minute=59, second=59, microsecond=0
    )
    coverage_start = (coverage_end - timedelta(days=6)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    return coverage_start, coverage_end


def get_issue_number():
    """Internal tracking only — not shown to readers."""
    counter_file = "issue_counter.txt"
    if os.path.exists(counter_file):
        with open(counter_file, "r") as f:
            n = int(f.read().strip()) + 1
    else:
        n = 1
    with open(counter_file, "w") as f:
        f.write(str(n))
    return n


def generate_newsletter(issue_number: int) -> str:
    """Generate the newsletter using Claude with web search."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    today = datetime.now()
    coverage_start, coverage_end = get_coverage_window(today)

    today_lv = format_latvian_date(today)
    cov_start_lv = format_latvian_date(coverage_start)
    cov_end_lv = format_latvian_date(coverage_end)

    user_prompt = f"""Šodiena: {today_lv}.

COVERAGE WINDOW (STRICT):
- From: {cov_start_lv}
- To:   {cov_end_lv}

Cover ONLY news, events, and developments that happened within this window. Do NOT include anything from today, yesterday (Monday), or before {cov_start_lv}.

Search the web thoroughly for stories from this window relevant to Latvia:
- Major Latvian news (politics, economy, society, culture, security)
- Baltic business and startup news
- Viral / trending topics among Latvians
- Major upcoming events in Latvia THIS week or weekend (for "Ko darīt šonedēļ" — these can be future-dated)
- European / international news with direct impact on Latvia
- Latvian sports achievements across all disciplines — scan basketball, hockey, tennis, Olympic sports, combat sports, athletics. Cover whichever actually had a notable event that week. Do NOT default to football.
- AI / technology / money trends affecting ordinary Latvians

Then generate the full "5 Minūtes Latvijā" newsletter following the structure and editorial standards from your system instructions.

Quality bar: premium, curated, confident, observational. Would a discerning Latvian reader forward this Tuesday morning?

Output the complete newsletter in Latvian, in markdown. No preamble."""

    print(f"Generating newsletter for {today_lv}")
    print(f"Coverage: {cov_start_lv} → {cov_end_lv}")

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4500,
        system=SYSTEM_PROMPT,
        tools=[{
            "type": "web_search_20250305",
            "name": "web_search"
        }],
        messages=[{"role": "user", "content": user_prompt}]
    )

    newsletter_text = ""
    for block in response.content:
        if hasattr(block, 'type') and block.type == "text":
            newsletter_text += block.text

    return newsletter_text.strip()


def make_unsub_token(email: str) -> str:
    """Generate a signed unsubscribe token."""
    secret = os.environ.get("UNSUB_SECRET", "change-this-secret")
    email_b64 = base64.urlsafe_b64encode(email.encode()).decode()
    sig = hmac.new(secret.encode(), email.encode(), hashlib.sha256).hexdigest()[:16]
    return f"{email_b64}.{sig}"


def markdown_to_html(markdown_text: str, subscriber_email: str = "") -> str:
    """Convert newsletter markdown to premium newspaper-style HTML email.
    Pass subscriber_email to embed a personal one-click unsubscribe link.
    """
    import re

    lines = markdown_text.split('\n')
    html_lines = []
    skipped_first_h1 = False

    for line in lines:
        stripped = line.strip()

        # Skip the title H1 (rendered in masthead)
        if not skipped_first_h1 and stripped.startswith('# '):
            skipped_first_h1 = True
            continue

        # Empty line — spacing
        if stripped == '':
            html_lines.append('<div style="height:10px"></div>')
            continue

        # Horizontal rule
        if stripped == '---':
            html_lines.append(
                '<hr style="border:none;border-top:1px solid #d0ccc0;margin:36px 0">'
            )
            continue

        # Section header — RED small caps newspaper-style
        if stripped.startswith('## '):
            text = stripped[3:]
            html_lines.append(
                f'<p class="section-lbl" style="font-family:Georgia,\'Times New Roman\',serif;'
                f'font-size:11px;font-weight:700;color:#9e1c20;'
                f'letter-spacing:3.5px;text-transform:uppercase;margin:34px 0 18px 0;'
                f'padding-bottom:10px;border-bottom:1.5px solid #1a1a1a">{text}</p>'
            )
            continue

        # Story headline
        if stripped.startswith('### '):
            text = stripped[4:]
            text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
            html_lines.append(
                f'<h3 class="h3" style="font-family:Georgia,\'Times New Roman\',serif;'
                f'font-size:24px;font-weight:700;color:#1a1a1a;line-height:1.22;'
                f'margin:26px 0 12px 0;letter-spacing:-0.4px">{text}</h3>'
            )
            continue

        # Italic-only tagline (skip — masthead handles it)
        if stripped.startswith('*') and stripped.endswith('*') and not stripped.startswith('**'):
            continue

        # Body paragraph
        text = stripped
        text = re.sub(r'\*\*(.+?)\*\*', r'<strong style="color:#1a1a1a">\1</strong>', text)
        text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
        text = re.sub(
            r'`(.+?)`',
            r'<code style="background:#f0ede4;padding:2px 5px;border-radius:3px;'
            r'font-family:monospace;font-size:13px">\1</code>',
            text
        )

        html_lines.append(
            f'<p class="body-p" style="font-family:Georgia,\'Times New Roman\',serif;'
            f'font-size:15.5px;color:#2a2a2a;line-height:1.78;margin:10px 0">{text}</p>'
        )

    body_content = '\n'.join(html_lines)

    today = datetime.now()
    masthead_date = format_latvian_date_short(today)
    masthead_weekday = LATVIAN_WEEKDAYS[today.weekday()]
    # Display: "12. maijs · Otrdiena"
    masthead_display = f"{masthead_date} &nbsp;·&nbsp; {masthead_weekday}"

    # Build unsubscribe link
    unsub_base = os.environ.get("UNSUB_BASE_URL", "").rstrip("/")
    if subscriber_email and unsub_base:
        token = make_unsub_token(subscriber_email)
        unsub_url = f"{unsub_base}/unsubscribe?token={token}"
        unsub_line = (
            f'<a href="{unsub_url}" '
            f'style="color:#9e1c20;text-decoration:none;font-size:11px;'
            f'letter-spacing:1.5px;text-transform:uppercase;font-weight:600">'
            f'Atrakstīties</a>'
        )
    else:
        unsub_line = ''

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>5 Minūtes Latvijā · {masthead_date}</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&display=swap" rel="stylesheet">
<style>
  @media only screen and (max-width: 640px) {{
    .outer-td    {{ padding: 0 !important; }}
    .card        {{ width: 100% !important; }}
    .pad         {{ padding-left: 24px !important; padding-right: 24px !important; }}
    .pad-top     {{ padding-top: 36px !important; }}
    .pad-body    {{ padding: 8px 24px 28px 24px !important; }}
    .pad-bottom  {{ padding: 0 24px 36px 24px !important; }}
    .pad-footer  {{ padding: 20px 24px !important; }}
    .title       {{ font-size: 48px !important; letter-spacing: -1.5px !important; }}
    .meta-right  {{ display: none !important; }}
    .h3          {{ font-size: 20px !important; }}
    .body-p      {{ font-size: 15px !important; line-height: 1.7 !important; }}
    .section-lbl {{ font-size: 10px !important; }}
    .footer-right {{ display: none !important; }}
    .unsub-mobile {{ display: block !important; margin-top: 8px !important; }}
  }}
</style>
</head>
<body style="margin:0;padding:0;background-color:#e8e4da;font-family:Georgia,'Times New Roman',serif">

  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#e8e4da">
    <tr>
      <td class="outer-td" align="center" style="padding:48px 16px">

        <table class="card" width="640" cellpadding="0" cellspacing="0"
               style="max-width:640px;width:100%;background:#fbf9f3;
                      box-shadow:0 2px 40px rgba(0,0,0,0.07)">

          <!-- Red rule -->
          <tr>
            <td style="height:2px;background:#9e1c20;font-size:0;line-height:0">&nbsp;</td>
          </tr>

          <!-- Masthead -->
          <tr>
            <td class="pad pad-top" style="padding:52px 60px 44px 60px">

              <!-- Date row -->
              <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px">
                <tr>
                  <td align="left" style="font-family:Georgia,serif;font-size:10px;
                             font-weight:500;color:#888;letter-spacing:2.5px;
                             text-transform:uppercase">
                    Iknedēļas izdevums
                  </td>
                  <td class="meta-right" align="right" style="font-family:Georgia,serif;font-size:10px;
                             font-weight:500;color:#888;letter-spacing:2.5px;
                             text-transform:uppercase">
                    Otrdienās plkst. 10:00
                  </td>
                </tr>
              </table>

              <!-- Thin rule -->
              <div style="border-top:1px solid #1a1a1a"></div>

              <!-- Title -->
              <h1 class="title" style="font-family:'Playfair Display',Georgia,'Times New Roman',serif;
                         line-height:0.92;letter-spacing:-2px;
                         margin:22px 0;font-size:64px;font-weight:800;text-align:left">
                <span style="color:#9e1c20">5 Minūtes</span><br>
                <span style="color:#1a1a1a">Latvijā</span>
              </h1>

              <!-- Thick rule -->
              <div style="border-top:2px solid #1a1a1a;margin-bottom:20px"></div>

              <!-- Date + pub line -->
              <p style="font-family:Georgia,serif;font-size:10px;font-weight:500;
                        color:#888;letter-spacing:2.5px;text-transform:uppercase;
                        margin:0 0 14px 0">
                {masthead_display} &nbsp;·&nbsp; ~5 min lasījums
              </p>

              <!-- Tagline -->
              <p style="font-family:Georgia,serif;font-size:16px;font-style:italic;
                        color:#888;margin:0;line-height:1.5">
                Par ko Latvija runāja šonedēļ.
              </p>

            </td>
          </tr>

          <!-- Body -->
          <tr>
            <td class="pad-body" style="padding:8px 60px 36px 60px">
              {body_content}
            </td>
          </tr>

          <!-- "Did we miss something?" -->
          <tr>
            <td class="pad-bottom" style="padding:0 60px 52px 60px">
              <div style="border-top:1px solid #d0ccc0;border-bottom:1px solid #d0ccc0;
                          padding:28px 0;text-align:center">
                <p style="font-family:Georgia,serif;font-size:10px;font-weight:700;
                          color:#9e1c20;letter-spacing:3px;text-transform:uppercase;
                          margin:0 0 10px 0">
                  Vai mēs kaut ko palaidām garām?
                </p>
                <p style="font-family:Georgia,serif;font-size:15px;color:#555;
                          line-height:1.65;margin:0;font-style:italic">
                  Labākie norādījumi nāk no lasītājiem. Atbildiet uz šo e-pastu — pastāstiet, kāds stāsts jums šonedēļ palika prātā.
                </p>
              </div>
              <p style="font-family:Georgia,serif;font-size:15px;color:#888;
                        line-height:1.6;margin:28px 0 0 0;text-align:center;font-style:italic">
                Tās ir piecas minūtes. Tiekamies nākamajā otrdienā.
              </p>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td class="pad-footer" style="border-top:1px solid #d0ccc0;padding:24px 60px;
                       background:#fbf9f3">
              <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                  <td style="font-family:Georgia,serif;font-size:13px;
                             font-weight:700;color:#1a1a1a;letter-spacing:-0.3px">
                    <span style="color:#9e1c20">5 Minūtes</span> Latvijā
                    <span class="unsub-mobile" style="display:none;font-size:11px;
                          font-weight:400;color:#888;margin-top:6px">
                      {unsub_line}
                    </span>
                  </td>
                  <td class="footer-right" align="right" style="font-family:Georgia,serif;font-size:11px;
                             color:#888">
                    {unsub_line}
                  </td>
                </tr>
              </table>
            </td>
          </tr>

        </table>

      </td>
    </tr>
  </table>

</body>
</html>"""


def load_subscribers() -> list:
    if not os.path.exists("subscribers.json"):
        return []
    with open("subscribers.json", "r") as f:
        data = json.load(f)
    return data.get("subscribers", [])


def draft_mode():
    """
    MONDAY 10:00 EET — generate newsletter and send ONLY to editor for review.
    Does NOT send to subscribers. Does NOT increment the issue counter.
    Saves draft to drafts/draft_latest.md for the send step to pick up.
    """
    # Peek at next issue number without incrementing
    counter_file = "issue_counter.txt"
    if os.path.exists(counter_file):
        with open(counter_file, "r") as f:
            next_issue = int(f.read().strip()) + 1
    else:
        next_issue = 1

    print(f"Generating draft for issue #{next_issue}...")
    markdown_content = generate_newsletter(next_issue)

    # Save draft
    os.makedirs("drafts", exist_ok=True)
    with open("drafts/draft_latest.md", "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print("Draft saved to drafts/draft_latest.md")

    # Send preview to editor
    editor_email = os.environ.get("EDITOR_EMAIL", os.environ["GMAIL_ADDRESS"])
    html_content = markdown_to_html(markdown_content, subscriber_email=editor_email)

    today = datetime.now()
    subject = f"[DRAFT #{next_issue}] 5 Minūtes Latvijā · {today.day}. {LATVIAN_MONTHS_GENITIVE[today.month]}"

    from send_gmail import send_single
    if send_single(subject=subject, html_content=html_content, to_email=editor_email):
        print(f"Draft sent to editor: {editor_email}")
    else:
        print("Failed to send draft to editor.")


def send_mode():
    """
    TUESDAY 10:00 EET — send the approved draft to all subscribers.
    Increments issue counter. Reads from drafts/draft_latest.md.
    """
    draft_path = "drafts/draft_latest.md"
    if not os.path.exists(draft_path):
        print("No draft found. Run draft mode first (python newsletter.py draft).")
        return

    with open(draft_path, "r", encoding="utf-8") as f:
        markdown_content = f.read()

    issue_number = get_issue_number()  # increments counter here

    # Archive
    date_str = datetime.now().strftime("%Y-%m-%d")
    os.makedirs("sent_issues", exist_ok=True)
    with open(f"sent_issues/izdevums_{issue_number}_{date_str}.md", "w", encoding="utf-8") as f:
        f.write(markdown_content)
    print(f"Archived to sent_issues/izdevums_{issue_number}_{date_str}.md")

    subscribers = load_subscribers()
    if not subscribers:
        print("No subscribers found.")
        return

    print(f"Sending issue #{issue_number} to {len(subscribers)} subscriber(s)...")

    today = datetime.now()
    subject = f"5 Minūtes Latvijā · {today.day}. {LATVIAN_MONTHS_GENITIVE[today.month]}"

    from send_gmail import send_single
    sent = 0
    for subscriber in subscribers:
        email = subscriber.get("email", subscriber) if isinstance(subscriber, dict) else subscriber
        email = email.strip()
        if not email or "@" not in email:
            continue
        html_content = markdown_to_html(markdown_content, subscriber_email=email)
        if send_single(subject=subject, html_content=html_content, to_email=email):
            sent += 1

    print(f"Issue #{issue_number} sent to {sent}/{len(subscribers)} subscribers.")


if __name__ == "__main__":
    import sys
    mode = sys.argv[1] if len(sys.argv) > 1 else "send"
    if mode == "draft":
        draft_mode()
    else:
        send_mode()
