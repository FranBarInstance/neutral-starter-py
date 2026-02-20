"""Network utility functions."""

import fnmatch


def normalize_host(host):
    """Normalize host value for allow-list checks (strip port and trailing dot)."""
    if not host:
        return ""

    value = host.strip().lower().rstrip('.')

    # IPv6 in URL host format: [::1]:5000
    if value.startswith('['):
        end = value.find(']')
        if end != -1:
            return value[1:end]

    if ':' in value:
        return value.rsplit(':', 1)[0]

    return value


def is_allowed_host(host, allowed_hosts):
    """Check host against allowed_hosts list supporting wildcard patterns."""
    for pattern in allowed_hosts:
        normalized_pattern = (pattern or '').strip().lower().rstrip('.')
        if not normalized_pattern:
            continue
        if normalized_pattern == "*" or fnmatch.fnmatch(host, normalized_pattern):
            return True
    return False
