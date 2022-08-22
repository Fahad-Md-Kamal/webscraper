from rest_framework.test import APITestCase
from django.urls import reverse


class TestSetup(APITestCase):
    """
    Application wide test setup
    """

    def setUp(self) -> None:
        self.scrape_url = reverse('scrape-list')
        self.scrape_detail_url = reverse('scrape-detail', kwargs={'pk':1})

        self.product_one = {
            "product_uid": '123456765432345',
            'title': 'Test Product',
            'price': '22.34',
            'image_src': ' https://ir.ebaystatic.com/cr/v/c1/s_1x2.gif',
            'product_link': 'https://www.ebay.com/itm/304604635190?hash=item46ebd9e036:g:KU4AAOSwxR1eVVvL'
        }
        return super().setUp()
