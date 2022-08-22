from .test_setup import TestSetup


class TestViews(TestSetup):

    def test_scrape_endpoint(self):
        res = self.client.post(self.scrape_url)
        self.assertEqual(res.status_code, 200)

    def test_scrape_detail_endpoint(self):
        res = self.client.post(self.scrape_detail_url)
        self.assertEqual(res.status_code, 200)