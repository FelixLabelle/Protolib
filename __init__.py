# __init__.py in the root directory of your project

import sys
import os

# Add the parent directory to the Python module search path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
