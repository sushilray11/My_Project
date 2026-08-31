import os, sys

_DIR = "/Users/I325211/Local_Project/Project_Up"
_app_path = os.path.join(_DIR, "app.py")
if _DIR not in sys.path:
    sys.path.insert(0, _DIR)

exec(open(_app_path).read(), {"__file__": _app_path})
