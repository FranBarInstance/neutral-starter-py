# Copyright (C) 2025 https://github.com/FranBarInstance/neutral-starter-py (See LICENCE)

"""Form request handler base that consumes PreparedRequest (`g.pr`).

This module provides FormRequestHandler for handling form validation and processing.
It extends RequestHandler with form-specific functionality.

WARNING: This module is INTERNAL to the core framework.
Component developers should extend FormRequestHandler for custom form handling.
"""

import time
import os
from datetime import datetime
from typing import TYPE_CHECKING
import fnmatch
import regex
import dns.resolver
from app.config import Config
from utils.tokens import ltoken_check
from .request_handler import RequestHandler

if TYPE_CHECKING:
    from .prepared_request import PreparedRequest


class FormRequestHandler(RequestHandler):
    """Base form request handler class handling form validation and processing.

    Extends RequestHandler with form-specific functionality:
    - Form token validation (link tokens and form tokens)
    - Field validation with multiple rule types
    - Error handling and reporting

    WARNING: INTERNAL USE ONLY.

    This class is part of the framework's internal request processing
    infrastructure. Component developers may extend this class for
    custom form handling, but should not import PreparedRequest directly.

    Example usage in component:
        from core.request_handler_form import FormRequestHandler
        from flask import g

        @bp.route("/form")
        def form_handler(route):
            handler = FormRequestHandler(g.pr, route, bp.neutral_route, ltoken, "my_form")
            if handler.req.method == "POST":
                if handler.form_post():
                    return handler.render_route()
            return handler.render_route()
    """

    def __init__(
        self,
        prepared_request: "PreparedRequest",
        comp_route: str = "",
        neutral_route: str | None = None,
        ltoken: str | None = None,
        form_name: str = "_unused_form"
    ):
        """Initialize form request handler with request context and validation rules.

        Args:
            prepared_request: The PreparedRequest built in before_request
            comp_route: Component-relative route path
            neutral_route: Neutral template route path
            ltoken: Link token for form validation
            form_name: Name of the form being processed
        """
        super().__init__(prepared_request, comp_route, neutral_route)
        self._ltoken = ltoken
        self._form_name = form_name

        # Initialize form error structure
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

        # Get form configuration from schema
        self.field_rules = self.schema_data['current_forms'][self._form_name]['rules']
        self.form_validation = self.schema_data['current_forms'][self._form_name]['validation']
        self.form_check_fields = self.schema_data['current_forms'][self._form_name]['check_fields']

    def form_get(self) -> bool:
        """Validate GET request for authentication forms."""
        return self.validate_get()

    def form_post(self) -> bool:
        """Validate POST request for authentication forms."""
        return self.validate_post()

    def validate_get(self) -> bool:
        """Validate GET request parameters and session state."""
        if not self.valid_form_tokens_get():
            return False
        return True

    def validate_post(self, error_prefix: str = "ref:form_error") -> bool:
        """Validate POST request for authentication forms.

        Args:
            error_prefix: Prefix for error message keys

        Returns:
            bool: True if validation passes, False otherwise
        """
        if not self.valid_form_tokens_post():
            return False

        if not self.valid_form_validation():
            return False

        if self.any_error_form_fields(error_prefix):
            return False

        return True

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

        for field_name, files in self.schema_data['CONTEXT'].get('FILES', {}).items():
            if self._count_submitted_files(files) > 0 and not self._is_file_allowed(field_name):
                self.error['form']['validation'] = "true"
                return False

        return True

    def any_error_form_fields(self, error_prefix: str) -> bool:
        """Check form fields for validation errors."""
        any_error = False
        for field_name in self.form_check_fields:
            any_error = self.get_error_field(field_name, error_prefix) or any_error
        return any_error

    def _is_field_allowed(self, field: str) -> bool:
        """Check if a field name is allowed based on patterns."""
        return any(fnmatch.fnmatch(field, pattern) for pattern in self.form_validation['allow_fields'])

    def _is_file_allowed(self, field: str) -> bool:
        """Check if a file field name is allowed based on patterns."""
        patterns = self.form_validation.get('allow_files', self.form_validation.get('allow_fields', []))
        return any(fnmatch.fnmatch(field, pattern) for pattern in patterns)

    def get_error_field(self, field_name: str, error_prefix: str) -> bool:
        """Check if a field has errors based on validation rules."""
        field_value = self.schema_data['CONTEXT']['POST'].get(field_name) or None
        file_values = self.schema_data['CONTEXT'].get('FILES', {}).get(field_name, [])
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
        file_validation_rules = {
            "required_file": self._get_error_field_required_file,
            "minfiles": self._get_error_field_minfiles,
            "maxfiles": self._get_error_field_maxfiles,
            "multiple": self._get_error_field_multiple,
            "max_file_size": self._get_error_field_max_file_size,
            "max_total_file_size": self._get_error_field_max_total_file_size,
            "allowed_mime": self._get_error_field_allowed_mime,
            "allowed_extensions": self._get_error_field_allowed_extensions,
        }

        if field_name not in self.field_rules:
            self.error['field'][field_name] = f"No rules for field '{field_name}'. Contact admin."
            return True

        has_uploaded_files = self._count_submitted_files(file_values) > 0

        for rule_name, rule_value in self.field_rules[field_name].items():
            if rule_name in validation_rules:
                required = self.field_rules[field_name].get("required") or False
                (error, error_suffix) = validation_rules[rule_name](field_value, rule_value, required)
                if error:
                    self.error['field'][field_name] = f"{error_prefix}_{rule_name}{error_suffix}"
                    return True
            elif rule_name in file_validation_rules:
                (error, error_suffix) = file_validation_rules[rule_name](file_values, rule_value)
                if error:
                    self.error['field'][field_name] = f"{error_prefix}_{rule_name}{error_suffix}"
                    return True

        if has_uploaded_files:
            default_file_rules = {
                "allowed_mime": Config.IMAGE_ALLOWED_MIME,
                "max_file_size": Config.IMAGE_MAX_FILE_BYTES,
                "max_total_file_size": Config.IMAGE_MAX_UPLOAD_BYTES,
            }
            for rule_name, rule_value in default_file_rules.items():
                if rule_name in self.field_rules[field_name]:
                    continue
                (error, error_suffix) = file_validation_rules[rule_name](file_values, rule_value)
                if error:
                    self.error['field'][field_name] = f"{error_prefix}_{rule_name}{error_suffix}"
                    return True

        return False

    def _count_submitted_files(self, files) -> int:
        """Count uploaded files with a non-empty filename."""
        return len(self._get_submitted_files(files))

    def _get_submitted_files(self, files) -> list:
        """Return only file entries that were actually submitted."""
        submitted_files = []
        for file_item in files or []:
            filename = getattr(file_item, "filename", "") or ""
            if filename:
                submitted_files.append(file_item)
        return submitted_files

    def _get_file_size(self, file_item) -> int:
        """Calculate file size without consuming the uploaded stream."""
        stream = getattr(file_item, "stream", None)
        if stream is None:
            return 0

        current_pos = stream.tell()
        stream.seek(0, os.SEEK_END)
        size = stream.tell()
        stream.seek(current_pos)
        return size

    def _normalize_rule_values(self, rule_value) -> set[str]:
        """Normalize comma-separated or iterable rule values."""
        if isinstance(rule_value, str):
            return {
                item.strip().lower()
                for item in rule_value.split(",")
                if item.strip()
            }
        if isinstance(rule_value, (list, tuple, set)):
            return {
                str(item).strip().lower()
                for item in rule_value
                if str(item).strip()
            }
        return set()

    def _get_error_field_set(self, field_value, require_set, _) -> tuple[bool, str]:
        """Check 'set' rule - field must/must not be present."""
        if field_value is None and require_set:
            return True, "_true"
        if field_value is not None and not require_set:
            return True, "_false"
        return False, ""

    def _get_error_field_required(self, field_value, required, _) -> tuple[bool, str]:
        """Check 'required' rule - field must have a value."""
        if field_value is None:
            if required:
                return True, "_true"
            return False, ""
        return False, ""

    def _get_error_field_minlength(self, field_value, minlength, required) -> tuple[bool, str]:
        """Check 'minlength' rule - minimum string length."""
        if field_value is None:
            if required:
                return True, "_true"
            return False, ""

        if len(str(field_value)) < int(minlength):
            return True, ""
        return False, ""

    def _get_error_field_maxlength(self, field_value, maxlength, required) -> tuple[bool, str]:
        """Check 'maxlength' rule - maximum string length."""
        if field_value is None:
            if required:
                return True, "_true"
            return False, ""

        if len(str(field_value)) > int(maxlength):
            return True, ""
        return False, ""

    def _get_error_field_pattern(self, field_value, pattern, required) -> tuple[bool, str]:
        """Check 'regex' rule - must match regex pattern."""
        if field_value is None:
            if required:
                return True, "_true"
            return False, ""

        if not regex.fullmatch(pattern, field_value):
            return True, ""
        return False, ""

    def _get_error_field_value(self, field_value, value, required) -> tuple[bool, str]:
        """Check 'value' rule - must equal specific value."""
        if field_value is None:
            if required:
                return True, "_true"
            return False, ""

        if field_value != value:
            return True, ""
        return False, ""

    def _get_error_field_required_file(self, file_values, required) -> tuple[bool, str]:
        """Check 'required_file' rule - at least one file must be present."""
        if required and self._count_submitted_files(file_values) == 0:
            return True, "_true"
        return False, ""

    def _get_error_field_minfiles(self, file_values, minfiles) -> tuple[bool, str]:
        """Check 'minfiles' rule - minimum uploaded file count."""
        if self._count_submitted_files(file_values) < int(minfiles):
            return True, ""
        return False, ""

    def _get_error_field_maxfiles(self, file_values, maxfiles) -> tuple[bool, str]:
        """Check 'maxfiles' rule - maximum uploaded file count."""
        if self._count_submitted_files(file_values) > int(maxfiles):
            return True, ""
        return False, ""

    def _get_error_field_multiple(self, file_values, multiple) -> tuple[bool, str]:
        """Check 'multiple' rule - whether more than one uploaded file is allowed."""
        if not multiple and self._count_submitted_files(file_values) > 1:
            return True, "_false"
        return False, ""

    def _get_error_field_max_file_size(self, file_values, max_file_size) -> tuple[bool, str]:
        """Check 'max_file_size' rule - each uploaded file must fit the limit."""
        max_size = min(int(max_file_size), int(Config.IMAGE_MAX_FILE_BYTES))
        for file_item in self._get_submitted_files(file_values):
            if self._get_file_size(file_item) > max_size:
                return True, ""
        return False, ""

    def _get_error_field_max_total_file_size(self, file_values, max_total_file_size) -> tuple[bool, str]:
        """Check 'max_total_file_size' rule - combined uploaded size must fit the limit."""
        max_total_size = min(int(max_total_file_size), int(Config.IMAGE_MAX_UPLOAD_BYTES))
        total_size = sum(self._get_file_size(file_item) for file_item in self._get_submitted_files(file_values))
        if total_size > max_total_size:
            return True, ""
        return False, ""

    def _get_error_field_allowed_mime(self, file_values, allowed_mime) -> tuple[bool, str]:
        """Check 'allowed_mime' rule - uploaded MIME type must be allow-listed."""
        config_allowed_values = self._normalize_rule_values(Config.IMAGE_ALLOWED_MIME)
        allowed_values = self._normalize_rule_values(allowed_mime)
        if allowed_values:
            allowed_values = allowed_values.intersection(config_allowed_values)
        else:
            allowed_values = config_allowed_values
        for file_item in self._get_submitted_files(file_values):
            mimetype = (getattr(file_item, "mimetype", "") or "").strip().lower()
            if mimetype not in allowed_values:
                return True, ""
        return False, ""

    def _get_error_field_allowed_extensions(self, file_values, allowed_extensions) -> tuple[bool, str]:
        """Check 'allowed_extensions' rule - uploaded filename extension must be allow-listed."""
        allowed_values = self._normalize_rule_values(allowed_extensions)
        normalized_extensions = {
            item if item.startswith(".") else f".{item}"
            for item in allowed_values
        }
        for file_item in self._get_submitted_files(file_values):
            filename = (getattr(file_item, "filename", "") or "").strip().lower()
            _, extension = os.path.splitext(filename)
            if extension not in normalized_extensions:
                return True, ""
        return False, ""

    def _get_error_field_match(self, field_value, field_to_match, required) -> tuple[bool, str]:
        """Check 'match' rule - must match another field's value."""
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
        """Check 'dns' rule - DNS record must exist for domain."""
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
        """Check 'maxage' rule - date must not be older than maxage years."""
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
        """Check 'minage' rule - date must be older than minage years."""
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
