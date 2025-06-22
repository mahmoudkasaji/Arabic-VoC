#!/usr/bin/env python3
"""
Unified Workflow Manager for Arabic VoC Platform
Provides one-command access to all DevOps operations
"""

import sys
import subprocess
from pathlib import Path

class WorkflowManager:
    """Central workflow management for easy Replit integration"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        
    def run_workflow(self, workflow_name):
        """Execute specific workflow"""
        workflows = {
            'status': 'bash workflows/environment-status.sh',
            'test': 'bash workflows/test-suite.sh',
            'staging': 'bash workflows/deploy-staging.sh',
            'seed': 'bash workflows/database-seed.sh',
            'deploy': 'bash workflows/quick-deploy.sh',
            'dev': 'python scripts/env_manager.py run development',
            'health': 'python scripts/env_manager.py health development'
        }
        
        if workflow_name not in workflows:
            self.show_help()
            return False
            
        cmd = workflows[workflow_name]
        print(f"Running workflow: {workflow_name}")
        print("=" * 50)
        
        try:
            result = subprocess.run(cmd, shell=True, cwd=self.project_root)
            return result.returncode == 0
        except Exception as e:
            print(f"Workflow failed: {e}")
            return False
            
    def show_help(self):
        """Display available workflows"""
        print("Arabic VoC Platform - Workflow Manager")
        print("=" * 40)
        print("Available workflows:")
        print("  python workflow.py status   - Check all environments")
        print("  python workflow.py test     - Run test suite")
        print("  python workflow.py staging  - Deploy to staging")
        print("  python workflow.py seed     - Add test data")
        print("  python workflow.py deploy   - Quick test + deploy")
        print("  python workflow.py dev      - Start development")
        print("  python workflow.py health   - Health check")
        print()
        print("Current Status:")
        subprocess.run("bash workflows/environment-status.sh", shell=True, cwd=self.project_root)

def main():
    manager = WorkflowManager()
    
    if len(sys.argv) < 2:
        manager.show_help()
        return
        
    workflow = sys.argv[1]
    success = manager.run_workflow(workflow)
    
    if not success:
        sys.exit(1)

if __name__ == '__main__':
    main()