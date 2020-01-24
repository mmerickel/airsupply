import attr
from contextlib import contextmanager
import plistlib
import posixpath
import re
import typing
import zipfile

@attr.s(auto_attribs=True)
class Icon:
    size: int
    name: str

@attr.s(auto_attribs=True)
class IPA:
    zip: zipfile.ZipFile
    app_path: str

    id: str
    display_name: str
    short_version: str
    version: str
    minimum_os_version: str
    icons: typing.Dict[int, Icon]

    @contextmanager
    def open_asset(self, name):
        with self.zip.open(f'{self.app_path}/{name}') as fp:
            yield fp

    def find_best_icon(self, target_size=72):
        best_icon = best_dist = None
        for size, icon in self.icons.items():
            dist = abs(target_size - size)
            if best_dist is None or dist < best_dist:
                best_icon = icon
                best_dist = dist
        return best_icon

@contextmanager
def open_ipa(path):
    with open(path, 'rb') as fp:
        with zipfile.ZipFile(fp) as zip:
            app_path = get_app_path(zip)
            with zip.open(f'{app_path}/Info.plist') as plist_fp:
                plist = plistlib.load(plist_fp)
            meta = parse_metadata(plist, zip, app_path)
            ipa = IPA(
                zip=zip,
                app_path=app_path,
                **meta,
            )
            yield ipa

def get_app_path(zip):
    plist_re = re.compile(r'Payload/[^/]+\.app/Info\.plist')
    for path in zip.namelist():
        if plist_re.match(path):
            return posixpath.dirname(path)
    raise ValueError('unable to find Info.plist')

def parse_metadata(plist, zip, app_path):
    icons = {}
    icons.update(parse_icon_metadata(plist, zip, app_path, 'CFBundleIcons'))
    icons.update(parse_icon_metadata(plist, zip, app_path, 'CFBundleIcons~ipad'))

    return dict(
        id=plist['CFBundleIdentifier'],
        display_name=plist['CFBundleDisplayName'],
        short_version=plist['CFBundleShortVersionString'],
        version=plist['CFBundleVersion'],
        minimum_os_version=plist.get('MinimumOSVersion'),
        icons=icons,
    )

icon_re = re.compile(
    r'''
    (?P<w>\d+\.?\d*)
    x
    (?P<h>\d+\.?\d*)
    (?:
        @
        (?P<r>\d+)
    )?
    (?:~ipad)?
    \.png
    ''',
    re.VERBOSE,
)

def parse_icon_metadata(plist, zip, app_path, key):
    icons = {}
    files = (
        plist
        .get(key, {})
        .get('CFBundlePrimaryIcon', {})
        .get('CFBundleIconFiles', [])
    )
    for icon_prefix in files:
        for path in zip.namelist():
            if not path.startswith(f'{app_path}/{icon_prefix}'):
                continue
            name = posixpath.basename(path)
            m = icon_re.search(name)
            if not m:
                continue
            r = int(m.group('r') or 1)
            icon = Icon(
                size=int(float(m['w']) * r),
                name=name,
            )
            icons[icon.size] = icon
    return icons
