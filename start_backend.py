import sys
import os
import subprocess
import time
import signal

backend_dir = r'e:\projects\MONEY GENERATOR APPS\live-data-dashboard-adsense\backend'
venv_python = r'e:\projects\MONEY GENERATOR APPS\live-data-dashboard-adsense\.venv\Scripts\python.exe'

os.chdir(backend_dir)

# Set environment variables
env = os.environ.copy()
env['PYTHONPATH'] = backend_dir
env['API_HOST'] = '0.0.0.0'
env['API_PORT'] = '8000'
env['DEBUG'] = 'True'
env['ENVIRONMENT'] = 'development'

# Start uvicorn in background
print("Starting FastAPI backend on http://0.0.0.0:8000...")
print("Backend directory:", backend_dir)
print("")

proc = subprocess.Popen(
    [venv_python, 'main.py'],
    env=env,
    cwd=backend_dir,
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True,
    bufsize=1,
)

# Print output for 10 seconds
try:
    for i in range(100):
        line = proc.stdout.readline()
        if line:
            print(line.rstrip())
        if proc.poll() is not None:
            print("Process exited with code:", proc.returncode)
            break
        time.sleep(0.1)
except KeyboardInterrupt:
    proc.terminate()
    proc.wait()