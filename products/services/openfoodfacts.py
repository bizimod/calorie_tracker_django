import logging
from typing import Optional

import requests
from django.conf import settings

logger = logging.getLogger(__name__)



class OpenFoodFactsError(Exception):
    pass


class OpenFoodFactsClient:

    def __init__(self):
        OFF = settings.OPEN_FOOD_FACTS
        self.base_url = OFF['BASE_URL']
        self.timeout = OFF['TIMEOUT']
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': OFF['USER_AGENT']})


    def get_by_barcode(self, barcode):
        url = f'{self.base_url}/api/v2/product/{barcode}.json'
        try:
            r = self.session.get(url, timeout=self.timeout)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.warning(f'OFF request failed for {barcode} : {e}')
            raise OpenFoodFactsError(e)
        try:
            data = r.json()
        except ValueError:
            logger.warning(f'OFF returned non-JSON for {barcode}')
            raise OpenFoodFactsError('non-JSON response')

        if data.get('status') != 1:
            return None
        return data.get('product')

    def search(self, query, page_size: int = 10):
        url = f"{self.base_url}/cgi/search.pl"
        params = {
            'search_terms': query,
            'search_simple': 1,
            'action': 'process',
            'json': 1,
            'page_size': page_size,
            'fields': 'code,product_name,brands,nutriments'
        }
        try:
            r = self.session.get(url, params=params, timeout=self.timeout)
            r.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.warning(f'OFF request failed for {query} : {e}')
            raise OpenFoodFactsError(str(e))
        return r.json().get('products', [])
