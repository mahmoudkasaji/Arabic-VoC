
# Import all models from the root models.py file
import sys
import os

# Add the parent directory to the path to import from root models.py
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Import all models from root models.py
try:
    from models import User, OAuth, Feedback
    __all__ = ['User', 'OAuth', 'Feedback']
except ImportError as e:
    print(f"Warning: Could not import models from models.py: {e}")
    # Define empty classes as fallback
    class User:
        pass
    class OAuth:
        pass
    class Feedback:
        pass
    __all__ = ['User', 'OAuth', 'Feedback']
