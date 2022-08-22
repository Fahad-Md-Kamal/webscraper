from .test_setup import TestSetup
from ..models import ScrapeData

class TestModel(TestSetup):

    def test_create_product(self):
        product = ScrapeData.objects.create(**self.product_one)
        self.assertEqual(product.title, self.product_one['title'])

    def test_model_str_method(self):
        product = ScrapeData.objects.create(**self.product_one)
        self.assertEqual(f'{product.title} - {product.price}', str(product))