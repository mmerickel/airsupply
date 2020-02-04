import attr
import boto3
import typing

@attr.s(auto_attribs=True)
class S3Target:
    bucket: str
    acl: str
    public: bool
    expires: int
    client: typing.Any = None

    def __attrs_post_init__(self):
        if self.client is None:
            self.client = boto3.client('s3')

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
