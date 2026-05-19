#!/usr/bin/env python3
"""
5 Minūtes Latvijā — Welcome Email
Sent automatically when a new subscriber is added.

Usage:
  python send_welcome.py someone@email.com
"""

import os
import sys
from send_gmail import send_single


def welcome_html(subscriber_email: str) -> str:
    """Generate welcome email HTML — same identity as the newsletter."""

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
<title>Laipni lūgts — 5 Minūtes Latvijā</title>
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;800&display=swap" rel="stylesheet">
<style>
  @media only screen and (max-width: 640px) {{
    .outer-td  {{ padding: 0 !important; }}
    .card      {{ width: 100% !important; }}
    .pad       {{ padding-left: 24px !important; padding-right: 24px !important; }}
    .title     {{ font-size: 48px !important; }}
    .pad-footer {{ padding: 20px 24px !important; }}
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

          <!-- Masthead — identical to newsletter -->
          <tr>
            <td class="pad" style="padding:52px 60px 44px 60px">

              <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px">
                <tr>
                  <td style="font-family:Georgia,serif;font-size:10px;font-weight:500;
                             color:#888;letter-spacing:2.5px;text-transform:uppercase">
                    Iknedēļas izdevums
                  </td>
                  <td align="right" style="font-family:Georgia,serif;font-size:10px;
                             font-weight:500;color:#888;letter-spacing:2.5px;
                             text-transform:uppercase">
                    Otrdienās plkst. 10:00
                  </td>
                </tr>
              </table>

              <div style="border-top:1px solid #1a1a1a"></div>

              <h1 class="title" style="font-family:'Playfair Display',Georgia,'Times New Roman',serif;
                         line-height:0.92;letter-spacing:-2px;
                         margin:22px 0;font-size:64px;font-weight:800;text-align:left">
                <span style="color:#9e1c20">5 Minūtes</span><br>
                <span style="color:#1a1a1a">Latvijā</span>
              </h1>

              <div style="border-top:2px solid #1a1a1a"></div>

            </td>
          </tr>

          <!-- Welcome body -->
          <tr>
            <td class="pad" style="padding:36px 60px 48px 60px">

              <!-- Section label -->
              <p style="font-family:Georgia,serif;font-size:10px;font-weight:700;
                        color:#9e1c20;letter-spacing:3.5px;text-transform:uppercase;
                        margin:0 0 24px 0;padding-bottom:10px;border-bottom:1.5px solid #1a1a1a">
                Laipni lūgts
              </p>

              <!-- Headline -->
              <h2 style="font-family:'Playfair Display',Georgia,serif;font-size:28px;
                         font-weight:700;color:#1a1a1a;line-height:1.2;
                         letter-spacing:-0.5px;margin:0 0 20px 0">
                Tu esi klāt.
              </h2>

              <!-- Body -->
              <p style="font-family:Georgia,serif;font-size:15.5px;color:#2a2a2a;
                        line-height:1.78;margin:0 0 16px 0">
                Katru otrdienu plkst. 10:00 saņemsi <em>5 Minūtes Latvijā</em> — piecu minūšu iknedēļas apskatu par svarīgāko, kas Latvijā un pasaulē noticis pagājušajā nedēļā.
              </p>

              <p style="font-family:Georgia,serif;font-size:15.5px;color:#2a2a2a;
                        line-height:1.78;margin:0 0 16px 0">
                Ne ziņu apkopojums. Ne garš raksts. Tikai tas, ko tiešām ir vērts zināt — rūpīgi atlasīts, skaidri uzrakstīts.
              </p>

              <p style="font-family:Georgia,serif;font-size:15.5px;color:#2a2a2a;
                        line-height:1.78;margin:0 0 32px 0">
                Ja ir stāsts, ko vajadzētu izskatīt — vai kāds jautājums — vienkārši atbildi uz šo e-pastu.
              </p>

              <!-- Divider -->
              <div style="border-top:1px solid #d0ccc0;margin:0 0 28px 0"></div>

              <!-- Sign-off -->
              <p style="font-family:Georgia,serif;font-size:15px;font-style:italic;
                        color:#888;margin:0;line-height:1.6">
                Tiekamies nākamajā otrdienā.
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
                  </td>
                  <td align="right" style="font-family:Georgia,serif;font-size:11px;color:#888">
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


def send_welcome(email: str) -> bool:
    html = welcome_html(email)
    subject = "Laipni lūgts — 5 Minūtes Latvijā"
    ok = send_single(subject=subject, html_content=html, to_email=email)
    if ok:
        print(f"Welcome email sent to {email}")
    return ok


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python send_welcome.py someone@email.com")
        sys.exit(1)
    email = sys.argv[1].strip()
    send_welcome(email)
