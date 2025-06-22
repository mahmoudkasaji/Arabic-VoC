#!/usr/bin/env python3
"""
Database manager for different environments
Handles database creation, migration, and seeding for test/staging/production
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app, db
from models_unified import Feedback, FeedbackChannel, FeedbackStatus

class DatabaseManager:
    """Manage databases across environments"""
    
    def __init__(self, environment):
        self.environment = environment
        self.load_environment()
        
    def load_environment(self):
        """Load environment-specific configuration"""
        env_file = f"environments/.env.{self.environment}"
        env_path = project_root / env_file
        
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        os.environ[key] = value
                        
        os.environ['FLASK_ENV'] = self.environment
        
    def create_database(self):
        """Create database tables"""
        with app.app_context():
            try:
                db.create_all()
                print(f"Database tables created for {self.environment} environment")
                return True
            except Exception as e:
                print(f"Error creating database: {e}")
                return False
                
    def drop_database(self):
        """Drop all database tables"""
        with app.app_context():
            try:
                db.drop_all()
                print(f"Database tables dropped for {self.environment} environment")
                return True
            except Exception as e:
                print(f"Error dropping database: {e}")
                return False
                
    def seed_test_data(self):
        """Seed database with test data"""
        if self.environment == 'production':
            print("Cannot seed production database with test data")
            return False
            
        with app.app_context():
            try:
                # Create sample Arabic feedback
                sample_feedback = [
                    {
                        'content': 'الخدمة ممتازة جداً وأنصح الجميع بالتعامل معكم',
                        'channel': FeedbackChannel.WEBSITE,
                        'rating': 5,
                        'sentiment_score': 0.8,
                        'language_detected': 'ar'
                    },
                    {
                        'content': 'هناك بعض المشاكل في التطبيق ولكن الدعم جيد',
                        'channel': FeedbackChannel.MOBILE_APP,
                        'rating': 3,
                        'sentiment_score': 0.2,
                        'language_detected': 'ar'
                    },
                    {
                        'content': 'خدمة سيئة للغاية ولا أنصح أحد بالتعامل معكم',
                        'channel': FeedbackChannel.EMAIL,
                        'rating': 1,
                        'sentiment_score': -0.7,
                        'language_detected': 'ar'
                    },
                    {
                        'content': 'التطبيق سهل الاستخدام والواجهة جميلة',
                        'channel': FeedbackChannel.MOBILE_APP,
                        'rating': 4,
                        'sentiment_score': 0.6,
                        'language_detected': 'ar'
                    },
                    {
                        'content': 'أحتاج مساعدة في استخدام الميزة الجديدة',
                        'channel': FeedbackChannel.WHATSAPP,
                        'rating': 3,
                        'sentiment_score': 0.0,
                        'language_detected': 'ar'
                    }
                ]
                
                for feedback_data in sample_feedback:
                    feedback = Feedback(**feedback_data)
                    db.session.add(feedback)
                    
                db.session.commit()
                print(f"Test data seeded for {self.environment} environment")
                print(f"Added {len(sample_feedback)} sample feedback records")
                return True
                
            except Exception as e:
                db.session.rollback()
                print(f"Error seeding test data: {e}")
                return False
                
    def backup_database(self, backup_file=None):
        """Create database backup"""
        if not backup_file:
            backup_file = f"backup_{self.environment}_{os.urandom(4).hex()}.sql"
            
        # This would need to be implemented based on the database type
        print(f"Database backup functionality would save to: {backup_file}")
        return True
        
    def get_database_stats(self):
        """Get database statistics"""
        with app.app_context():
            try:
                total_feedback = db.session.query(Feedback).count()
                processed_feedback = db.session.query(Feedback).filter_by(
                    status=FeedbackStatus.PROCESSED
                ).count()
                pending_feedback = db.session.query(Feedback).filter_by(
                    status=FeedbackStatus.PENDING
                ).count()
                
                channel_stats = db.session.query(
                    Feedback.channel,
                    db.func.count(Feedback.id).label('count')
                ).group_by(Feedback.channel).all()
                
                print(f"Database statistics for {self.environment}:")
                print(f"  Total feedback: {total_feedback}")
                print(f"  Processed: {processed_feedback}")
                print(f"  Pending: {pending_feedback}")
                print("  By channel:")
                for channel, count in channel_stats:
                    print(f"    {channel.value}: {count}")
                    
                return {
                    'total': total_feedback,
                    'processed': processed_feedback,
                    'pending': pending_feedback,
                    'channels': dict(channel_stats)
                }
                
            except Exception as e:
                print(f"Error getting database stats: {e}")
                return None

def main():
    """Main entry point"""
    if len(sys.argv) < 3:
        print("Usage: python database_manager.py <environment> <command>")
        print("Environments: development, test, staging, production")
        print("Commands:")
        print("  create    - Create database tables")
        print("  drop      - Drop all tables")
        print("  seed      - Seed with test data (not for production)")
        print("  stats     - Show database statistics")
        print("  backup    - Create database backup")
        sys.exit(1)
        
    environment = sys.argv[1]
    command = sys.argv[2]
    
    manager = DatabaseManager(environment)
    
    if command == 'create':
        manager.create_database()
    elif command == 'drop':
        confirm = input(f"Are you sure you want to drop all tables in {environment}? (yes/no): ")
        if confirm.lower() == 'yes':
            manager.drop_database()
        else:
            print("Operation cancelled")
    elif command == 'seed':
        manager.seed_test_data()
    elif command == 'stats':
        manager.get_database_stats()
    elif command == 'backup':
        manager.backup_database()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()