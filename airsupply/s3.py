import attr
import boto3
import os.path
import typing

from .ipa import open_ipa
from .templates import DEFAULT_HTML, DEFAULT_MANIFEST, render_template

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

def push(
    ipa_path,
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
        prefix = os.path.splitext(os.path.basename(ipa_path))[0]

    s3 = S3(
        client=boto3.client('s3'),
        bucket=bucket,
        acl=acl,
        public=public,
        expires=expires,
    )

    image_url = None
    with open_ipa(ipa_path) as ipa:
        icon = ipa.find_best_icon()
        if icon is not None:
            with ipa.open_asset(icon.name) as fp:
                image_url = s3.put_object(f'{prefix}.png', fp, 'image/png')

    with open(ipa_path, 'rb') as fp:
        ipa_url = s3.put_object(f'{prefix}.ipa', fp, 'application/zip')

    manifest = render_template(DEFAULT_MANIFEST, context=dict(
        ipa=ipa,
        ipa_url=ipa_url,
        image_url=image_url,
    ))
    manifest_url = s3.put_object(
        f'{prefix}.plist',
        manifest.encode('utf8'),
        'text/xml',
    )

    html = render_template(DEFAULT_HTML, context=dict(
        ipa=ipa,
        image_url=image_url,
        manifest_url=manifest_url,
    ))
    url = s3.put_object(
        f'{prefix}.html',
        html.encode('utf8'),
        'text/html',
    )
    return url
