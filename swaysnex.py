#!/usr/bin/env python

"""
Smart split and execute command in Sway.

SPDX-License-Identifier: MIT
Copyright (C) 2022 Artem Senichev <artemsen@gmail.com>
"""

import os
import json
import socket
import struct
import argparse


class Sway:
    """ Sway IPC. """

    HEADER_MAGIC = b'i3-ipc'
    HEADER_FORMAT = '<6sII'

    IPC_COMMAND = 0
    IPC_SUBSCRIBE = 2
    IPC_GET_TREE = 4

    SPLIT_HORIZONTAL = True
    SPLIT_VERTICAL = False

    def __init__(self):
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.connect(os.getenv('SWAYSOCK'))

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sock.close()

    def message(self, message_type, payload=None):
        """ Exchange messages with Sway. """
        # send request
        payload_size = len(payload) if payload else 0
        request = struct.pack(Sway.HEADER_FORMAT,
                              Sway.HEADER_MAGIC,
                              payload_size,
                              message_type)
        self.sock.send(request)
        if payload_size:
            self.sock.send(payload)
        # read response
        response = self.sock.recv(struct.calcsize(Sway.HEADER_FORMAT))
        (_, payload_size, _) = struct.unpack(Sway.HEADER_FORMAT, response)
        payload = self.sock.recv(payload_size)
        return json.loads(payload)

    def window_size(self):
        """ Get size of the current window. """
        tree = self.message(Sway.IPC_GET_TREE)
        current = Sway._find_current(tree)
        if current and 'rect' in current:
            rect = current['rect']
            width = rect.get('width', 0)
            height = rect.get('height', 0)
            return (width, height)
        return (0, 0)

    @staticmethod
    def _find_current(tree):
        """ Searching for current window. """
        if 'focused' in tree and tree['focused']:
            return tree
        if 'nodes' in tree:
            for node in tree['nodes']:
                node = Sway._find_current(node)
                if node:
                    return node
        return None

    def split_and_exec(self, split_mode, command):
        """ Split window and execute command. """
        cmd = ''
        if split_mode is not None:
            cmd += 'split '
            if split_mode == Sway.SPLIT_HORIZONTAL:
                cmd += 'horizontal;'
            else:
                cmd += 'vertical;'
        if command:
            cmd += 'exec \''
            for arg in command:
                if arg.find(' ') < 0:
                    cmd += arg
                else:
                    cmd += '"' + arg + '"'
                cmd += ' '
            cmd += '\''
        response = self.message(Sway.IPC_COMMAND, cmd.encode('utf-8'))
        for status in response:
            if not status['success']:
                raise Exception('IPC error')


def main():
    """Entry point."""
    parser = argparse.ArgumentParser(description='Smart split and execute.')
    parser.add_argument('-r', '--reverse', action='store_true',
                        help='reverse split logic')
    parser.add_argument('command', nargs=argparse.REMAINDER,
                        help='command to execute')
    args = parser.parse_args()
    with Sway() as sway:
        split_mode = None
        (width, height) = sway.window_size()
        if width != 0 and height != 0:
            if width < height:
                split_mode = Sway.SPLIT_VERTICAL
            else:
                split_mode = Sway.SPLIT_HORIZONTAL
            if args.reverse:
                split_mode = not split_mode
        sway.split_and_exec(split_mode, args.command)


if __name__ == '__main__':
    main()
