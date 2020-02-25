#!/usr/bin/env python3
#
# receiver.py
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
from srudp import SRUDPServer

logger = logging.getLogger(__name__)
def check_arg(args=None):
    parser = ArgumentParser(description='Simplest Reliable User Datagram Protocol (srudp - sender 1.0)')
    parser.add_argument('-H', '--bind-address', help='Bind receiver to address', default='0.0.0.0')
    parser.add_argument('-p', '--port', required=True,
                                        type=int,
                                        choices=range(10001, 11000),
                                        metavar="[10001-11000]",
                                        help='port of the receiver (10001-11000)')
    parser.add_argument('-v', '--verbose', action='count', default=0)
    results = parser.parse_args(args)

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG if results.verbose > 0 else logging.INFO)

    return (results.bind_address,
            results.port)



if __name__ == '__main__':
    bind_address, port = check_arg(sys.argv[1:])
    logger.debug('Level debug is enabled.')
    logger.info('Level info is enabled.')
    logger.warning('Level warning is enabled.')
    logger.error('Level error is enabled.')
    logger.critical('Level critical is enabled.')
    logger.info(f'Bind {bind_address} and port {port}')
    server = SRUDPServer(bind_address, port)

    for data in server.receive():
        print ("RECV: ", data)