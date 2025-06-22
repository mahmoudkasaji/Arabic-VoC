"""
Main entry point for Flask Arabic Voice of Customer Platform
"""

from app import app



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)