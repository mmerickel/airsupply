import click
import logging

@click.group()
@click.option('-v', '--verbose', count=True)
@click.version_option()
def main(verbose=0):
    if verbose < 1:
        level = logging.WARN
    elif verbose == 1:
        level = logging.INFO
    elif verbose >= 2:
        level = logging.DEBUG
    logging.basicConfig(level=level)

@click.command('s3:push')
@click.option('-b', '--bucket', required=True)
@click.option('-p', '--public', default=False, is_flag=True)
@click.option('--acl')
@click.option('--prefix')
@click.option('--expires', type=int, default=86400)
@click.argument('package')
def s3(package, bucket, acl, prefix, public, expires):
    from .s3 import push

    url = push(
        package_path=package,
        bucket=bucket,
        acl=acl,
        prefix=prefix,
        public=public,
        expires=expires,
    )
    click.echo(url)

main.add_command(s3)
