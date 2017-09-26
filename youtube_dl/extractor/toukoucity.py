from __future__ import unicode_literals

import re

from .common import InfoExtractor
from ..compat import compat_str
from ..utils import (
    clean_html,
    dict_get,
    ExtractorError,
    int_or_none,
    parse_duration,
    unified_strdate,
)


class ToukouCityIE(InfoExtractor):
    _VALID_URL =  r'https?://(?:www\.)?toukoucity\.to/video/(?P<id>[A-Za-z0-9]+)/?'

    _TESTS = [{
        'url': 'http://toukoucity.to/video/zIb0ZaadjH/',
        'md5': '8281348b8d3c53d39fffb377d24eac4e',
        'info_dict': {
            'id': '1509445',
            'display_id': 'femaleagent_shy_beauty_takes_the_bait',
            'ext': 'mp4',
            'title': 'FemaleAgent Shy beauty takes the bait',
            'upload_date': '20121014',
            'uploader': 'Ruseful2011',
            'duration': 893,
            'age_limit': 18,
            'categories': ['Fake Hub', 'Amateur', 'MILFs', 'POV', 'Boss', 'Office', 'Oral', 'Reality', 'Sexy'],
        },
    }]

    def _real_extract(self, url):
        mobj = re.match(self._VALID_URL, url)
        video_id = mobj.group('id')

        webpage = self._download_webpage(url, video_id)

        title = self._html_search_regex(
            [r'<h1[^>]*>([^<]+)</h1>'],
            webpage, 'title')

        video_url = self._search_regex(
            [r'''file(?P<q>["']),\s*(?P=q)(?P<mp4>.+?)(?P=q)'''],
            webpage, 'video url', group='mp4', default=None)

        thumbnail = self._search_regex(
            [r'''image(?P<q>["']),\s*(?P=q)(?P<thumbnail>.+?)(?P=q)'''],
            webpage, 'thumbnail', fatal=False, group='thumbnail')

        # Only one format available
        formats = [{
                    'format_id': 'source',
                    'url': video_url,
                    'quality': 0,
                }]

        return {
            'id': video_id,
            'title': title,
            'thumbnail': thumbnail,
            'formats': formats
        }
