import click
import logging
import os

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
@click.argument('packages', nargs=-1, required=True)
def s3_push(packages, bucket, acl, prefix, public, expires):
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

    url = push(target, packages, prefix=prefix)
    click.echo(url)

@click.command('local:push')
@click.option('--url', required=True)
@click.option('--prefix')
@click.argument('packages', nargs=-1, required=True)
def local_push(packages, url, prefix):
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

    url = push(target, packages, prefix=prefix)
    click.echo(url)

main.add_command(s3_push)
main.add_command(local_push)
