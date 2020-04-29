import argparse
import keyring
import os
import smtplib
import tempfile
import time
from keyring.backends import SecretService
from email.mime.application import MIMEApplication
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr
from email import encoders

# On headless installs like a raspberry pi you can't 
# use the default backend.
keyring.set_keyring(SecretService.Keyring())

recipients = {
    'Noel': 'nniles@oceanit.com'
    'Mike': 'mfoley@oceanit.com'
}

def send_text(email, username, password, smtp, gateways, subject, text, attachment):
    server = smtplib.SMTP(smtp)
    server.starttls()
    server.login(username, password)

    for recipient_name, recipient_email in recipients.items():
        msg            = MIMEMultipart()
        msg['TO']      = formataddr((recipient_name, recipient_email))
        msg['FROM']    = formataddr((username, email))
        msg['SUBJECT'] = subject
        body           = text
        msg.attach(MIMEText(body, 'plain'))

        attachment_name = f"{time.strftime('%Y%m%d-%H%M%S')}.log"
        record = MIMEText(attachment, 'plain')
        encoders.encode_base64(record)
        record['Content-Disposition'] = f'attachment; filename="{attachment_name}"'
        msg.attach(record)
        
        server.sendmail(email, recipient_email, msg.as_string())

    server.quit()

def cli():
    ap = argparse.ArgumentParser()
    ap.add_argument('--email', type=str, required=True,
        help='email address for from line')
    ap.add_argument('--username', type=str, required=True,
        help='username for auth with smtp server')
    ap.add_argument('--keyring_system', type=str,
        help='the system named you used when adding the password to keyring')
    ap.add_argument('--dotfile', type=str, 
        help='path to a fot file with a password')
    ap.add_argument('--smtp', default='smtp.gmail.com:587',
        help='host:port for smtp server')
    ap.add_argument('--sms_gateways', nargs="*", 
        help='phonenumber@sms.example.com')
    ap.add_argument('--service', type=str, required=True,
        help='name of the systemd service')

    return ap.parse_args()

def main():
    args = cli()

    if not args.keyring_system and not args.dotfile:
        print('You need to either install a keyring or use a password file.')
        return -1

    gateways = args.sms_gateways

    tmp = tempfile.NamedTemporaryFile(mode='w+t', encoding='utf-8')
    os.system(f'systemctl status --no-pager -l {args.service} > {tmp.name}')
    tmp.seek(0)
    status = str(tmp.read())

    tmp = tempfile.NamedTemporaryFile(mode='w+t', encoding='utf-8')
    os.system(f'systemctl status --no-pager -l -n 100 {args.service} > {tmp.name}')
    tmp.seek(0)
    recent = str(tmp.read())

    text       = f'An error occured with the {args.service} process. The logs are attached.'
    attachment = f'Current Status:\n{status}\n\nLast 100 records:\n{recent}\n\n'
    subject    = 'pilikia with ibeach service'
    
    if args.keyring_system:
        password = keyring.get_password(args.keyring_system, args.email)
    else:
        with open(args.dotfile, 'r') as f:
            line = f.readline()
            password = line.split('=')[1]
    send_text(args.email, args.username, password, args.smtp, gateways, subject, text, attachment)

if __name__ == main():
    main()