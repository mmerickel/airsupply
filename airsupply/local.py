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
