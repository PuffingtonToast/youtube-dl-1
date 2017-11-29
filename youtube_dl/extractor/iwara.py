# coding: utf-8
from __future__ import unicode_literals

import itertools
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


class IwaraIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.|ecchi\.)?iwara\.tv/videos/(?P<id>[a-zA-Z0-9]+)'
    _TESTS = [{
        'url': 'http://iwara.tv/videos/amVwUl1EHpAD9RD',
        # md5 is unstable
        'info_dict': {
            'id': 'amVwUl1EHpAD9RD',
            'ext': 'mp4',
            'title': '【MMD R-18】ガールフレンド carry_me_off',
            'age_limit': 18,
        },
    }, {
        'url': 'http://ecchi.iwara.tv/videos/Vb4yf2yZspkzkBO',
        'md5': '7e5f1f359cd51a027ba4a7b7710a50f0',
        'info_dict': {
            'id': '0B1LvuHnL-sRFNXB1WHNqbGw4SXc',
            'ext': 'mp4',
            'title': '[3D Hentai] Kyonyu × Genkai × Emaki Shinobi Girls.mp4',
            'age_limit': 18,
        },
        'add_ie': ['GoogleDrive'],
    }, {
        'url': 'http://www.iwara.tv/videos/nawkaumd6ilezzgq',
        # md5 is unstable
        'info_dict': {
            'id': '6liAP9s2Ojc',
            'ext': 'mp4',
            'age_limit': 18,
            'title': '[MMD] Do It Again Ver.2 [1080p 60FPS] (Motion,Camera,Wav+DL)',
            'description': 'md5:590c12c0df1443d833fbebe05da8c47a',
            'upload_date': '20160910',
            'uploader': 'aMMDsork',
            'uploader_id': 'UCVOFyOSCyFkXTYYHITtqB7A',
        },
        'add_ie': ['Youtube'],
    }]

    def _real_extract(self, url):
        video_id = self._match_id(url)

        webpage, urlh = self._download_webpage_handle(url, video_id)

        hostname = compat_urllib_parse_urlparse(urlh.geturl()).hostname
        # ecchi is 'sexy' in Japanese
        age_limit = 18 if hostname.split('.')[0] == 'ecchi' else 0

        video_data = self._download_json('http://www.iwara.tv/api/video/%s' % video_id, video_id)

        if not video_data:
            iframe_url = self._html_search_regex(
                r'<iframe[^>]+src=([\'"])(?P<url>[^\'"]+)\1',
                webpage, 'iframe URL', group='url')
            return {
                '_type': 'url_transparent',
                'url': iframe_url,
                'age_limit': age_limit,
            }

        title = remove_end(self._html_search_regex(
            r'<title>([^<]+)</title>', webpage, 'title'), ' | Iwara')

        formats = []
        for a_format in video_data:
            format_uri = url_or_none(a_format.get('uri'))
            if not format_uri:
                continue
            format_id = a_format.get('resolution')
            height = int_or_none(self._search_regex(
                r'(\d+)p', format_id, 'height', default=None))
            formats.append({
                'url': self._proto_relative_url(format_uri, 'https:'),
                'format_id': format_id,
                'ext': mimetype2ext(a_format.get('mime')) or 'mp4',
                'height': height,
                'width': int_or_none(height / 9.0 * 16.0 if height else None),
                'quality': 1 if format_id == 'Source' else 0,
            })

        self._sort_formats(formats)

        return {
            'id': video_id,
            'title': title,
            'age_limit': age_limit,
            'formats': formats,
        }


class IwaraUserVideosIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.|ecchi\.)?iwara\.tv/users/(?P<id>[^/]+)(/videos)?/?$'
    _TESTS = [{
        'url': 'http://ecchi.iwara.tv/users/DNNinetail/videos',
        'info_dict': {
            'id': 'DNNinetail',
        },
        'playlist_mincount': 567,
    }, {
        'url': 'http://ecchi.iwara.tv/users/DNNinetail/videos',
        'playlist_mincount': 567,
    }]

    @classmethod
    def _extract_entries(cls, webpage):
        if '_VIDEO_URL_RE' not in cls.__dict__:
            cls.VIDEO_URL_RE = re.compile(r'"/videos/.+?"')
        return orderedSet(cls.VIDEO_URL_RE.findall(webpage))

    def _extract_from_videos_list(self, url, page_num):
        user_id = self._match_id(url)
        hostname = compat_urllib_parse_urlparse(url).hostname
        scheme = compat_urllib_parse_urlparse(url).scheme

        try:
            videos_page_url = '%s://%s/users/%s/videos' % (scheme, hostname, user_id)
            videos_page = self._download_webpage(
                videos_page_url, user_id,
                'Downloading page %d at %s' % (page_num, videos_page_url),
                query={'page': page_num})
        except ExtractorError as e:
            if isinstance(e.cause, compat_HTTPError) and e.cause.code == 404:
                return []
            raise
        return [
            self.url_result(
                scheme + '://' + hostname + video_rel_path.strip('"'),
                IwaraIE.ie_key())
            for video_rel_path in self._extract_entries(videos_page)
        ]

    def _extract_from_user_page(self, url):
        user_id = self._match_id(url)
        hostname = compat_urllib_parse_urlparse(url).hostname
        scheme = compat_urllib_parse_urlparse(url).scheme

        try:
            user_page_url = '%s://%s/users/%s' % (scheme, hostname, user_id)
            user_page = self._download_webpage(
                user_page_url, user_id,
                'Downloading from user page at %s' % user_page_url)
        except ExtractorError as e:
            if isinstance(e.cause, compat_HTTPError) and e.cause.code == 404:
                return []
            raise
        return [
            self.url_result(
                scheme + '://' + hostname + video_rel_path.strip('"'),
                IwaraIE.ie_key())
            for video_rel_path in self._extract_entries(user_page)
        ]

    def _real_extract(self, url):
        user_id = self._match_id(url)

        entries = []
        for page_num in itertools.count(0):
            page_entries = self._extract_from_videos_list(url, page_num)
            if not page_entries:
                break
            entries.extend(page_entries)
        if not entries:
            self.to_screen('No videos in video list. Falling back to user page.')
            entries.extend(self._extract_from_user_page(url))

        return self.playlist_result(entries, user_id, user_id)


class IwaraFollowingIE(InfoExtractor):
    _VALID_URL = r'https?://(?:www\.|ecchi\.)?iwara\.tv/users/(?P<id>[^/]+)/following/?'
    _TESTS = [{
        'url': 'http://ecchi.iwara.tv/users/yunatbm/following',
        'info_dict': {
            'id': 'yunatbm_following_list',
        },
        'playlist_mincount': 12,
    }]

    @classmethod
    def _extract_entries(cls, webpage):
        if '_USER_URL_RE' not in cls.__dict__:
            cls.USER_URL_RE = re.compile(r'"/users/[^/]+?"')
        return orderedSet(cls.USER_URL_RE.findall(webpage))

    def _real_extract(self, url):
        follower_id = self._match_id(url)
        playlist_id = follower_id + "_following_list"
        hostname = compat_urllib_parse_urlparse(url).hostname
        scheme = compat_urllib_parse_urlparse(url).scheme

        entries = []
        for page_num in itertools.count(0):
            try:
                following_page_url = '%s://%s/users/%s/following' % (scheme, hostname, follower_id)
                following_page = self._download_webpage(
                    following_page_url, follower_id,
                    'Downloading page %d at %s' % (page_num, following_page_url),
                    query={'page': page_num})
            except ExtractorError as e:
                if isinstance(e.cause, compat_HTTPError) and e.cause.code == 404:
                    break
                raise
            page_entries = [
                self.url_result(
                    scheme + '://' + hostname + user_rel_path.strip('"'),
                    IwaraUserVideosIE.ie_key())
                for user_rel_path in self._extract_entries(following_page)
            ]

            if not page_entries:
                break
            entries.extend(page_entries)

        return self.playlist_result(entries, playlist_id, playlist_id)
