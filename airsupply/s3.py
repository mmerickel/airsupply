import attr
import boto3
import importlib.resources
import mimetypes
import os.path
import typing

from .apk import is_apk, open_apk
from .ipa import is_ipa, open_ipa
from .templates import render_template

def push(
    package_path,
    bucket,
    *,
    acl=None,
    public=False,
    expires=86400,
    prefix=None,
):
    if not acl:
        acl = 'public-read' if public else 'private'

    if not prefix:
        prefix = os.path.splitext(os.path.basename(package_path))[0]

    s3 = S3(
        client=boto3.client('s3'),
        bucket=bucket,
        acl=acl,
        public=public,
        expires=expires,
    )

    if is_ipa(package_path):
        with open_ipa(package_path) as ipa:
            ctx = push_ipa(ipa, s3, prefix)

    elif is_apk(package_path):
        with open_apk(package_path) as apk:
            ctx = push_apk(apk, s3, prefix)

    else:
        raise ValueError('unrecognized package')

    html_tmpl = importlib.resources.read_text(__package__, 'html.jinja2')
    html = render_template(html_tmpl, context=ctx)
    url = s3.put_object(
        f'{prefix}.html',
        html.encode('utf8'),
        'text/html',
    )
    return url

@attr.s(auto_attribs=True)
class S3:
    client: typing.Any
    bucket: str
    acl: str
    public: bool
    expires: int

    def put_object(self, path, data, content_type):
        self.client.put_object(
            Bucket=self.bucket,
            Key=path,
            Body=data,
            ACL=self.acl,
            ContentType=content_type,
        )

        url = self.client.generate_presigned_url(
            'get_object',
            Params=dict(
                Bucket=self.bucket,
                Key=path,
            ),
            ExpiresIn=self.expires,
        )
        if self.public:
            i = url.index('?')
            url = url[:i]
        return url

def push_ipa(ipa, s3, prefix):
    image_url = None
    icon = ipa.find_best_icon(512)
    if icon is not None:
        with ipa.open_asset(icon.name) as fp:
            image_url = s3.put_object(f'{prefix}.png', fp, 'image/png')

    with open(ipa.filename, 'rb') as fp:
        ipa_url = s3.put_object(f'{prefix}.ipa', fp, 'application/zip')

    manifest_tmpl = importlib.resources.read_text(
        __package__, 'ipa_manifest.jinja2')
    manifest = render_template(manifest_tmpl, context=dict(
        ipa=ipa,
        ipa_url=ipa_url,
        image_url=image_url,
    ))
    manifest_url = s3.put_object(
        f'{prefix}.plist',
        manifest.encode('utf8'),
        'text/xml',
    )

    return dict(
        package_type='ipa',
        app_id=ipa.id,
        display_name=ipa.display_name,
        version_name=ipa.short_version,
        version_code=ipa.version,
        minimum_os_version=ipa.minimum_os_version,
        image_url=image_url,
        ipa_url=ipa_url,
        manifest_url=manifest_url,
    )

def push_apk(apk, s3, prefix):
    image_url = None
    icon = apk.get_app_icon(512)
    if icon and not icon.endswith('.xml'):
        image_data = apk.get_file(icon)
        image_ext = os.path.splitext(icon)[1]
        image_type, _ = mimetypes.guess_type(icon, strict=False)
        image_url = s3.put_object(f'{prefix}{image_ext}', image_data, image_type)

    with open(apk.filename, 'rb') as fp:
        apk_url = s3.put_object(
            f'{prefix}.apk', fp, 'application/vnd.android.package-archive')

    return dict(
        package_type='apk',
        app_id=apk.package,
        display_name=apk.application,
        version_name=apk.version_name,
        version_code=apk.version_code,
        image_url=image_url,
        apk_url=apk_url,
    )
