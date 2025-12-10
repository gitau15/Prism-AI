import unittest
from fastapi.testclient import TestClient
from app.main import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
    
    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
    
    def test_auth_login_endpoint(self):
        response = self.client.post("/api/v1/auth/login", data={
            "username": "test@example.com",
            "password": "testpassword"
        })
        # This will fail because we don't have a real user, but the endpoint exists
        self.assertEqual(response.status_code, 401)

if __name__ == "__main__":
    unittest.main()