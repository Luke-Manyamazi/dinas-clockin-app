import subprocess
import webbrowser
import sys
import time
import os

# Make sure we are in the project directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Start the Flask app
process = subprocess.Popen([sys.executable, "main.py"])

# Wait a few seconds for the Flask server to start
time.sleep(3)

# Open the default browser to the scan page
webbrowser.open("http://localhost:5002/scan")

# Keep script running until the Flask server stops
try:
    process.wait()
except KeyboardInterrupt:
    process.terminate()
