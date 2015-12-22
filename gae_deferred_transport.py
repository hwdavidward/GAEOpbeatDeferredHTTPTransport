# -*- coding: utf-8 -*-
import logging
import json

from google.appengine.ext import deferred
from google.appengine.api import urlfetch
from google.appengine.api.urlfetch_errors import Error as URLFetchError, DeadlineExceededError

from opbeat.conf import defaults
from opbeat.transport.base import Transport, TransportException

__author__ = 'DavidWard'


class GAEDeferredHTTPTransport(Transport):
    scheme = ['http', 'https']
    async_mode = True

    def __init__(self, parsed_url):
        self.check_scheme(parsed_url)
        self._parsed_url = parsed_url
        self._url = parsed_url.geturl()

    @classmethod
    def send_request(cls, url, data, headers):
        timeout = defaults.TIMEOUT or 30
        urlfetch.set_default_fetch_deadline(timeout)

        try:
            response = urlfetch.fetch(url, payload=data, method='POST', headers=headers)
            body = response.content

            if response.status_code == 429:
                message = 'Temporarily rate limited: (url: %s, body: %s)' % (url, body)
                raise TransportException(message, data, print_trace=False)

        except URLFetchError as e:
            message = 'Unable to reach Opbeat server: %s (url: %s)' % (e, url)
            raise TransportException(message, data, print_trace=True)
        except DeadlineExceededError as de:
            message = "Connection to Opbeat server timed out (url: %s, timeout: %d seconds)" % (url, timeout)
            raise TransportException(message, data, print_trace=True)
        except Exception as ex:
            logging.error("An error occurred while sending your request: %s", e)
            raise

        #content = json.loads(response.content)
        #logging.debug("Content: %s", content)

    def send_async(self, data, headers, success_callback=None, fail_callback=None):
        kwargs = {
            'url': self._url,
            'data': data,
            'headers': headers
        }

        try:
            deferred.defer(self.send_request, _queue='opbeat-activity-tracking', **kwargs)
        except Exception as e:
            fail_callback(exception=e)
        else:
            success_callback(url=self._url)

