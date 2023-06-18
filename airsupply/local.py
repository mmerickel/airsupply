import attr
import os
from urllib.parse import urljoin

log = __import__('logging').getLogger(__name__)

@attr.s(auto_attribs=True)
class LocalTarget:
    url: str
    root_dir: str

    def put_object(self, path, data, content_type):
        local_path = os.path.join(self.root_dir, path)
        local_dir = os.path.dirname(local_path)

        os.makedirs(local_dir, exist_ok=True)

        log.info(f'uploading object to {path}')
        with open(local_path, 'wb') as fp:
            if not isinstance(data, bytes):
                data = data.read()
            fp.write(data)

        return self.get_url(path)

    def get_url(self, path):
        return urljoin(self.url, path)

    def get_object(self, path, *, raise_if_not_found=True):
        path = os.path.join(self.root_dir, path)
        try:
            with open(path, 'rb') as fp:
                return fp.read()
        except FileNotFoundError:
            if raise_if_not_found:
                raise
            return None
