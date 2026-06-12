import smtplib
from email.message import EmailMessage

EMAIL_SUBJECT = "Webull platform impersonation — your name appeared"
EMAIL_BODY = """Hello,

If this reached you in error, we apologize.

You are receiving this because your name appeared in connection with Webull platform impersonation matters currently under legal review.

Our firm, The Crypto Lawyers PLLC, represents clients in matters involving unauthorized use of the Webull brand and platform. We are not affiliated with Webull.

We investigate institutional liability for platform impersonation schemes. We do not charge fees to evaluate initial submissions, and we do not request sensitive credentials, seed phrases, or private keys. You can read about our work here: https://www.newswire.com/news/the-crypto-lawyers-pllc-seeks-recovery-of-stolen-funds-for-more-than-22641283

We have received submissions from victims across multiple states.

If you believe you were affected by impersonation involving Webull's platform, you may submit your information for review at https://crypto-lawyers.github.io/crypto-lawyers-intake/

Our team reviews submissions as they are received. We contact you only if your evidence qualifies for reparation. There is no obligation to proceed. Submitting does not create an attorney-client relationship. If anyone claiming to represent us requests payment or keys, please report it immediately by replying directly to this email.

However you decide, please know this: You were not foolish. You were targeted. And you are not alone.

Sincerely,

Forensic Litigation Division
The Crypto Lawyers, PLLC
Florida Bar No. #1002677
848 Brickell Avenue, Penthouse 5, Miami, Florida 33131
1005 Congress Avenue, Suite 925, Austin, Texas 78701"""

msg = EmailMessage()
msg["From"] = "thecryptolawyers.cases@gmail.com"
msg["To"] = "TheCryptoLawyers.Intake@proton.me"
msg["Subject"] = EMAIL_SUBJECT
msg["Reply-To"] = "thecryptolawyers.cases@gmail.com"
msg.set_content(EMAIL_BODY)

with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
    server.login("thecryptolawyers.cases@gmail.com", "yacpazewbbpiupww")
    server.send_message(msg)
    print("SENT OK")
