#from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import http.server
import socketserver
import simplejson
import json
import random
import os



def jsonPPrint(filename):
    f = open(filename, 'r')
    data = json.loads(f.read())
    print(json.dumps(data, indent=4, sort_keys=True))


class S(http.server.BaseHTTPRequestHandler):
    '''Servidor HTTP'''

    def get_File(self, mime):
        self.send_response(200)
        self.send_header('Content-type', mime)
        self.end_headers()
        f = open(os.path.dirname(
            os.path.abspath(__file__)) + self.path, 'rb')
        self.wfile.write(f.read())
        f.close()

    def do_GET(self):
        '''Callback para GETs'''
        print(self.path)
        try:
            if(self.path.endswith('/')):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                f = open("myPag.html", "r", encoding="utf8")
                self.wfile.write(f.read().encode())
                f.close()

            elif(self.path.endswith('.jpg')):
                self.get_File('image/jpg')
                
        except FileNotFoundError:
            self.send_error(404, "File Not Found {}".format(self.path))

    def do_HEAD(self):
        self._set_headers()



def run(server_class=http.server.HTTPServer, handler_class=S, server='localhost', port=80):
    server_address = (server, port)
    httpd = server_class(server_address, handler_class)
    print('Server starting at ' + str(server_address[0]) + ':' + str(port))
    httpd.serve_forever()


if __name__ == "__main__":
    from sys import argv

if len(argv) == 3:
    run(server=argv[1], port=int(argv[2]))
    print(argv[1])
else:
    run()