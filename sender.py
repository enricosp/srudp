#!/usr/bin/env python3
#
# sender.py
#
# Simplest Reliable User Datagram Protocol : https://github.com/enricosp/srudp
#
# By Enrico Spinetta
# License: MIT
#   See https://github.com/enricosp/srudp/blob/master/LICENSE
#
import sys
import socket
import ipaddress
import logging
from argparse import ArgumentParser
from srudp import SRUDPClient

logger = logging.getLogger(__name__)

def check_arg(args=None):
    parser = ArgumentParser(description='Simplest Reliable User Datagram Protocol (srudp - sender 1.0)')
    parser.add_argument('-H', '--host', help='host of the receiver', required='True')
    parser.add_argument('-p', '--port', type=int,
                                        choices=range(10001, 11000),
                                        metavar="[10001-11000]",
                                        help='port of the receiver (10001-11000)  Default is 100001.', default=10001)
    parser.add_argument('-n', '--number-of-msg', required=True, type=int, help='number of messages to send to receiver. (min 1)')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    results = parser.parse_args(args)

    if results.number_of_msg < 1:
        parser.error('argument -n/--number-of-msg minimal is 1')
        parser.print_help()
        exit(1)

    try:
        host = socket.gethostbyname(results.host)
        ipaddress.ip_address(host)
    except socket.error:
        parser.error('argument -H/--host [{}] is not valid.'.format(results.host))
        parser.print_help()
        exit(1)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG if results.verbose > 0 else logging.INFO)


    return (results.host,
            results.port,
            results.number_of_msg)

if __name__ == '__main__':
    host, port, number_of_msg = check_arg(sys.argv[1:])
    logger.debug('Level debug is enabled.')
    logger.info('Level info is enabled.')
    logger.warning('Level warning is enabled.')
    logger.error('Level error is enabled.')
    logger.critical('Level critical is enabled.')
    logger.info(f'{number_of_msg} messages to transmit to {host}:{port}')

    client = SRUDPClient(host, port)

    # Tenta pigar 4x no server para verificar se o mesmo está on-line
    if not client.ping(4, data=b'data-ping'):
        logger.critical(f"Fail ping to {host}:{port} check receiver is up on {port}")
        exit(2)

    data = [f"MSG Number {n+1}" for n in range(0, number_of_msg)]
    client.send(data)