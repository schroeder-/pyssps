import byte_compiler
from err import GenError

class PC:
#klasse die den Programmz�hler abbildet
#Erzeugt aus den gewonnen Tokens ByteCode �ber den Bytecode compiler
    def __init__(self, code, tags, vm, name, io):
    #Parameter:
    #   code: Tokens vom Parser
    #   tags: gewonnene Sprungmarken vom Parser
    #   vm: die Ziel VM
    #   io: Objekt das die IOs handelt
        self.commands = {}
        self.vm = vm
        self.name = name
        self._io = io
        self.pc = -1
        self.stop = False
        #Erzeugt Bytecode
        byte_code = byte_compiler.Compiler(code, tags, vm)
        self.ref_files = byte_code.ref_files
        self.ins = byte_code.ins
        #for i in self.ins:
        #    print(i)



    def exec_ins(self):
    #f�hrt einen Befehl aus
        func, op, t = self.ins[self.pc]
        #Anhand der Parameterl�nge und des mit gelieferten types t 
        #wird die Funktion func von der vm aufgerufen mit 
        #den gewandelten Argumenten op
        if len(op) == 0:
            func()
        elif len(op) == 1:
            if t == byte_compiler.OP_INT:
                func(int(op[0]))
            elif t == byte_compiler.OP_STRING:
                func(op[0])
            elif t == byte_compiler.OP_BOOL:
                if op[0] in ['0', 'FALSE', 'false']:
                    func(False)
                else:
                    func(True)
        else:
            erg = False
            if t == byte_compiler.OP_BIT:
                if op[0] == 'M':
                    v = self.vm.lookup_bit(op[1])
                elif op[0] == 'I':
                    v = self._io.lookup_bit(op[1], 'i')
                elif op[0] == 'O':
                    v = self._io.lookup_bit(op[1], 'o')
                erg = func(v)
            elif t == byte_compiler.OP_MEM:
                if op[0] == 'M':
                    v = self.vm.lookup_mem(op[1])
                elif op[1] == 'I':
                    v = self._io.lookup_mem(op[1], 'i')
                elif op[1] == 'O':
                    v = self._io.lookup_mem(op[1], 'o')
                erg = func(v)
            elif t == byte_compiler.OP_MEM_ADDR:
                v = (int(op[1]), op[0])
                func(v[0], v[1])
            elif t == byte_compiler.OP_BIT_ADDR:
                v = (op[1], op[0])
                func(v[0], v[1])
            if erg == True:
                self.stop = True

    def startet(self):
    #PC ist nocht nicht fertig bzw. wurde w�hrend der ausf�hrung angehalten
        if self.pc > -1:
            return True
        return False


    def next(self):
    #pr�ft das n�chste vorgehen
        if self.stop:
            return False
        self.pc += 1
        if self.pc < len(self.ins) - 1:
            return True
        return False

    def start(self):
    #startet die ausf�hrung 
        self.vm.set_exe_file(self.name)
        while self.next():
            self.exec_ins()
        if self.stop:
            return ('', '')
        return (self.name, self.vm.called())

    def load(self):
    #der PC wird resetet
    #und der Bytecode ausgef�hrt
        self.pc = -1
        return self.start()

    def jmp(self, tag):
    #sprung an die Adresse
        self.pc = self.tags[tag] - 1

    def ret(self):
    #Return anweisung wurde ausgef�hrt
        self.stop = True
