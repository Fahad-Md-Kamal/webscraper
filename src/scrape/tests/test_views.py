from .test_setup import TestSetup


class TestViews(TestSetup):
    """
    Test App views and API action verbs
    """

    def test_items_list_api(self):
        res = self.client.get(self.scrape_url)
        self.assertEqual(res.status_code, 200)

    def test_item_create_api(self):
        res = self.client.post(self.scrape_url, self.product_one)
        self.assertEqual(res.status_code, 201)

    def test_detail_not_found_response(self):
        res = self.client.get(self.scrape_detail_url)
        self.assertEqual(res.status_code, 404)

    def test_http_action_method_not_allowed(self):
        res = self.client.put(self.scrape_detail_url)
        self.assertEqual(res.status_code, 405)