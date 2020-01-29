from contextlib import contextmanager
from pyaxmlparser import APK
import zipfile

@contextmanager
def open_apk(path):
    apk = APK(path)
    yield apk

def is_apk(path):
    try:
        with open(path, 'rb') as fp:
            with zipfile.ZipFile(fp) as zip:
                return 'AndroidManifest.xml' in zip.namelist()
    except Exception:
        return False
