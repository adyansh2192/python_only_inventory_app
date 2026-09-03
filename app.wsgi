import os
import sys

sys.path.insert(0, "/var/www/python-inventory")

for raw_line in open("/etc/python-inventory.env", encoding="utf-8"):
    line = raw_line.strip()
    if line and not line.startswith("#") and "=" in line:
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip())

from app import app as application
