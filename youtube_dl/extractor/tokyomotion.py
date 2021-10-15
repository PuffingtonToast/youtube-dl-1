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


class TokyoMotionIE(InfoExtractor):
    # https://www.tokyomotion.net/video/2015313/%E3%83%95%E3%82%A7%E3%83%A9%E3%80%80%EF%BC%92
    _VALID_URL = r'https?://(www.)?tokyomotion\.net/video/(?P<id>[^#!]+)'

    @staticmethod
    def _info_to_format(info, headers):
        return {
            'url': info['source'],
            'ext': info['ext'],
            'format_id': info['format_id'],
            'http_headers': headers
        }

    def _real_extract(self, url):
        headers = {
            'Host': 'www.tokyomotion.net',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:90.0) Gecko/20100101 Firefox/90.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'identity',
            'Referer': 'https://www.tokyomotion.net/videos'
        }

        video_id = self._match_id(url)

        webpage, urlh = self._download_webpage_handle(url, video_id, headers=headers, encoding='utf-8')
        age_limit = 18
        title_re = r'<h3 class="hidden-xs big-title-truncate m-t-0">(?P<title>.+?)</h3>'
        title = re.search(title_re, webpage).groupdict()['title'][:20]

        user_re = r' user-container">[^<]+?<a href="/user/(?P<username>.+?)">'
        uploader = re.search(user_re, webpage).groupdict()['username']

        hd_source_re = r'<source src="(?P<source>[^"]+)" res="(?P<format_id>HD)" label="HD" type="video/(?P<ext>.+?)">'
        sd_source_re = r'<source src="(?P<source>[^"]+)" default res="(?P<format_id>SD)" label="SD" type="video/(?P<ext>.+?)">'

        hd_re_result = re.search(hd_source_re, webpage)
        sd_re_result = re.search(sd_source_re, webpage)

        preferred_source = hd_re_result.groupdict() if hd_re_result else sd_re_result.groupdict()
        formats = [self._info_to_format(preferred_source, headers)]

        id_re = r'https://www.tokyomotion.net/vsrc/[^/]+/(?P<vid_id>.+)'
        actual_id = re.search(id_re, preferred_source['source']).groupdict()['vid_id']

        return {
            'id': actual_id,
            'title': title,
            'age_limit': age_limit,
            'formats': formats,
            'uploader': uploader
        }