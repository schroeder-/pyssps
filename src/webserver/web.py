from tornado import websocket, web, ioloop
import sys
sys.path.append('../io_unit')
import tcp
import plc_io

cl = []
con = None
io = None

class WebIO(plc_io.BasicIO):
    def change(self, ad, val):
        print('Change ', ad, val)
        for c in cl:
            c.write_message('I' + ' ' + str(ad) + ' ' + str(val))

    def set(self, addr, b):
        print('Set ', addr, b)
        for c in cl:
            c.write_message('O' + ' ' + str(addr) + ' ' + str(b))

class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("app.html")

class SocketHandler(websocket.WebSocketHandler):

    def open(self):
        print('Websock connected')
        if self not in cl:
            cl.append(self)
        i,o = io.flush()
        for ad, v in i:
            self.write_message('I' + ' ' + str(ad) + ' ' + str(v))
        for ad, v in o:
            self.write_message('O' + ' ' + str(ad) + ' ' + str(v))


    def on_message(self, message):
        print(message)
        data = message.split(' ')
        if data[0] == 'b':
            if data[2] == "0":
                io.reset_bit(data[1])
            else:
                io.set_bit(data[1])
        else:
            io[int(data[1])] = int(data[2])

    def on_close(self):
        if self in cl:
            cl.remove(self)

app = web.Application([
    (r'/', IndexHandler),
    (r'/ws', SocketHandler),
    (r'/(favicon.ico)', web.StaticFileHandler, {'path': '../'}),
    (r"/css/(.*)", web.StaticFileHandler, {'path': 'static/css'}),
    (r'/js/(.*)', web.StaticFileHandler, {'path': 'static/js'}),
    (r'/images/(.*)', web.StaticFileHandler, {'path': 'static/images'})
], debug=True)

if __name__ == '__main__':
    io = WebIO(0, 2, 2)
    con = tcp.TcpConServer(io, 5559)
    app.listen(8888)
    ioloop.IOLoop.instance().start()
