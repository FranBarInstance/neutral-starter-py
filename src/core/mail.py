# Copyright (C) 2025 https://github.com/FranBarInstance/neutral-starter-py (See LICENCE)

"""Mail Class"""

import json
import math
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from subprocess import Popen, PIPE
from app.config import Config

if Config.NEUTRAL_IPC:
    from neutral_ipc_template import NeutralIpcTemplate as NeutralTemplate
else:
    from neutraltemplate import NeutralTemplate


class Mail():
    """
    Mail class for sending emails.
    """

    DEFAULT_SCHEMA = {
        "config": {
            "comments": "remove",
            "cache_prefix": "neutral-cache-mail",
            "cache_dir": "",
            "cache_on_post": False,
            "cache_on_get": False,
            "cache_on_cookies": False,
            "cache_disable": True,  # In the case of email, caching could be problematic.
            "filter_all": False,
            "disable_js": True
        },
        "inherit": {
            "locale": {
                "current": "en"
            },
        },
        "data": {
            "mail_data": {},
            "HTTP_ERROR": {},
            "dispatch_result": False
        }
    }

    def __init__(self, schema: dict) -> None:
        """Initialize the Mail class."""
        self.schema = schema
        self.template_layout = Config.TEMPLATE_MAIL + '/index.ntpl'
        self.site = self.schema['data']['site']
        self.auth_link = self.site['url'] + self.site['sign_links']['pin']
        self.login_link = self.site['url'] + self.site['sign_links']['in']
        self.reminder_link = self.site['url'] + self.site['sign_links']['reminder']
        self.defaults = {
            "template": 'sample',
            "url_home": self.site['url'],
            "logo": self.site['url'] + '/' + self.site['logo'],
            "cover": self.site['url'] + '/' + self.site['cover'],
            "brand_text": self.site['name'],
            "cover_text": self.site['name'],
            "login_link": self.login_link,
            "reminder_link": self.reminder_link,
            "auth_link": self.auth_link,
            "auth_pin": '',
            "user_alias": '',
            "expires": math.floor(int(Config.PIN_EXPIRES_SECONDS) / 60 / 60),
        }
        self.default_schema = self.DEFAULT_SCHEMA
        self.default_schema['inherit']['locale']['current'] = self.schema['inherit']['locale']['current']

    def send(self, template: str, user_data: dict) -> None:
        """Send an email."""
        self.default_schema['inherit']['locale']['current'] = user_data.get('locale', 'en')
        self.default_schema['data']['mail_data'] = {**self.defaults, **self.schema['data']['mail_data']}
        self.default_schema['data']['mail_data']["template"] = template
        self.default_schema['data']['mail_data']["auth_link"] = self.auth_link + '/' + user_data.get('token', '')
        self.default_schema['data']['mail_data']["auth_pin"] = user_data.get('pin', '')
        self.default_schema['data']['mail_data']["user_alias"] = user_data.get('alias', '')

        template = NeutralTemplate(self.template_layout, json.dumps(self.default_schema))
        body = template.render()

        if Config.MAIL_METHOD == 'sendmail':
            self.send_via_sendmail(body, user_data)
        elif Config.MAIL_METHOD == 'smtp':
            self.send_via_smtp(body, user_data)
        elif Config.MAIL_METHOD == 'file':
            with open(Config.MAIL_TO_FILE, "w", encoding="utf-8") as file:
                file.write(body)
        else:
            print("Invalid sending method")

    def send_via_sendmail(self, body: str, user_data: dict) -> None:
        """Send email using sendmail/postfix."""
        sender = user_data.get('from') or Config.MAIL_SENDER
        return_path = Config.MAIL_RETURN_PATH

        # Create email message
        message = MIMEMultipart()
        message['From'] = sender
        message['To'] = user_data['to']
        message['Subject'] = user_data['subject']
        message.attach(MIMEText(body, 'html'))

        # Send using sendmail
        p = Popen(['/usr/sbin/sendmail', '-t', '-oi', '-f', return_path], stdin=PIPE)
        p.communicate(message.as_string().encode('utf-8'))

    def send_via_smtp(self, body: str, user_data: dict) -> None:
        """Send email using SMTP."""
        sender = user_data.get('from') or Config.MAIL_SENDER

        # Create email message
        message = MIMEMultipart()
        message['From'] = sender
        message['To'] = user_data['to']
        message['Subject'] = user_data['subject']
        message.attach(MIMEText(body, 'html'))

        # Connect to SMTP server and send
        with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
            if Config.MAIL_USE_TLS:
                server.starttls()
            if Config.MAIL_USERNAME and Config.MAIL_PASSWORD:
                server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            server.sendmail(sender, user_data['to'], message.as_string())
