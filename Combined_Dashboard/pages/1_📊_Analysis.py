import os, sys

_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "Analysis")
_app_path = os.path.join(_DIR, "app.py")
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

exec(open(_app_path, encoding="utf-8").read(), {"__file__": _app_path})
