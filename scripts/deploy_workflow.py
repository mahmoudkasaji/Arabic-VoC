#!/usr/bin/env python3
"""
Comprehensive deployment workflow manager for Arabic VoC platform
Automates the development → test → staging → production pipeline
"""

import os
import sys
import subprocess
import json
import time
import shlex
from pathlib import Path

class DeploymentWorkflow:
    """Manage the complete deployment workflow"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.environments = ['development', 'test', 'staging', 'production']
        
    def run_command(self, cmd, cwd=None):
        """Run command and return result"""
        try:
            # Convert string commands to list for shell=False safety
            if isinstance(cmd, str):
                cmd_list = shlex.split(cmd)
            else:
                cmd_list = cmd
            
            result = subprocess.run(
                cmd_list, shell=False, cwd=cwd or self.project_root,
                capture_output=True, text=True, check=True
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr
            
    def check_git_status(self):
        """Check if git working directory is clean"""
        success, output = self.run_command("git status --porcelain")
        if not success:
            return False, "Git status check failed"
        
        if output.strip():
            return False, "Working directory has uncommitted changes"
        
        return True, "Git working directory is clean"
        
    def run_tests(self):
        """Run comprehensive test suite"""
        print("🧪 Running test suite...")
        
        # Run tests using environment manager
        success, output = self.run_command("python scripts/env_manager.py test")
        
        if not success:
            return False, f"Tests failed: {output}"
            
        # Check for test coverage
        if "FAILED" in output:
            return False, "Some tests failed"
            
        return True, "All tests passed"
        
    def check_environment_health(self, environment):
        """Check if environment is healthy"""
        print(f"🔍 Checking {environment} environment health...")
        
        success, output = self.run_command(
            f"python scripts/env_manager.py health {environment}"
        )
        
        return success, output
        
    def deploy_to_environment(self, environment):
        """Deploy to specific environment"""
        print(f"🚀 Deploying to {environment}...")
        
        # Set up database if needed
        success, output = self.run_command(
            f"python scripts/database_manager.py {environment} create"
        )
        
        if not success and "already exists" not in output.lower():
            return False, f"Database setup failed: {output}"
            
        # For non-production, seed with test data
        if environment in ['development', 'staging']:
            self.run_command(
                f"python scripts/database_manager.py {environment} seed"
            )
            
        return True, f"Deployed to {environment} successfully"
        
    def create_git_tag(self, version):
        """Create git tag for release"""
        print(f"🏷️  Creating git tag {version}...")
        
        success, output = self.run_command(f"git tag -a {version} -m 'Release {version}'")
        if not success:
            return False, f"Failed to create tag: {output}"
            
        success, output = self.run_command(f"git push origin {version}")
        if not success:
            return False, f"Failed to push tag: {output}"
            
        return True, f"Tag {version} created and pushed"
        
    def full_deployment_pipeline(self, target_environment='staging'):
        """Run complete deployment pipeline"""
        print("🔄 Starting full deployment pipeline...\n")
        
        steps = []
        
        # Step 1: Check git status
        success, message = self.check_git_status()
        steps.append(("Git Status", success, message))
        if not success:
            self.print_results(steps)
            return False
            
        # Step 2: Run tests
        success, message = self.run_tests()
        steps.append(("Test Suite", success, message))
        if not success:
            self.print_results(steps)
            return False
            
        # Step 3: Deploy to development (if not already)
        if target_environment != 'development':
            success, message = self.deploy_to_environment('development')
            steps.append(("Development Deploy", success, message))
            
        # Step 4: Deploy to test environment
        if target_environment not in ['development']:
            success, message = self.deploy_to_environment('test')
            steps.append(("Test Deploy", success, message))
            
        # Step 5: Deploy to staging (if target is staging or production)
        if target_environment in ['staging', 'production']:
            success, message = self.deploy_to_environment('staging')
            steps.append(("Staging Deploy", success, message))
            
            # Wait for staging verification
            print("⏳ Waiting 10 seconds for staging verification...")
            time.sleep(10)
            
            success, message = self.check_environment_health('staging')
            steps.append(("Staging Health Check", success, message))
            if not success:
                self.print_results(steps)
                return False
                
        # Step 6: Deploy to production (only if explicitly requested)
        if target_environment == 'production':
            confirm = input("🚨 Deploy to PRODUCTION? This affects live users. (yes/no): ")
            if confirm.lower() != 'yes':
                steps.append(("Production Deploy", False, "User cancelled"))
                self.print_results(steps)
                return False
                
            success, message = self.deploy_to_environment('production')
            steps.append(("Production Deploy", success, message))
            
            if success:
                success, message = self.check_environment_health('production')
                steps.append(("Production Health Check", success, message))
                
        self.print_results(steps)
        return all(step[1] for step in steps)
        
    def print_results(self, steps):
        """Print deployment results"""
        print("\n" + "="*60)
        print("🔄 DEPLOYMENT PIPELINE RESULTS")
        print("="*60)
        
        for step_name, success, message in steps:
            status = "✅ PASS" if success else "❌ FAIL"
            print(f"{status:<8} {step_name:<20} {message}")
            
        print("="*60)
        
    def quick_development_setup(self):
        """Quick setup for development environment"""
        print("🛠️  Setting up development environment...")
        
        steps = [
            ("Create DB", lambda: self.run_command("python scripts/database_manager.py development create")),
            ("Seed Data", lambda: self.run_command("python scripts/database_manager.py development seed")),
            ("Health Check", lambda: self.check_environment_health('development'))
        ]
        
        results = []
        for step_name, step_func in steps:
            success, message = step_func()
            results.append((step_name, success, message))
            
        self.print_results(results)
        
        if all(result[1] for result in results):
            print("🎉 Development environment ready!")
            print("🔗 Run: python scripts/env_manager.py run development")
        
    def environment_status(self):
        """Show status of all environments"""
        print("📊 ENVIRONMENT STATUS REPORT")
        print("="*50)
        
        for env in self.environments:
            print(f"\n{env.upper()}:")
            
            # Database stats
            success, output = self.run_command(
                f"python scripts/database_manager.py {env} stats"
            )
            
            if success:
                print(f"  Database: ✅ Connected")
                # Parse stats from output
                lines = output.strip().split('\n')
                for line in lines:
                    if 'Total feedback:' in line:
                        print(f"  {line.strip()}")
            else:
                print(f"  Database: ❌ Error")
                
            # Health check (for running environments)
            success, output = self.check_environment_health(env)
            if success:
                print(f"  Health: ✅ Healthy")
            else:
                print(f"  Health: ⚠️  Not running or unhealthy")

def main():
    """Main entry point"""
    workflow = DeploymentWorkflow()
    
    if len(sys.argv) < 2:
        print("Usage: python deploy_workflow.py <command> [options]")
        print("\nCommands:")
        print("  deploy <env>     - Full deployment pipeline to environment")
        print("  setup-dev        - Quick development environment setup")
        print("  status           - Show status of all environments")
        print("  test             - Run test suite only")
        print("  health <env>     - Check specific environment health")
        print("\nEnvironments: development, test, staging, production")
        sys.exit(1)
        
    command = sys.argv[1]
    
    if command == 'deploy':
        if len(sys.argv) < 3:
            target = 'staging'  # Default to staging
        else:
            target = sys.argv[2]
            
        if target not in workflow.environments:
            print(f"Invalid environment: {target}")
            sys.exit(1)
            
        success = workflow.full_deployment_pipeline(target)
        sys.exit(0 if success else 1)
        
    elif command == 'setup-dev':
        workflow.quick_development_setup()
        
    elif command == 'status':
        workflow.environment_status()
        
    elif command == 'test':
        success, message = workflow.run_tests()
        print("✅ Tests passed" if success else f"❌ Tests failed: {message}")
        sys.exit(0 if success else 1)
        
    elif command == 'health':
        if len(sys.argv) < 3:
            print("Please specify environment")
            sys.exit(1)
        env = sys.argv[2]
        success, message = workflow.check_environment_health(env)
        print(f"Environment {env}: {'✅ Healthy' if success else '❌ Unhealthy'}")
        print(message)
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == '__main__':
    main()