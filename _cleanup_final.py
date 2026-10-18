import os
files = [
    r'e:\projects\MONEY GENERATOR APPS\live-data-dashboard-adsense\check_deps.py',
    r'e:\projects\MONEY GENERATOR APPS\live-data-dashboard-adsense\test_import_app.py',
    r'e:\projects\MONEY GENERATOR APPS\live-data-dashboard-adsense\launch_server.py',
    r'e:\projects\MONEY GENERATOR APPS\live-data-dashboard-adsense\install_deps.py',
    r'e:\projects\MONEY GENERATOR APPS\live-data-dashboard-adsense\check_and_run.py',
    r'e:\projects\MONEY GENERATOR APPS\live-data-dashboard-adsense\check_app.py',
]
for f in files:
    try:
        os.remove(f)
        print(f'Removed: {f}')
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f'Error removing {f}: {e}')
print('Cleanup complete')