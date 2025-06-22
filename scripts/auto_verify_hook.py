#!/usr/bin/env python3
"""
Git Hook for Automatic Frontend Verification
Runs frontend integration tests before commits
"""

import sys
import subprocess
import os

def run_verification():
    """Run frontend verification script"""
    print("🔍 Running frontend integration verification...")
    
    try:
        result = subprocess.run([
            'python', 'scripts/verify_frontend_integration.py'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Frontend verification passed")
            return True
        else:
            print("❌ Frontend verification failed")
            print("Output:", result.stdout)
            print("Errors:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Frontend verification timed out")
        return False
    except Exception as e:
        print(f"❌ Error running verification: {e}")
        return False

def main():
    """Main hook execution"""
    print("=" * 50)
    print("Pre-commit Frontend Verification Hook")
    print("=" * 50)
    
    # Change to repository root
    repo_root = subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).decode().strip()
    os.chdir(repo_root)
    
    # Run verification
    if run_verification():
        print("🎉 All checks passed, proceeding with commit")
        sys.exit(0)
    else:
        print("🚫 Commit blocked due to frontend verification failures")
        print("💡 Fix the issues above or run 'python workflow.py verify' for details")
        sys.exit(1)

if __name__ == "__main__":
    main()