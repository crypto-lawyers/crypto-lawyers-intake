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
EMAIL_SUBJECT = "Notice regarding Webull platform impersonation"
EMAIL_BODY = """Hello,

If this reached you in error, we apologize.

You are receiving this because your name appeared in connection with 
Webull platform impersonation matters currently under legal review.

Our firm, The Crypto Lawyers PLLC, represents clients in matters 
involving unauthorized use of the Webull brand and platform. We are not 
affiliated with Webull.

What we do:
- We represent clients in federal forfeiture proceedings and related matters
- We investigate institutional liability for platform impersonation schemes
- We do not charge fees to evaluate initial submissions
- We do not request sensitive credentials, seed phrases, or private keys
- Read about our work: https://www.newswire.com/news/the-crypto-lawyers-pllc-seeks-recovery-of-stolen-funds-for-more-than-22641283

We have received submissions from victims across multiple states.

If you believe you were affected by impersonation involving Webull's 
platform, you may submit your information for review:

→ https://crypto-lawyers.github.io/crypto-lawyers-intake/

Our team reviews submissions as they are received. We contact you only if 
your evidence qualifies for reparation. There is no obligation to proceed. 
Submitting does not create an attorney-client relationship. If anyone 
claiming to represent us requests payment or keys, please report it 
immediately by replying directly to this email.

However you decide, please know this: You were not foolish. You were 
targeted. And you are not alone.

Sincerely,

Forensic Litigation Division
The Crypto Lawyers, PLLC
Florida Bar No. #1002677
848 Brickell Avenue, Penthouse 5, Miami, Florida 33131
1005 Congress Avenue, Suite 925, Austin, Texas 78701

---
Prior results do not guarantee similar outcomes. Reply "OPT-OUT" to unsubscribe."""

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
