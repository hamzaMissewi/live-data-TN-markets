import importlib
packages = ['fastapi', 'uvicorn', 'sqlalchemy', 'pydantic', 'pydantic_settings', 'alembic']
for pkg in packages:
    try:
        mod = importlib.import_module(pkg)
        version = getattr(mod, '__version__', 'unknown')
        print(f'{pkg}: {version}')
    except ImportError:
        print(f'{pkg}: NOT INSTALLED')