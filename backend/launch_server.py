import subprocess
import sys
import time
import os

backend_dir = r'e:\projects\MONEY GENERATOR APPS\live-data-dashboard-adsense\backend'
script_path = r'e:\projects\MONEY GENERATOR APPS\live-data-dashboard-adsense\start_server.py'

# Start server in background
proc = subprocess.Popen(
    [sys.executable, script_path],
    cwd=backend_dir,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    env={**os.environ, 'PYTHONPATH': backend_dir},
)

# Wait a bit for server to start
time.sleep(5)

# Check if process is still running
if proc.poll() is None:
    print("Server is running (PID:", proc.pid, ")")
else:
    print("Server exited with code:", proc.returncode)
    stdout, stderr = proc.communicate()
    print("STDOUT:", stdout.decode() if stdout else "none")
    print("STDERR:", stderr.decode() if stderr else "none")