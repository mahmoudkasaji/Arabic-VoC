
# Import models from the root models.py file
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

try:
    from models import User, OAuth, Feedback
    __all__ = ['User', 'OAuth', 'Feedback']
except ImportError:
    # Fallback if models.py doesn't exist or has issues
    print("Warning: Could not import models from models.py")
    __all__ = []
