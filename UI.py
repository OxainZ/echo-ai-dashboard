import sys
import os

# Change to the echo directory so relative imports work
echo_dir = os.path.join(os.path.dirname(__file__), 'echo')
os.chdir(echo_dir)
sys.path.insert(0, echo_dir)

# Now import and run the main app
import app_streamlit
