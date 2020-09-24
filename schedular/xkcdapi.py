import random
import requests
import logging
import sys

log = logging.getLogger('XKCD_SERVICE_API')
log.setLevel(logging.DEBUG)
log_format = logging.Formatter("%(levelname)-10s %(name)-10s %(asctime)s %(message)s")
ch = logging.StreamHandler(sys.stdout)
ch.setFormatter(log_format)
log.addHandler(ch)

API = "http://xkcd.com/info.0.json"
COMIC_URL = 'https://xkcd.com/%i/info.0.json'

class XkcdAPi:

    @classmethod
    def _api_address(cls):
        return API

    @classmethod
    def get_random_comic_number(cls):
        response = cls._get_json(cls._api_address())
        return random.randint(0, response['num'])

    @classmethod
    def get_comic_img_url(cls, number):
        url = COMIC_URL % number
        return cls._get_json(url)['img']

    @classmethod
    def get_image(cls, number):
        url = COMIC_URL % number
        img_url = cls._get_json(url)['img']
        img_title = cls._get_json(url)['title']
        return cls._request(img_url).content, img_title

    @classmethod
    def _get_json(cls, url):
        response = cls._request(url)
        try:
            return response.json()
        except Exception as e:
            log.error(e)


    @classmethod
    def _request(cls, url):
        try:
            return requests.get(url)

        except Exception as e:
            log.error(e)

