import unittest
import os

class TestPhase82WebXR(unittest.TestCase):
    def test_public_html_exists(self):
        self.assertTrue(os.path.exists("public/index.html"))

    def test_api_has_spatial_mount(self):
        from src.api import app
        routes = [route.path for route in app.routes]
        self.assertIn("/spatial", routes)

if __name__ == "__main__":
    unittest.main()

