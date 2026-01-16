# Copyright (C) 2025 https://github.com/FranBarInstance/neutral-starter-py (See LICENCE)

import json

from flask import request


def get_ip():
    """Get the IP address of the client, cloudflare ip or remote addr."""
    return request.headers.get("CF-Connecting-IP", request.remote_addr)


def format_ua(ua):
    """Format user agent information into a readable string."""
    return f"{ua['name']} - {ua['os']} - {ua['category']}"


def merge_dict(a, b):
    """Merge dictionary b recursively into dictionary a.

    Args:
        a: Target dictionary to merge into (modified in place)
        b: Source dictionary (or JSON string) to merge from

    Note:
        Modifies dictionary 'a' directly. For JSON strings in 'b',
        they are automatically parsed before merging.
    """
    if isinstance(b, str):
        b = json.loads(b)

    def recursive_merge(target, source):
        for key, value in source.items():
            if (
                key in target
                and isinstance(target[key], dict)
                and isinstance(value, dict)
            ):
                recursive_merge(target[key], value)
            else:
                target[key] = value
        return target

    recursive_merge(a, b)


def parse_vars(template, data):
    """Parse variables in template with [:; ... :] delimiters and "->" for nested keys."""

    if not isinstance(data, dict):
        raise TypeError(f"Expected dict for data, got {type(data).__name__}")

    result = []
    i = 0

    while i < len(template):
        start = template.find("[:;", i)

        if start == -1:
            result.append(template[i:])
            break

        result.append(template[i:start])

        end = template.find(":]", start + 3)

        if end == -1:
            raise ValueError(f"Unclosed delimiter at position {start}")

        path = template[start + 3 : end]

        if "->" in path:
            keys = [k.strip() for k in path.split("->")]
        else:
            keys = [path.strip()]

        if any(not key for key in keys):
            raise ValueError(f"Empty key in path: '{path}'")

        value = data
        for idx, key in enumerate(keys):
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                traversed = "->".join(keys[:idx]) if idx > 0 else "root"
                raise KeyError(
                    f"Key '{key}' not found at '{traversed}'. "
                    f"Available keys: {list(value.keys()) if isinstance(value, dict) else 'N/A'}. "
                    f"Full path: '{path}'"
                )

        if isinstance(value, (str, int, float, bool, type(None))):
            result.append(str(value) if value is not None else "")
        else:
            raise TypeError(
                f"Value at path '{path}' has unsupported type "
                f"{type(value).__name__}. Expected str, int, float, bool, or None."
            )

        i = end + 2

    return "".join(result)
