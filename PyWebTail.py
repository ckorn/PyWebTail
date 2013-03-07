#!/usr/bin/pyhon
# -*- coding: utf-8 -*- 

"""
PyWebTail.py
  Utility that creates a minimal HTTP web server that can be used to export 
  a log file tail. 
  It uses Python's BaseHTTPServer, removing the burden of installing and
  configuring a full web server for such a trivial purpose.
"""

import sys
import os
import argparse
from time import time, strftime, localtime
from SocketServer import ThreadingMixIn
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler


__author__ = "João Pinto"
__copyright__ = "Copyright 2013, João Pinto"
__credits__ = ["João Pinto"]
__license__ = "GPL-3"
__version__ = "1.0"
__maintainer__ = "João Pinto"
__email__ = "lamego.pinto@gmail.com"
__status__ = "Production"


def parse_args():
    """ Parse command line arguments """
    parser = argparse.ArgumentParser(description="Utility that creates a minimal HTTP web server that can be used to export a log file tail.")

    parser.add_argument("-n", "--lines K", 
                      action="store", type=int, dest="lines", default=10,
                      help="output the last K lines, instead of the last 10")    
    parser.add_argument("-l", "--listener-port", 
                      action="store", type=int, dest="port", required=True,
                      help="Specifies the HTTP listener port")
    parser.add_argument("log_file", help="the file for which the tail should be shown")
    return parser.parse_args()


def tail(f, lines=10, _block_size=512):
    """ Return tail of file """
    data = ''
    block_counter = -1   
    f.seek(0, os.SEEK_END)
    file_size = f.tell()
    lines_count = 0
    while lines_count < lines:
        try:
            f.seek(block_counter * _block_size, os.SEEK_END)
        except IOError:  # too small, or too many lines
            f.seek(0)
            data = f.read(file_size)
            return data.splitlines()
        tmp_data = f.read(_block_size)
        lines_count += tmp_data.count('\n')
        data = tmp_data + data
        block_counter -= 1
    return data.splitlines()[-lines:]
        
class TailHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()  
        html="""
<html><!--- refresh with a random url to avoid caching --->
<head><meta http-equiv="refresh" content="10;URL=/%s"></head>
<body>
<b>%s</b><br>
""" % (str(time()), strftime("%a, %d %b %Y %X %Z", localtime()))
        self.wfile.write(html)
        with open(self.server.tail_filename) as tail_file:
            tail_lines = tail(tail_file, self.server.tail_lines)            
            self.wfile.write('<br>'.join(tail_lines))
        self.wfile.write('</body></html>')            

class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass

def main():
    options = parse_args()
    tail_filename = options.log_file
    server = ThreadingHTTPServer( 
            ("0.0.0.0", options.port), TailHandler )
    server.tail_filename = tail_filename
    server.tail_lines = options.lines
    server.serve_forever()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print "Interrupted"
        
