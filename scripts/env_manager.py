#!/usr/bin/env python3
"""
Environment manager for Arabic VoC platform
Handles switching between test, staging, and production environments
"""

import os
import sys
import subprocess
from pathlib import Path

class EnvironmentManager:
    """Manage different environments for the Arabic VoC platform"""
    
    ENVIRONMENTS = {
        'development': {
            'port': 5000,
            'workers': 1,
            'debug': True,
            'reload': True,
            'env_file': 'environments/.env.development'
        },
        'test': {
            'port': 5002,
            'workers': 1,
            'debug': False,
            'reload': False,
            'env_file': 'environments/.env.test'
        },
        'staging': {
            'port': 5001,
            'workers': 2,
            'debug': False,
            'reload': False,
            'env_file': 'environments/.env.staging'
        },
        'production': {
            'port': 5000,
            'workers': 4,
            'debug': False,
            'reload': False,
            'env_file': 'environments/.env.production'
        }
    }
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        
    def load_env_file(self, env_file):
        """Load environment variables from file"""
        env_path = self.project_root / env_file
        if not env_path.exists():
            raise FileNotFoundError(f"Environment file not found: {env_path}")
            
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
                    
    def validate_environment(self, env_name):
        """Validate environment configuration"""
        if env_name not in self.ENVIRONMENTS:
            raise ValueError(f"Unknown environment: {env_name}")
            
        env_config = self.ENVIRONMENTS[env_name]
        
        # Load environment file
        self.load_env_file(env_config['env_file'])
        
        # Validate required variables based on environment
        if env_name == 'production':
            required_vars = ['SECRET_KEY', 'DATABASE_URL', 'OPENAI_API_KEY']
            missing = [var for var in required_vars if not os.environ.get(var)]
            if missing:
                raise ValueError(f"Missing required production variables: {missing}")
                
        return True
        
    def run_environment(self, env_name):
        """Run the application in specified environment"""
        print(f"Starting Arabic VoC Platform in {env_name} environment...")
        
        # Validate environment
        self.validate_environment(env_name)
        
        env_config = self.ENVIRONMENTS[env_name]
        
        # Set Flask environment
        os.environ['FLASK_ENV'] = env_name
        
        # Build command
        if env_name == 'development':
            cmd = [
                'python', 'main.py'
            ]
        else:
            cmd = [
                'gunicorn',
                '--bind', f"0.0.0.0:{env_config['port']}",
                '--workers', str(env_config['workers']),
                '--timeout', '120',
                'main:app'
            ]
            
            if env_name == 'production':
                cmd.extend(['--max-requests', '1000'])
                
        print(f"Running: {' '.join(cmd)}")
        subprocess.run(cmd, cwd=self.project_root)
        
    def run_tests(self):
        """Run test suite"""
        print("Running test suite...")
        
        # Load test environment
        self.load_env_file('environments/.env.test')
        os.environ['FLASK_ENV'] = 'test'
        
        # Initialize test database
        subprocess.run([
            'python', '-c',
            'from app import app, db; '
            'with app.app_context(): db.create_all(); '
            'print("Test database initialized")'
        ], cwd=self.project_root)
        
        # Run tests
        subprocess.run([
            'python', '-m', 'pytest', 'tests/', '-v',
            '--cov=.', '--cov-report=html', '--cov-report=term'
        ], cwd=self.project_root)
        
    def health_check(self, env_name):
        """Check health of specified environment"""
        env_config = self.ENVIRONMENTS[env_name]
        port = env_config['port']
        
        try:
            import requests
            response = requests.get(f"http://localhost:{port}/health", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"Environment {env_name} is healthy:")
                print(f"  Status: {data.get('status')}")
                print(f"  Database: {data.get('database')}")
                print(f"  Arabic support: {data.get('arabic_support')}")
                return True
            else:
                print(f"Environment {env_name} returned status {response.status_code}")
                return False
        except Exception as e:
            print(f"Environment {env_name} health check failed: {e}")
            return False

def main():
    """Main entry point"""
    manager = EnvironmentManager()
    
    if len(sys.argv) < 2:
        print("Usage: python env_manager.py <command> [environment]")
        print("Commands:")
        print("  run <env>     - Run application in specified environment")
        print("  test          - Run test suite")
        print("  health <env>  - Check environment health")
        print("  list          - List available environments")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == 'run':
        if len(sys.argv) < 3:
            print("Please specify environment: development, test, staging, or production")
            sys.exit(1)
        env_name = sys.argv[2]
        manager.run_environment(env_name)
        
    elif command == 'test':
        manager.run_tests()
        
    elif command == 'health':
        if len(sys.argv) < 3:
            print("Please specify environment to check")
            sys.exit(1)
        env_name = sys.argv[2]
        manager.health_check(env_name)
        
    elif command == 'list':
        print("Available environments:")
        for env_name, config in manager.ENVIRONMENTS.items():
            print(f"  {env_name:12} - Port {config['port']}, {config['workers']} workers")
            
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()