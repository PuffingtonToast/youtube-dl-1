import re

from .common import InfoExtractor

from ..compat import compat_urllib_parse_urlparse, compat_HTTPError
from ..utils import (
    int_or_none,
    mimetype2ext,
    remove_end,
    url_or_none,
    orderedSet,
    ExtractorError
)


class VrPornIE(InfoExtractor):
    # https://www.tokyomotion.net/video/2015313/%E3%83%95%E3%82%A7%E3%83%A9%E3%80%80%EF%BC%92
    _VALID_URL = r'https?://(www.)?vrporn.com/(?P<id>[^#!]+)'

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage, urlh = self._download_webpage_handle(url, video_id, encoding='utf-8')
        age_limit = 18
        title_re = r'<input type="hidden" name="post_title_hidden_tag" value="(?P<title>.+?)"'
        title = re.search(title_re, webpage).groupdict()['title']

        user_re = r'<span class="left_links"><a href\s*=\s*"https://vrporn.com/studio/(?P<username>.+?)/.*?"'
        uploader = re.search(user_re, webpage).groupdict()['username']

        data_re = r'data-id=".+?" data="(?P<data>.+?)"\s*?name="4K"><span>4K'

        data_result = re.search(data_re, webpage).groupdict()['data']

        return {
            'id': video_id,
            'title': title,
            'age_limit': age_limit,
            'formats': [{
                'url': data_result,
                'ext': 'mp4',
                'format_id': '4k'
            }],
            'uploader': uploader
        }
