"""Parse Feed."""

from urllib.error import HTTPError

import fastfeedparser


def get_rss(rss_url, rrss_name, rrss_valid_names) -> dict:
    """Get RSS."""
    schema_data = {'rrss_feed_error': ''}

    if not rss_url:
        schema_data['rrss_feed_error'] = "No RSS URL provided"
    elif not rrss_name:
        schema_data['rrss_feed_error'] = "No RSS name provided"
    elif rrss_name not in rrss_valid_names:
        schema_data['rrss_feed_error'] = "Invalid RSS name"
    else:
        try:
            rrss = fastfeedparser.parse(rss_url)
            if not rrss.feed and not rrss.entries:
                schema_data['rrss_feed_error'] = "No feed or entries found"
            else:
                schema_data['rrss_feed_url'] = rss_url
                schema_data['rrss_feed_feed'] = rrss.feed or {}
                schema_data['rrss_feed_entries'] = rrss.entries or {}
        except HTTPError as e:
            schema_data['rrss_feed_error'] = str(e.reason)
        except (ImportError, Exception) as e:  # pylint: disable=broad-except
            schema_data['rrss_feed_error'] = str(e)

    schema_data['rrss_name'] = rrss_name

    return schema_data
