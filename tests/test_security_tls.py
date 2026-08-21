import unittest
import os

class TestTLSConfiguration(unittest.TestCase):

    def test_nginx_conf_exists(self):
        """Verify NGINX configuration exists and contains WSS and SSE proxy directives."""
        conf_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "nginx", "nginx.conf")
        self.assertTrue(os.path.exists(conf_path), "nginx.conf file is missing")

        with open(conf_path, "r") as f:
            content = f.read()

        self.assertIn("listen 443 ssl;", content)
        self.assertIn("proxy_set_header Upgrade $http_upgrade;", content)
        self.assertIn("proxy_buffering off;", content)

if __name__ == "__main__":
    unittest.main()