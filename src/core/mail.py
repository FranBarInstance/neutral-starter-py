"""Mail Class"""

import re
import smtplib
from subprocess import Popen, PIPE
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from app.config import Config

if Config.NEUTRAL_IPC:
    from neutral_ipc_template import NeutralIpcTemplate as NeutralTemplate # pylint: disable=no-name-in-module,import-error
else:
    from neutraltemplate import NeutralTemplate # pylint: disable=no-name-in-module,import-error


class MailTemplate: # pylint: disable=too-few-public-methods
    """Email template rendering via NeutralTemplate."""

    def __init__(self, schema: dict) -> None:
        self.schema = schema

    def render(self, tpl: str) -> str:
        """Renders the NTPL layout with the prepared schema."""
        template = NeutralTemplate(tpl, schema_obj=self.schema)
        return template.render()


class MailSend: # pylint: disable=too-few-public-methods
    """Email transport."""

    def __init__(self) -> None:
        self.method = Config.MAIL_METHOD  # 'smtp', 'sendmail', 'file'

    def send(self, mail_data: dict, html_body: str, text_body: str = None) -> dict:
        """Sends email and returns a result dict.

        Args:
            mail_data: Dict with 'to', 'subject', and optional 'from'.
                       Sender: mail_data.get('from') or Config.MAIL_SENDER
        """
        try:
            to = mail_data['to']
            subject = mail_data['subject']
            sender = mail_data.get('from') or Config.MAIL_SENDER

            msg = self._build_mime(to, subject, sender, html_body, text_body)
            if self.method == 'smtp':
                return self._send_smtp(msg, to, sender)
            if self.method == 'sendmail':
                return self._send_sendmail(msg)
            if self.method == 'file':
                return self._send_file(msg, html_body)
            return {'success': False, 'error': f"Unknown method: {self.method}"}
        except Exception as e: # pylint: disable=broad-exception-caught
            return {'success': False, 'error': str(e)}

    def _build_mime( # pylint: disable=too-many-arguments,too-many-positional-arguments
        self, to: str, subject: str, sender: str, html: str, text: str
    ) -> MIMEMultipart:
        """Builds a multipart MIME message."""
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = to
        msg['X-Mailer'] = 'NeutralMail/2.0'
        if text:
            msg.attach(MIMEText(text, 'plain', 'utf-8'))
        msg.attach(MIMEText(html, 'html', 'utf-8'))
        return msg

    def _send_smtp(self, msg: MIMEMultipart, to: str, sender: str) -> dict:
        """Sends via SMTP with optional TLS."""
        with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
            if Config.MAIL_USE_TLS:
                server.starttls()
            if Config.MAIL_USERNAME and Config.MAIL_PASSWORD:
                server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            server.sendmail(sender, to, msg.as_string())
        return {'success': True, 'message_id': None, 'error': None}

    def _send_sendmail(self, msg: MIMEMultipart) -> dict:
        """Sends via local sendmail."""
        with Popen(['/usr/sbin/sendmail', '-t', '-oi', '-f', Config.MAIL_RETURN_PATH], stdin=PIPE) as p:
            p.communicate(msg.as_string().encode('utf-8'))
        return {'success': True, 'message_id': None, 'error': None}

    def _send_file(self, msg: MIMEMultipart, html_body: str) -> dict:
        """Saves to file for testing."""
        with open(Config.MAIL_TO_FILE, "w", encoding="utf-8") as f:
            f.write(f"<!-- To: {msg['To']} -->\n")
            f.write(f"<!-- Subject: {msg['Subject']} -->\n")
            f.write(html_body)
        return {'success': True, 'message_id': Config.MAIL_TO_FILE, 'error': None}


class Mail: # pylint: disable=too-few-public-methods
    """Email delivery orchestrator.

    Pattern identical to Template: __init__(schema, tpl=None).
    The consumer does not know file paths.
    """

    def __init__(self, schema: dict, tpl: str = None) -> None:
        self.schema = schema
        self.data = schema.get("data", {})
        self.tpl = tpl or self.data.get('MAIL_TEMPLATE_LAYOUT')

        if not self.tpl:
            raise ValueError(
                "MAIL_TEMPLATE_LAYOUT is not defined in the schema. "
                "Make sure a mail template provider component is "
                "active and has called set_current_mail_template()."
            )

    def send(
        self,
        content_template: str,
        mail_data: dict,
        layout_data: dict = None
    ) -> dict:
        """Sends an email rendering content_template inside the layout.

        Args:
            content_template: Content template identifier.
            mail_data: Dict with mandatory 'to', 'subject';
                       'from' optional (default: Config.MAIL_SENDER);
                       plus template variables (token, code, etc.).
            layout_data: Optional presentation data. The template
                        component decides if they are needed.
        """
        try:
            # 1. Prepare current_mail in schema
            self._prepare_mail_data(content_template, mail_data, layout_data)

            # 2. Render HTML
            html_body = MailTemplate(self.schema).render(self.tpl)
            text_body = self._html_to_text(html_body)

            # 3. Send
            result = MailSend().send(
                mail_data=mail_data,
                html_body=html_body,
                text_body=text_body
            )
            return result
        except Exception as e: # pylint: disable=broad-exception-caught
            return {'success': False, 'error': str(e)}

    def _prepare_mail_data(
        self,
        content_template: str,
        mail_data: dict,
        layout_data: dict = None
    ) -> None:
        """Sets current_mail in the schema for the NTPL layout to use."""
        self.data['current_mail'] = {
            'content_template': content_template,
            **(layout_data or {}),
            **mail_data
        }

        # Ensure the email context does not inject JS or try to cache
        self.schema.setdefault('config', {})
        self.schema['config']['cache_disable'] = True
        self.schema['config']['disable_js'] = True

    def _html_to_text(self, html: str) -> str:
        """Basic HTML to plain text conversion."""
        text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
