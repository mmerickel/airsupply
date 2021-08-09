import click
import logging
import os

DEFAULT_LOG_FORMAT = '%(levelname)s: %(message)s'
VERBOSE_LOG_FORMAT = '%(asctime)s %(levelname)s %(name)s: %(message)s'

@click.group()
@click.option('-v', '--verbose', count=True)
@click.version_option()
def main(verbose=0):
    level = logging.INFO
    format = DEFAULT_LOG_FORMAT
    if verbose > 0:
        level = logging.DEBUG
        format = VERBOSE_LOG_FORMAT
    logging.basicConfig(format=format, level=level)

@click.command('s3:push')
@click.option('-b', '--bucket', required=True)
@click.option('-p', '--public', is_flag=True, default=False)
@click.option('--acl')
@click.option('--prefix')
@click.option('--expires', type=int, default=86400)
@click.option('--overwrite-index', is_flag=True, default=False)
@click.argument('packages', nargs=-1, required=True)
def s3_push(packages, bucket, acl, prefix, public, expires, overwrite_index):
    from .push import push
    from .s3 import S3Target

    if not acl:
        acl = 'public-read' if public else 'private'

    target = S3Target(
        bucket=bucket,
        acl=acl,
        public=public,
        expires=expires,
    )

    url = push(target, packages, prefix=prefix, overwrite_index=overwrite_index)
    click.echo(url)

@click.command('local:push')
@click.option('--url', required=True)
@click.option('--prefix')
@click.option('--overwrite-index', is_flag=True, default=False)
@click.argument('packages', nargs=-1, required=True)
def local_push(packages, url, prefix, overwrite_index):
    from .local import LocalTarget
    from .push import push

    # it's surprising when the final segment is chopped off by urljoin
    # so ensure there's always a trailing slash
    if not url.endswith('/'):
        url += '/'

    target = LocalTarget(
        url=url,
        root_dir=os.getcwd(),
    )

    url = push(target, packages, prefix=prefix, overwrite_index=overwrite_index)
    click.echo(url)

main.add_command(s3_push)
main.add_command(local_push)
