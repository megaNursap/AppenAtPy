import sys
import os
path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(path.replace(os.path.basename(path), ''))