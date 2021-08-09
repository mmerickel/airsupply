import attr
import os
from urllib.parse import urljoin

log = __import__('logging').getLogger(__name__)

@attr.s(auto_attribs=True)
class LocalTarget:
    url: str
    root_dir: str

    def put_object(self, path, data, content_type):
        url = urljoin(self.url, path)

        path = os.path.join(self.root_dir, path)
        root_dir = os.path.dirname(path)

        os.makedirs(root_dir, exist_ok=True)

        log.info(f'uploading object to {path}')
        with open(path, 'wb') as fp:
            if not isinstance(data, bytes):
                data = data.read()
            fp.write(data)

        return url

    def get_object(self, path, *, raise_if_not_found=True):
        path = os.path.join(self.root_dir, path)
        try:
            with open(path, 'rb') as fp:
                return fp.read()
        except FileNotFoundError:
            if raise_if_not_found:
                raise
            return None
