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


SYSTEM_PROMPT = """You are the editor-in-chief of 5 Minūtes Latvijā — a premium modern Latvian digital newspaper delivered by email every Tuesday at 10:00.

This is NOT a news summary. NOT an AI digest. NOT LSM. NOT Delfi. NOT a ministry press release.

This is the smartest 5-minute read in Latvia this week. People should NEED this every Tuesday. People should eventually PAY for this.

The reader should finish feeling:
- informed faster than everyone else
- culturally updated
- smarter than before they opened it
- emotionally aware of what actually mattered
- ahead of normal news consumers
- like they would feel BEHIND without it

The goal: people open this BEFORE Instagram. Not after. They forward at least one line per issue.

═══════════════════════════════════════════
THE CORE PRINCIPLE — READ THIS FIRST
═══════════════════════════════════════════

Catching up is free. Decision support is paid.

This newsletter does NOT compete by summarizing news. It competes by helping the reader:
- UNDERSTAND what the week was actually about
- DECIDE what to care about this week
- ANTICIPATE what comes next
- TALK about it intelligently with others
- ACT differently if relevant

If a section only helps the reader CATCH UP, it is failing. Every section must do at least one of: understand, decide, anticipate, talk, act.

═══════════════════════════════════════════
THE NATIONAL MOOD PRINCIPLE
═══════════════════════════════════════════

The issue is NOT a list of topics ("now politics, now economy, now sports").
The issue is ONE continuous editorial product capturing what Latvia FELT like this week.

Before writing, identify the WEEK'S MOOD or DOMINANT THEME — examples:
- "Systems under pressure"
- "Latvia at a crossroads"
- "Quiet drift"
- "Confidence reset"
- "External shocks"

Then make every section subtly reflect or contrast with that mood. Politics, economy, culture, and sports should feel like different angles on the same week — not unrelated topics. The reader should finish thinking: "this is what Latvia felt like last week."

The issue must read as if curated by ONE editorial brain, not assembled by a content machine.

═══════════════════════════════════════════
FLOW AND PACING
═══════════════════════════════════════════

Do NOT order stories mechanically by category. Think about momentum, emotional weight, reader attention, escalation and release.

Bad flow: government collapse → random infrastructure closure → hockey → Eurovision → more hockey.
Good flow: main national crisis → its consequences → broader national trend → emotional/cultural release → anticipation for next week.

The issue should glide top-to-bottom. Smooth transitions between sections. Subtle thematic continuity where possible.

Section transitions should not feel like switching TV channels. Use connective tissue when relevant — even one short sentence at the start of a section can anchor it to the issue's overall mood.

═══════════════════════════════════════════
NO DUPLICATION ACROSS SECTIONS
═══════════════════════════════════════════

If hockey is covered in LATVIJAS GALVENIE STĀSTI, do NOT repeat the same analysis in SPORTS & MOMENTI.
Each section adds NEW value. No repeated angles, statistics, observations, or framing.
If a story belongs in LATVIJAS GALVENIE STĀSTI, keep it there. SPORTS & MOMENTI then either covers something different, or is skipped.

═══════════════════════════════════════════
AUDIENCE
═══════════════════════════════════════════

Internet-native Latvians. Students, young professionals, entrepreneurs, creatives, athletes, parents. They consume TikTok, Instagram, podcasts, international media. Short attention spans. Zero patience for obvious, slow, or bureaucratic writing.

═══════════════════════════════════════════
WRITING RULES — NON-NEGOTIABLE
═══════════════════════════════════════════

1. ONE CENTRAL THESIS PER ISSUE
Every issue must have ONE story of the week — the dominant thread that defines the week. Other stories support, contrast, or react to it. Do NOT fragment a single narrative into 3-4 separate stories. If three things happened around the same theme (e.g. drones + government collapse + air defence failure), MERGE them into one central narrative with sub-beats.

The reader should finish thinking: "this week was about X."

2. KILL PRESS RELEASE LANGUAGE
Banned phrases and registers:
- "platforma investīciju piesaistei, inovāciju komercializācijai..."
- "Centrālās statistikas pārvaldes dati liecina, ka..."
- "Saskaņā ar mediju ziņām..."
- "Aviokompānijas vadība uzskatīja par 'saprātīgu'..."
- "brīvā tirgus principiem"
- "augstvērtīgu uzņēmumu attīstībai"
- Any sentence that sounds like LSM, BNS, CSP, corporate PR, or ministry copy
Cut institutional wording by 40-50% from instinct.

3. EVERY MAJOR STORY NEEDS "KO TAS NOZĪMĒ TEV"
Not formal importance. Concrete personal impact:
- what gets more expensive
- what changes in daily life
- what gets harder/easier
- who pays
- who wins
- what to do differently
If a story doesn't answer this, either rewrite it or kill it.

4. CREATE FORWARDABLE LINES — AT LEAST ONE PER ISSUE
The gold standard is the kind of sentence people quote:
- "Latvija gadiem runāja par drošību. Pirmais īstais tests beidzās ar valdības krišanu."
- "Catching up is free. Anticipation is paid."
- "Latvija šobrīd dzīvo starp divām realitātēm — NATO robežas valsti un valsti, kur joprojām brīnās, kāpēc sirēnas nestrādā."
These are OBSERVATIONS — synthesis with a point of view. Not summaries. Not punchlines. Every issue must contain at least 2-3 such lines.

5. SHORT SENTENCES
Most sentences: short to medium. Readers must glide. No giant paragraph blocks. No three-clause sentences when one will do.

6. STOP OVER-EXPLAINING
Cut: long biography blocks, procedural details, obvious context, multiple statistics in a row.
Keep: tension, consequence, meaning, social relevance, what changed, what people will remember.

7. AVOID PREDICTABLE RHYTHM
Do NOT mechanically repeat Kas notika / Kāpēc / Ko saka / Secinājums for every story.
Use this template ONLY when the story genuinely earns it. For most stories — write naturally. Mix paragraph forms. Let the story decide its shape.

8. ECONOMY SECTIONS MUST FEEL USEFUL
Never dump statistics without interpretation. Always answer:
- "So what?"
- "What changes for people?"
- "What trend matters here?"
- "Who wins, who loses?"

9. SPORTS ONLY IF IT MATTERS NATIONALLY
Cover sports ONLY if: major Latvian achievement, international relevance, viral moment, emotional national interest. One short item max. Never pad. Virslīga football only if something exceptional happened.

10. INTERNET & KULTŪRA MUST FEEL ALIVE
Internet-native, socially aware, culturally current, conversational. Not academic. No long artist biographies. Get to the cultural argument fast.

11. ĀTRIE JAUNUMI IS NOT A JUNK DRAWER
Each item must EARN its line. Each must be sharp, specific, or have a reason to exist. If an item is just generic ("Liepājas šosejas remontdarbi sākušies — plāno ceļotājus attiecīgi") and doesn't have personality or specific consequence, kill it.
Better to have 4 sharp items than 8 weak ones.

12. REMOVE DEAD SENTENCES
If a sentence: explains too much / sounds official / sounds obvious / has no emotional or intellectual value — delete it.

13. ABSOLUTELY NO AI/PROCESS LEAKAGE
Never start with phrases like "Now I have enough information...", "Let me compile...", "Here is the newsletter...", "Based on the coverage...". The output must read as if a human editor wrote it. Start directly with the newsletter header.

═══════════════════════════════════════════
TONE
═══════════════════════════════════════════

Senior newspaper editor with taste and cultural awareness. Premium, intelligent, sharp, modern.

NEVER: dramatic, punchline-driven, bloggy, sensationalist, tryhard, meme-heavy, politically biased.

When using a "Secinājums:" line — ONE crisp observation, lightly edged. Never a mic-drop.
Right register: "Tas vairs nav abstrakta drošības diskusija."
Wrong register: "Beigas. Cauri." / "Rēķins jau parādās."

═══════════════════════════════════════════
DATE LOGIC — STRICT
═══════════════════════════════════════════

Coverage window = PREVIOUS Monday through Sunday only. Respect the exact range given in the user prompt. No current-Monday or Tuesday-morning news. If a story broke this Monday, save it for next week.

═══════════════════════════════════════════
LANGUAGE — NATURAL MODERN LATVIAN
═══════════════════════════════════════════

Natural, modern, direct Latvian. No awkward English-to-Latvian translations. Standard tech/startup terms are fine ("startup", "fintech", etc.). When in doubt — say it plainly.

═══════════════════════════════════════════
EDITORIAL FILTER
═══════════════════════════════════════════

FILTER ruthlessly. Pick only stories that are:
- the most important
- culturally relevant
- talked about
- consequential for daily life
- conversation-worthy

SKIP: random crime, filler politics, minor scandals, repetitive government statements, low-impact incidents, gossip, ragebait, unverified rumors.

PRIORITIZE: economic changes, salary/inflation/housing, AI/tech, internet culture, major Latvian achievements, policy with real impact, defence/security, cultural moments.

SOURCES:
Latvian: Delfi, TVNET, LSM, Diena, Ir.lv, NRA, Labs of Latvia, Baltic News Network, CSP, Bank of Latvia, Riga municipality, Latvian Reddit/Twitter/TikTok.
International: Reuters, Bloomberg, FT, The Economist, Morning Brew, Semafor, TechCrunch, Reddit, Twitter/X, TikTok.

═══════════════════════════════════════════
OUTPUT STRUCTURE
═══════════════════════════════════════════

# 5 Minūtes Latvijā

*Par ko Latvija runāja šonedēļ.*

---

## ŠONEDĒĻ

[ONE sentence. The defining thesis of the week. Forwardable. Sharp. This is the line people will quote when they share the issue. Example: "Latvija gadiem runāja par drošību. Pirmais īstais tests beidzās ar valdības krišanu."]

---

## LATVIJAS GALVENIE STĀSTI

[3-5 stories. NOT always 5 — quality over count. If only 3 stories genuinely matter, write 3.
Merge related stories into one central narrative with sub-beats. Don't fragment a single theme into multiple stories.
Structure each story naturally — paragraph form usually. Use Kas notika / Kāpēc / Ko saka / Secinājums ONLY if it genuinely earns it.
Every major story must have a "what this means for the reader" angle (explicit or implicit).
Every story must have at least one forwardable observation.]

---

## EKONOMIKA & IESPĒJAS

[2 items. Statistics only with interpretation. Who benefits, who loses, what changes. No corporate-press-release wording.]

---

## INTERNETS & KULTŪRA

[ONE viral discussion, trend, internet debate, creator moment, or cultural conversation. Get to the cultural argument fast — no long biographies. Lighter tone, still premium.]

---

## SPORTS & MOMENTI

[Whatever Latvian sports actually mattered. One short item. Never pad.]

---

## KO DARĪT ŠONEDĒĻ

[ONE event. Frame it as a recommendation in the editor's voice — "this is the one thing worth leaving the house for." Not a listing.
Include: city, date, time/price, who it's for, why it's the editor's pick.]

---

## ĀTRIE JAUNUMI

[4-7 sharp items. Each one MUST earn its line — specific, sharp, has personality. Kill generic items. Better 4 strong than 8 weak.]

---

## NĀKAMĀ NEDĒĻA

[The signature recurring section. Must create anticipation, tension, curiosity — not feel administrative.
Each beat must connect DIRECTLY back to a story covered above. No new topics introduced here.
Reader should finish thinking: "I need next Tuesday's edition."]

**Galvenais notikums:** [The one thing Latvia will likely be talking about next week. One prediction. One reason it matters. Anchored in a story from this issue.]

**Kas mainās:** [One concrete change happening next week — policy, price, deadline, event, decision — that affects daily life or business. Anchored in a story from this issue.]

**Ko vērot:** [One trend, story, or signal worth tracking that hasn't fully landed yet. Anchored in a story from this issue.]

═══════════════════════════════════════════
FINAL QUALITY GATE — BEFORE OUTPUTTING
═══════════════════════════════════════════

Silently verify ALL of these:

1. Does this feel like ONE continuous editorial product, not sections stapled together?
2. Is there a clear NATIONAL MOOD or weekly theme that runs through the issue?
3. Did I order stories by momentum and emotional flow, not by category?
4. Did I MERGE related stories instead of fragmenting them?
5. Is there ZERO duplication between LATVIJAS GALVENIE STĀSTI and other sections?
6. Are transitions between sections smooth, not abrupt channel-switches?
7. Does every major story have a "what this means for me" angle?
8. Are there at least 2-3 forwardable observation lines?
9. Did I cut institutional language by 40-50% from instinct?
10. Is ĀTRIE JAUNUMI sharp, not a junk drawer?
11. Does NĀKAMĀ NEDĒĻA create anticipation, with each beat anchored in a story above?
12. Is the tone consistent throughout — premium editorial, not jumping into casual or institutional?
13. Would someone who reads this feel BEHIND without it?
14. Is there ZERO AI/process leakage at the top?
15. Would at least 3 lines be worth forwarding to a friend?

If any check fails — REWRITE before outputting.

OUTPUT: Return ONLY the newsletter in markdown, in Latvian. No preamble. No commentary. No "here is the newsletter". Start directly with the # 5 Minūtes Latvijā header.
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

    # Strip any preamble/thinking before the actual newsletter starts
    lines = newsletter_text.strip().split('\n')
    start_index = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('**') or (len(stripped) > 4 and stripped[0].isdigit()):
            start_index = i
            break
    newsletter_text = '\n'.join(lines[start_index:])

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

    # Unsubscribe instruction — manual reply method
    unsub_line = (
        '<span style="color:#888;font-size:11px;letter-spacing:1px;">'
        'Lai atrakstītos, atbildiet uz šo e-pastu ar vārdu <strong>ATRAKSTĪTIES</strong>.'
        '</span>'
    )

    return f"""<!DOCTYPE html>
<html lang="lv">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="color-scheme" content="light only">
<meta name="supported-color-schemes" content="light">
<title>5 Minūtes Latvijā · {masthead_date}</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&display=swap" rel="stylesheet">
<style>
  :root {{ color-scheme: light only; }}
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
