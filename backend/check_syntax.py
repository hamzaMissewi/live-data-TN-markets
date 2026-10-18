import py_compile
files = [
    r'e:\projects\MONEY GENERATOR APPS\live-data-dashboard-adsense\backend\app\main.py',
    r'e:\projects\MONEY GENERATOR APPS\live-data-dashboard-adsense\backend\app\api\v1\news.py',
    r'e:\projects\MONEY GENERATOR APPS\live-data-dashboard-adsense\backend\app\schemas\news.py',
]
for f in files:
    py_compile.compile(f, doraise=True)
    print(f'OK: {f}')
print('All syntax checks passed')