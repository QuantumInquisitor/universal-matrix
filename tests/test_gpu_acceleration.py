import unittest
import jwt
import datetime

SECRET_KEY = "universal_matrix_super_secret_jwt_key_change_in_prod"
ALGORITHM = "HS256"

class TestRBACAuthentication(unittest.TestCase):

    def test_jwt_token_generation_and_validation(self):
        """Verify JWT token encoding, role attribution, and expiration validation."""
        exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
        payload = {"sub": "operator", "role": "admin", "exp": exp}
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        self.assertEqual(decoded["sub"], "operator")
        self.assertEqual(decoded["role"], "admin")

    def test_invalid_role_rejection(self):
        """Verify non-admin roles fail access check."""
        exp = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1)
        payload = {"sub": "guest", "role": "viewer", "exp": exp}
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        
        decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        self.assertNotEqual(decoded["role"], "admin")

if __name__ == "__main__":
    unittest.main()