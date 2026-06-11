"""
REMINDER: You MUST use a 16-character Gmail "App Password", NOT your regular account password.
Generate one at: https://myaccount.google.com/apppasswords (requires 2FA enabled).
"""

import csv
import smtplib
import time
import logging
import os
import re
import random
from email.message import EmailMessage

# ─── CONFIGURATION ───────────────────────────────────────────────────────────
SENDER_EMAIL = "thecryptolawyers.intake@gmail.com"
SENDER_APP_PASSWORD = "yhuhakuutedofxbj"
EMAIL_SUBJECT = "Your Webull case: Settlement path confirmed — Access your terms"
EMAIL_BODY = """Hello,

Your evidence has been reviewed and establishes a credible path toward recovery.

In our prior Webull impersonation cases, 100% of clients who signed the engagement agreement reached a settlement. Past results do not guarantee your outcome, but your case is positioned for a high-probability resolution.

Next step: Submit your loss declaration and sign your engagement letter

1. Submit your intake form: https://crypto-lawyers.github.io/crypto-lawyers-intake/index.html
2. Sign your retainer (password below): https://crypto-lawyers.github.io/crypto-lawyers-intake/retainer.html
3. Your case access password: SOobgj#@D$GiK7fMx9Sy9c3E
4. Read the engagement terms thoroughly before signing. Do not skip any sections.
5. Sign electronically only if you agree with the terms.

After you sign, you'll see simple payment instructions to activate your case.

48-Hour Docket Lock:
Due to the high volume of Webull claims, our Forensic Litigation Division can only hold your case file in the active queue for 48 hours. If the forensic setup retainer is not confirmed within this window, your file will be automatically deferred to the next quarter's review cycle. Earlier execution positions your case for inclusion in the current batch.

Security & Support:
- This password is unique to your case. Keep it confidential.
- We will NEVER ask for this password, sensitive login credentials, or keys via unsolicited email.
- Need help with access or payment routing? Reply directly to this email.

However you decide, please know this: You were not foolish. You were targeted. And you are not alone.

With respect,

Forensic Litigation Division
The Crypto Lawyers, PLLC
Florida Bar No. #1002677
848 Brickell Avenue, Penthouse 5
Miami, Florida 33131

---
This communication does not guarantee recovery. Past results do not guarantee a similar outcome. The Crypto Lawyers, PLLC, 848 Brickell Avenue, Penthouse 5, Miami, FL 33131. Reply "OPT-OUT" to unsubscribe. Keep your password confidential."""

CSV_FILE = r"C:\Users\Hp\Desktop\CUSTOMERS_EMAILS_REMAINING.csv"
SENT_FILE = "sent_emails.txt"
FAILED_FILE = "failed_emails.txt"
EMAIL_COLUMN = "EMAIL"
BATCH_SIZE = 40
START_OFFSET = 0
SLEEP_SECONDS = 20
SLEEP_JITTER = 4
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465
# ─────────────────────────────────────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger(__name__)

EMAIL_REGEX = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")


def is_valid_email(addr: str) -> bool:
    return bool(EMAIL_REGEX.match(addr))


def load_file_set(path: str) -> set[str]:
    if not os.path.isfile(path):
        return set()
    with open(path, encoding="utf-8") as f:
        return {line.strip().lower() for line in f if line.strip()}


def append_to_file(path: str, addr: str) -> None:
    with open(path, "a", encoding="utf-8") as f:
        f.write(addr + "\n")


