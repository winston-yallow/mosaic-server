import click
import logging
import server


HOST = '0.0.0.0'
PORT = 8765
LOGFORMAT = '[%(levelname)s] %(message)s'


loglevels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
loglevel_options = click.Choice(loglevels, case_sensitive=False)


@click.command()
@click.option(
    '--loglevel',
    type=loglevel_options,
    default=loglevels[2],
    help="Filter which log messages will be printed"
)
@click.option('--cert', type=str, help='SSL Cert')
@click.option('--key', type=str, help='SSL Key')
def cli(loglevel, cert, key):
    logging.basicConfig(
        level=logging.getLevelName(loglevel),
        format=LOGFORMAT
    )
    server.run(HOST, PORT, cert, key)


if __name__ == '__main__':
    cli()
