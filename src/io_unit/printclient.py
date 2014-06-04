import tcp
import plc_io

class PrintIO(plc_io.BasicIO):
    def __init__(self, addr_offset, size_in, size_out):
        super(PrintIO, self).__init__(addr_offset, size_in, size_out)

    def change(self, ad, val):
        print('[RECV] ADDR: %d = %d' % (ad, val))

    def set(self, addr, b):
        print('[SET] ADDR %d = %d' % (addr, b))





io = PrintIO(0, 10, 10)
cl = tcp.TcpConClient(io, 'localhost', 5551)

while True:
    data = input()
    print(data)
    io[1] = 10

