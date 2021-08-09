import attr
import boto3
import typing

log = __import__('logging').getLogger(__name__)

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
        log.info(f'uploading object to s3://{self.bucket}/{path}')
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
        log.debug(f'object url={url}')
        return url

    def get_object(self, path, *, raise_if_not_found=True):
        try:
            response = self.client.get_object(
                Bucket=self.bucket,
                Key=path,
            )
        except self.client.exceptions.NoSuchKey:
            if raise_if_not_found:
                raise
            return None

        return response['Body'].read()
