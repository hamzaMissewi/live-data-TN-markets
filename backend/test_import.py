import sys
import os
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
sys.path.insert(0, backend_dir)

try:
    from app.main import app
    print("App imported successfully")
    print(f"Routes: {[r.path for r in app.routes[:10]]}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()