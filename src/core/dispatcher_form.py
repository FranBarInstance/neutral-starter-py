# Copyright (C) 2025 https://github.com/FranBarInstance/neutral-starter-py (See LICENCE)

"""Dispatcher forms"""


import time
from datetime import datetime
import fnmatch
import regex
import dns.resolver
from constants import * # pylint: disable=wildcard-import,unused-wildcard-import
from utils.tokens import ltoken_check
from .dispatcher import Dispatcher

class DispatcherForm(Dispatcher):
    """Base form dispatcher class handling form validation and processing.

    Provides core functionality for:
    - Form token validation (link tokens and form tokens)
    - Field validation with multiple rule types
    - Error handling and reporting
    """

    def __init__(self, req, comp_route, neutral_route=None, ltoken=None, form_name="form"):
        """Initialize form dispatcher with request context and validation rules."""
        super().__init__(req, comp_route, neutral_route, ltoken)
        self._form_name = form_name
        self.schema_data[form_name] = {
            "error": {
                "form": {
                    "ltoken": None,
                    "validation": None,
                    "already_session": None
                },
                "field": {}
            },
            "is_submit": {}
        }
        self.error = self.schema_data[self._form_name]['error']
        self.form_submit = self.schema_data[self._form_name]['is_submit']
        self.field_rules = self.schema_data['core']['forms'][self._form_name]['rules']
        self.form_validation = self.schema_data['core']['forms'][self._form_name]['validation']
        self.form_check_fields = self.schema_data['core']['forms'][self._form_name]['check_fields']

    def valid_form_tokens_get(self) -> bool:
        """Validate form tokens for GET requests."""
        # Check that the link to the form has a correct token.
        if not ltoken_check(self._ltoken, self.schema_data['CONTEXT']['UTOKEN']):
            self.error['form']['ltoken'] = "true"
            return False

        return True

    def valid_form_tokens_post(self) -> bool:
        """Validate form tokens for POST requests."""
        # Check that the link to the form has a correct token.
        if not ltoken_check(self._ltoken, self.schema_data['CONTEXT']['UTOKEN']):
            self.error['form']['ltoken'] = "true"
            return False

        return True

    def valid_form_validation(self) -> bool:
        """Validate form-level constraints."""
        if "minfields" in self.form_validation:
            if len(self.schema_data['CONTEXT']['POST']) < int(self.form_validation['minfields']):
                self.error['form']['validation'] = "true"
                return False

        if "maxfields" in self.form_validation:
            if len(self.schema_data['CONTEXT']['POST']) > int(self.form_validation['maxfields']):
                self.error['form']['validation'] = "true"
                return False

        for field_name, _ in self.schema_data['CONTEXT']['POST'].items():
            if not self._is_field_allowed(field_name):
                self.error['form']['validation'] = "true"
                return False

        return True

    def any_error_form_fields(self, error_prefix):
        """Check form fields for validation errors."""
        any_error = False
        for field_name in self.form_check_fields:
            any_error = self.get_error_field(field_name, error_prefix) or any_error
        return any_error

    def _is_field_allowed(self, field):
        return any(fnmatch.fnmatch(field, pattern) for pattern in self.form_validation['allow_fields'])

    def get_error_field(self, field_name: str, error_prefix: str) -> bool:
        """Check if a field has errors based on validation rules."""
        field_value = self.schema_data['CONTEXT']['POST'].get(field_name) or None
        validation_rules = {
            "set": self._get_error_field_set,
            "required": self._get_error_field_required,
            "minage": self._get_error_field_minage,
            "maxage": self._get_error_field_maxage,
            "minlength": self._get_error_field_minlength,
            "maxlength": self._get_error_field_maxlength,
            "regex": self._get_error_field_pattern,
            "value": self._get_error_field_value,
            "match": self._get_error_field_match,
            "dns": self._get_error_field_dns
        }

        if field_name not in self.field_rules:
            self.error['field'][field_name] = f"No rules for field '{field_name}'. Contact admin."
            return True

        for rule_name, rule_value in self.field_rules[field_name].items():
            if rule_name in validation_rules:
                required = self.field_rules[field_name].get("required") or False
                (error, error_suffix) = validation_rules[rule_name](field_value, rule_value, required)
                if error:
                    self.error['field'][field_name] = f"{error_prefix}_{rule_name}{error_suffix}"
                    return True

        return False

    def _get_error_field_set(self, field_value, require_set, _) -> tuple[bool, str]:
        if field_value is None and require_set:
            return True, "_true"
        if field_value is not None and not require_set:
            return True, "_false"
        return False, ""

    def _get_error_field_required(self, field_value, required, _) -> tuple[bool, str]:
        if field_value is None:
            if required:
                return True, "_true"
            return False, ""
        return False, ""

    def _get_error_field_minlength(self, field_value, minlength, required) -> tuple[bool, str]:
        if field_value is None:
            if required:
                return True, "_true"
            return False, ""

        if len(str(field_value)) < int(minlength):
            return True, ""
        return False, ""

    def _get_error_field_maxlength(self, field_value, maxlength, required) -> tuple[bool, str]:
        if field_value is None:
            if required:
                return True, "_true"
            return False, ""

        if len(str(field_value)) > int(maxlength):
            return True, ""
        return False, ""

    def _get_error_field_pattern(self, field_value, pattern, required) -> tuple[bool, str]:
        if field_value is None:
            if required:
                return True, "_true"
            return False, ""

        if not regex.fullmatch(pattern, field_value):
            return True, ""
        return False, ""

    def _get_error_field_value(self, field_value, value, required) -> tuple[bool, str]:
        if field_value is None:
            if required:
                return True, "_true"
            return False, ""

        if field_value != value:
            return True, ""
        return False, ""

    def _get_error_field_match(self, field_value, field_to_match, required) -> tuple[bool, str]:
        if field_value is None:
            if required:
                return True, "_true"
            return False, ""

        if field_value is not None:
            post_data = self.schema_data['CONTEXT']['POST']

            if field_to_match not in post_data:
                return True, "_unset"

            if field_value != post_data[field_to_match]:
                return True, ""

        return False, ""

    def _get_error_field_dns(self, field_value, dns_type, required) -> tuple[bool, str]:
        if field_value is None:
            if required:
                return True, "_true"
            return False, ""

        try:
            domain = field_value.split('@')[-1]
            result = dns.resolver.resolve(domain, dns_type)
            return bool(not result), ""

        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.LifetimeTimeout):
            return True, ""

    def _get_error_field_maxage(self, field_value, maxage, required) -> tuple[bool, str]:
        if field_value is None:
            if required:
                return True, "_true"
            return False, ""

        try:
            now = int(time.time())
            age = datetime.strptime(field_value, "%Y-%m-%d")
            age = time.mktime(age.timetuple())
            limit = now - (int(maxage) * 365.25 * 24 * 60 * 60)

            if age < limit:
                return True, ""
            return False, ""

        except ValueError:
            return True, ""

    def _get_error_field_minage(self, field_value, minage, required) -> tuple[bool, str]:
        if field_value is None:
            if required:
                return True, "_true"
            return False, ""

        try:
            now = int(time.time())
            age = datetime.strptime(field_value, "%Y-%m-%d")
            age = time.mktime(age.timetuple())
            limit = now - (int(minage) * 365.25 * 24 * 60 * 60)

            if age > limit:
                return True, ""
            return False, ""

        except ValueError:
            return True, ""
