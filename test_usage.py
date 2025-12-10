import unittest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.base import Base
from app.models.user import User, SubscriptionTier
from app.core.usage import check_usage_limits
from datetime import date

class TestUsageTracking(unittest.TestCase):
    def setUp(self):
        # Create an in-memory SQLite database for testing
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.db = SessionLocal()
        
        # Create a test user
        self.test_user = User(
            email="test@example.com",
            hashed_password="hashed_password",
            subscription_tier=SubscriptionTier.EXPLORER,
            pages_processed_this_month=0,
            queries_this_month=0,
            last_usage_reset_date=date.today()
        )
        self.db.add(self.test_user)
        self.db.commit()
        self.db.refresh(self.test_user)

    def tearDown(self):
        self.db.close()

    def test_check_page_limit_not_exceeded(self):
        """Test that page limit checking works when limit is not exceeded"""
        # Explorer tier has 50 pages limit
        for i in range(49):  # Process 49 pages, should be fine
            user = check_usage_limits(self.test_user.id, "page", self.db)
            self.assertEqual(user.pages_processed_this_month, i + 1)
        
        # Should still be under limit
        user = check_usage_limits(self.test_user.id, "page", self.db)
        self.assertEqual(user.pages_processed_this_month, 50)

    def test_check_page_limit_exceeded(self):
        """Test that page limit checking raises exception when limit is exceeded"""
        # Process 50 pages to reach the limit
        for i in range(50):
            user = check_usage_limits(self.test_user.id, "page", self.db)
        
        # The next page should raise an exception
        with self.assertRaises(Exception) as context:
            check_usage_limits(self.test_user.id, "page", self.db)
        
        self.assertIn("monthly page processing limit", str(context.exception))

    def test_check_query_limit_not_exceeded(self):
        """Test that query limit checking works when limit is not exceeded"""
        # Explorer tier has 100 queries limit
        for i in range(99):  # Process 99 queries, should be fine
            user = check_usage_limits(self.test_user.id, "query", self.db)
            self.assertEqual(user.queries_this_month, i + 1)
        
        # Should still be under limit
        user = check_usage_limits(self.test_user.id, "query", self.db)
        self.assertEqual(user.queries_this_month, 100)

    def test_check_query_limit_exceeded(self):
        """Test that query limit checking raises exception when limit is exceeded"""
        # Process 100 queries to reach the limit
        for i in range(100):
            user = check_usage_limits(self.test_user.id, "query", self.db)
        
        # The next query should raise an exception
        with self.assertRaises(Exception) as context:
            check_usage_limits(self.test_user.id, "query", self.db)
        
        self.assertIn("monthly query limit", str(context.exception))

    def test_upgrade_to_pro_tier(self):
        """Test upgrading user to PRO tier increases limits"""
        # First, use up the EXPLORER limits
        for i in range(50):
            user = check_usage_limits(self.test_user.id, "page", self.db)
        
        # Upgrade user to PRO tier
        self.test_user.subscription_tier = SubscriptionTier.PRO
        self.db.commit()
        
        # Now we should be able to process more pages (up to 500 for PRO)
        for i in range(100):  # Process 100 more pages
            user = check_usage_limits(self.test_user.id, "page", self.db)
        
        self.assertEqual(user.pages_processed_this_month, 150)

if __name__ == "__main__":
    unittest.main()