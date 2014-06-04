import vm
import iparser
import programm_counter
from time import clock
import json
from io_unit import plc_io, tcp
import io_handler



class SPS_IO(plc_io.BasicIO):
    def __init__(self, addr_offset, size_in, size_out):
        super(SPS_IO, self).__init__(addr_offset, size_in, size_out)

    def change(self, ad, val):
        pass

    def set(self, addr, b):
        pass

class CodeGen:
#Klasse die für die CodeGenerierung zuständig ist
#die Variable self.byte_code enthällt für jeden Dateinamen den passenden programmzähler inklusive ByteCode
    def __init__(self):
        self.byte_code = {}

    def generate_code(self, fname, vm_u, io):
    #erzeugt ByteCode
    #parameter name für die Datei
    #parameter vm_u ist die VM auf die gelinkt wird
        print("Bearbeite %s:" % fname)
        #Tokens erzeugen
        il = iparser.Parser(fname)
        #Programmcounter und Bytecode erzeugen
        byte_code = programm_counter.PC(il.code, il.tags, vm_u, fname, io)
        self.byte_code[fname] = byte_code
        #Dateien auf die Aufrufe sind werden ebenfalls Compiliert
        #falls noch nicht compiliert
        more = byte_code.ref_files
        for f in more:
            if not self.byte_codes.contains(f):
                self.generate_code(f, vm_u)

                
class Runtime:
#Runtime für die SPS
    def __init__(self):
        self.io_handler = io_handler.IOHandler()
        self.console = SPS_IO(0, 10, 10)
        self.cons = []
        #self.cons.append(tcp.TcpConClient(self.console, 'localhost', 5551))
        self.webserver = SPS_IO(20, 2, 2)
        #self.cons.append(tcp.TcpConClient(self.console, 'localhost', 5559))
        self.io_handler.add(self.console)
        self.io_handler.add(self.webserver)

    def load_parameter(self):
    #laden von Parametern
        with open('config.json', 'r') as f:
            self.conf = json.load(f)
        print(self.conf)
        self.fc = self.conf['main_file']
        self.max_time = self.conf['max_run_time']

    def init(self):
    #Erzeugt die VM generiert den Byte Code und PCs
        self.vm_u = vm.VM(self.conf['mem_size'], self.io_handler)
        gen = CodeGen()
        gen.generate_code(self.fc, self.vm_u, self.io_handler)
        self.code = gen.byte_code

    def run(self):
    #Lässt das SPS Programm laufen
    #@TODO:laufzeit überprüfung verbessern
    #      Abbruchs möglichkeit
        ret = (self.fc, '')
        stack = []
        used = ''
        t = clock()
        ht = 0
        print("Starte Programm ausführung")
        
        while True:
        #Endlose Programm ausführung
        #durch die Rückgaben werden die unterschiedlichen ProgrammCounter aufgerufen
            if ret == (self.fc, '') :
            #Mainloop
                #self.vm_u.update_memory()
                ret = self.code[self.fc].load()
                t2 = clock()
                ht = t2 - t
                if self.max_time < ht and self.max_time > 0:
                    print("Laufzeitüberschreitung")
                t = t2
            elif ret[1] == '' and ret[0] != '':
            #ein aufgerufener PC ist fertig
                used = stack.pop()
                ret = self.code[used].start()
            else:
            #ein neuer PC wird aufgerufen
                stack.append(ret[0])
                ret = self.code[ret[1]].load()

#Mainloop
if __name__ == "__main__":
    run_t = Runtime()
    run_t.load_parameter()
    run_t.init()
    run_t.run()
