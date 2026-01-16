# Copyright (C) 2025 https://github.com/FranBarInstance/neutral-starter-py (See LICENCE)

"""template and response"""

import json
import re

from flask import Response, current_app, make_response

from app.config import Config

if Config.NEUTRAL_IPC:
    from neutral_ipc_template import NeutralIpcTemplate as NeutralTemplate
else:
    from neutraltemplate import NeutralTemplate


class Template:
    """Neutral Template"""

    def __init__(self, schema):
        """init"""
        self.schema = schema
        self.data = self.schema.properties["data"]
        self.response = make_response()
        self.response.headers["Content-Type"] = "text/html"
        self.contents = None
        self._cookies = {}

        if current_app.debug:
            self.data["current_app_debug"] = "true"

    def render(self, tpl=None, headers=None) -> Response:
        """render template and return response"""
        tpl = tpl or self.data['TEMPLATE_LAYOUT']

        template = NeutralTemplate(tpl, json.dumps(self.schema.properties))
        self.contents = template.render()

        self.contents = self.contents.lstrip('\n\r\t ')
        if Config.TEMPLATE_HTML_MINIFY:
            self.contents = re.sub(
                r"^\s+<(?!pre\b|code\b|samp\b|kbd\b|var\b|textarea\b|xmp\b|script\b|style\b|template\b)([^>]+>)",
                r"<\1",
                self.contents,
                flags=re.MULTILINE
            )

        status_code = int(template.get_status_code())
        status_text = template.get_status_text()
        status_param = template.get_status_param()
        if template.has_error() and current_app.debug:
            print("There are parse errors in the templates, check logs")

        # The template may generate redirects.
        if status_code in [301, 302, 307, 308]:
            self._set_cookies()
            self.response.headers["Location"] = status_param
            self.response.status_code = status_code
            return self.response

        # The template may generate HTTP errors.
        if status_code >= 400:
            return self.render_error(status_code, status_text, status_param)

        if headers:
            for key, value in headers.items():
                self.response.headers[key] = value

        self.response.status_code = status_code
        self.response.set_data(self.contents)
        self._set_cookies()
        return self.response

    def render_error(
        self, status_code=404, status_text="Not Found", status_param=""
    ) -> Response:
        """render template ERROR and return response"""
        self.data["CURRENT_COMP_ROUTE"] = "HTTP_ERROR"
        self.data["HTTP_ERROR"] = {
            "code": status_code,
            "text": status_text,
            "param": status_param,
        }

        template = NeutralTemplate(
            self.data['TEMPLATE_ERROR'], json.dumps(self.schema.properties)
        )
        self.contents = template.render()

        self.contents = self.contents.lstrip('\n\r\t ')
        if Config.TEMPLATE_HTML_MINIFY:
            self.contents = re.sub(
                r"^\s+<(?!pre\b|code\b|samp\b|kbd\b|var\b|textarea\b|xmp\b|script\b|style\b|template\b)([^>]+>)",
                r"<\1",
                self.contents,
                flags=re.MULTILINE
            )

        self.response.status_code = status_code
        self.response.set_data(self.contents)
        self._set_cookies()

        return self.response

    def _set_cookies(self) -> None:
        """set cookies"""
        if self._cookies is not None:
            for _, cookie_params in self._cookies.items():
                self.response.set_cookie(**cookie_params)

    def add_cookie(self, cookie) -> None:
        """add cookie"""
        if cookie:
            self._cookies.update(cookie)
