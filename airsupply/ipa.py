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
    filename: str
    zip: zipfile.ZipFile
    app_path: str

    id: str
    display_name: str
    short_version: str
    version: str
    platform: str
    minimum_os_version: str
    icons: typing.Dict[int, Icon]
    plist: typing.Dict[str, typing.Any]

    @contextmanager
    def open_asset(self, name):
        with self.zip.open(f'{self.app_path}/{name}') as fp:
            yield fp

    def find_best_icon(self, target_size=1024):
        best_icon = best_dist = None
        for size, icon in self.icons.items():
            dist = abs(target_size - size)
            if best_dist is None or dist < best_dist:
                best_icon = icon
                best_dist = dist
        return best_icon

def is_ipa(path):
    try:
        with open(path, 'rb') as fp:
            with zipfile.ZipFile(fp) as zip:
                get_app_path(zip)
                return True
    except Exception:
        return False

@contextmanager
def open_ipa(path):
    with open(path, 'rb') as fp:
        with zipfile.ZipFile(fp) as zip:
            app_path = get_app_path(zip)
            with zip.open(f'{app_path}/Info.plist') as plist_fp:
                plist = plistlib.load(plist_fp)
            meta = parse_metadata(plist, zip, app_path)
            ipa = IPA(
                filename=path,
                zip=zip,
                app_path=app_path,
                plist=plist,
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

    display_name = plist.get('CFBundleDisplayName')
    if display_name is None:
        display_name = plist.get('CFBundleName')
    if display_name is None:
        raise ValueError(
            'could not determine display name from CFBundleDisplayName or '
            'CFBundleName'
        )

    return dict(
        id=plist['CFBundleIdentifier'],
        display_name=display_name,
        short_version=plist['CFBundleShortVersionString'],
        version=plist['CFBundleVersion'],
        platform=plist['DTPlatformName'],
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
        x
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