def load_recipients(path: str, skip_set: set[str]) -> list[str]:
    seen: set[str] = set()
    recipients: list[str] = []
    duplicates = 0
    invalid = 0
    already_sent = 0
    raw_count = 0
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if EMAIL_COLUMN not in (reader.fieldnames or []):
            log.error("CSV must contain a column named '%s'. Found: %s", EMAIL_COLUMN, reader.fieldnames)
            raise SystemExit(1)
        for row in reader:
            raw_count += 1
            if raw_count <= START_OFFSET:
                continue
            addr = row[EMAIL_COLUMN].strip().lower()
            if not addr:
                continue
            if not is_valid_email(addr):
                invalid += 1
                continue
            if addr in seen:
                duplicates += 1
                continue
            if addr in skip_set:
                already_sent += 1
                continue
            seen.add(addr)
            recipients.append(addr)
    if START_OFFSET:
        log.info("Skipped first %d rows (START_OFFSET)", START_OFFSET)
    if already_sent:
        log.info("Skipped %d already-sent address(es)", already_sent)
    if duplicates:
        log.info("Skipped %d duplicate address(es)", duplicates)
    if invalid:
        log.info("Skipped %d invalid address(es)", invalid)
    return recipients


def build_message(sender: str, to: str, subject: str, body: str) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = to
    msg["Subject"] = subject
    msg["Reply-To"] = sender
    msg["List-Unsubscribe"] = f"<mailto:{sender}?subject=OPT-OUT>"
    msg.set_content(body)
    return msg


def send_all_batches(recipients: list[str]) -> None:
    total = len(recipients)
    failed: list[str] = []
    sent_count = 0
    batch_num = 0
    total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE

    for batch_start in range(0, total, BATCH_SIZE):
        batch = recipients[batch_start:batch_start + BATCH_SIZE]
        batch_num += 1
        batch_sent = 0
        batch_failed = 0

        log.info("=== BATCH %d/%d  (%d emails) ===", batch_num, total_batches, len(batch))

        try:
            with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=30) as server:
                server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)

                for idx, recipient in enumerate(batch, start=1):
                    global_idx = batch_start + idx
                    try:
                        msg = build_message(SENDER_EMAIL, recipient, EMAIL_SUBJECT, EMAIL_BODY)
                        server.send_message(msg)
                        append_to_file(SENT_FILE, recipient)
                        sent_count += 1
                        batch_sent += 1
                        log.info("[%d/%d] Sent to: %s", global_idx, total, recipient)
                    except Exception as exc:
                        batch_failed += 1
                        failed.append(recipient)
                        log.info("[%d/%d] Failed: %s -- Reason: %s", global_idx, total, recipient, exc)

                if idx < len(batch):
                    delay = SLEEP_SECONDS + random.uniform(-SLEEP_JITTER, SLEEP_JITTER)
                    time.sleep(delay)

        except smtplib.SMTPAuthenticationError as exc:
            log.error("SMTP auth failed. Reason: %s", exc)
            for addr in batch:
                if addr not in [f for f in failed]:
                    failed.append(addr)
                    batch_failed += 1
            break

        log.info("Batch %d complete: sent %d, failed %d", batch_num, batch_sent, batch_failed)

        if batch_num < total_batches:
            log.info("Pausing 5 min before next batch to respect rate limits...")
            time.sleep(300)

    if failed:
        with open(FAILED_FILE, "a", encoding="utf-8") as f:
            for addr in failed:
                f.write(addr + "\n")
        log.info("Wrote %d failed address(es) to %s", len(failed), FAILED_FILE)

    log.info("=== FINAL SUMMARY ===")
    log.info("Total: %d  Sent: %d  Failed: %d", total, sent_count, len(failed))
    log.info("Sent log: %s  |  Failed log: %s", SENT_FILE, FAILED_FILE)


def main() -> None:
    if not os.path.isfile(CSV_FILE):
        log.error("CSV file not found: %s", CSV_FILE)
        raise SystemExit(1)

    sent_set = load_file_set(SENT_FILE)
    failed_set = load_file_set(FAILED_FILE)
    skip_set = sent_set | failed_set

    recipients = load_recipients(CSV_FILE, skip_set)
    if not recipients:
        log.info("No new recipients to send. All already processed.")
        raise SystemExit(0)

    log.info("Remaining recipients: %d", len(recipients))
    send_all_batches(recipients)


if __name__ == "__main__":
    main()
