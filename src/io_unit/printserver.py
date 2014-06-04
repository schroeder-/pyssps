import tcp
import plc_io
from time import sleep
import argparse



class PrintIO(plc_io.BasicIO):
    def __init__(self, addr_offset, size_in, size_out):
        super(PrintIO, self).__init__(addr_offset, size_in, size_out)

    def change(self, ad, val):
        print('[RECV] ADDR: %d = %d' % (ad, val))


    def set(self, addr, b):
        print('[SET] ADDR %d = %d' % (addr, b))





parser = argparse.ArgumentParser()
parser.add_argument("-osize", "--output_size", dest="osize", help="Ausgabe Speichergröße", type=int, default=10)
parser.add_argument("-isize", "--input_size", dest="isize", help="Eingabe Speichergröße", type=int, default=10)
parser.add_argument("-offset", "--address_offset", dest="offset", help="Adressen Offset", type=int, default=0) 
parser.add_argument("-p", "--port", dest="port", help="Server Port", type=int, default=5551)
args = parser.parse_args()


io = PrintIO(args.offset, args.isize, args.osize)
cl = tcp.TcpConServer(io, args.port)

if __name__ == "__main__":
	while True:
		s = input("Befehl eingeben")
		if s[0] == 'i' or s[0] == 'I':
			print(s.lstrip('Ii '), " = ",  int(cl[s.lstrip('Ii ')]))
		elif s[0] == 'o' or s[0] == 'O':
			s = s.lstrip('Oo ')
			s = s.split()
			if len(s) != 2:
				print("Nicht genug Argumente")
			else:
				s[int(s[0])] = int(s[1])
		elif s[0] == 'q':
			break;
		else:
			print("Unbekannter Befehl \n Ausgangswert setzten: o Addresse Wert \n Eingabewert lesen: i Addresse \n Verlassen: q")			
	print('Programm wurde beendet')

