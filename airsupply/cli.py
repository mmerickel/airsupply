import click

@click.group()
def main():
    pass

@click.command('s3:push')
@click.option('-b', '--bucket', required=True)
@click.option('-p', '--public', default=False, is_flag=True)
@click.option('--acl')
@click.option('--prefix')
@click.option('--expires', type=int, default=86400)
@click.argument('ipa_file')
def s3(ipa_file, bucket, acl, prefix, public, expires):
    from .s3 import push

    url = push(
        ipa_path=ipa_file,
        bucket=bucket,
        acl=acl,
        prefix=prefix,
        public=public,
        expires=expires,
    )
    click.echo(url)

main.add_command(s3)
