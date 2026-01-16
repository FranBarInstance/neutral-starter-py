"""RSS Neutral plugin for RRSS."""

from feed import get_rss


def main(params=None):
    """Main function."""

    rrss_url = params.get("rrss_url")
    rrss_name = params.get("rrss_name")
    rrss_valid_names = params.get("rrss_valid_names")

    return {
        "data": get_rss(rrss_url, rrss_name, rrss_valid_names)
    }
