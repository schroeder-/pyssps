import memory
#@TODO Add all commands
class VM:

    def __init__(self, memory_size, io):
        self.io = io
        self.acc = 0
        self.b = 0
        self.mem = memory.memory(memory_size)
        self.stack = []
        self.hooks = []
        self.callf = ''
        self.exe_file = ''

    def set_exe_file(self, file):
        self.exe_file = file

    def called(self):
        return self.callf

    def lookup_bit(self, addr):
        return self.mem.get_bit(addr)

    def lookup_mem(self, addr):
        return self.mem[addr]

    def nop(self):
        pass

    def set_hook(self, name, hook):
        self.hooks[name] = hook
    #@TODO Sollte acc in blöcke übernommen werden bei bit functionen

    def begin_block(self, bit_func, calc_func = None, load_val = 0):
        self.stack.append((self.b, bit_func, calc_func, self.acc))
        self.acc = load_val
        self.b = None

    def end_block(self):
        b = self.b
        acc = self.acc
        self.b, bf, cf, self.acc = self.stack.pop()
        if bf != None:
            bf(b)
        elif cf != None:
            cf(acc)

    def add(self, op):
        self.acc = self.acc + op

    def add_block(self, op=0):
        self.start_block(None, self.add, op)

    def sub(self, op):
        self.acc = self.acc - op

    def sub_block(self, op=0):
        self.start_block(None, self.sub, op)

    #@TODO ADD RUNTIME ERR bei op = 0
    def div(self, op):
        self.acc = self.acc / op

    def div_block(self, op=0):
        self.start_block(None, self.div, op)

    def mul(self, op):
        self.acc = self.acc * op

    def mul_block(self, op=0):
        self.start_block(None, self.mul, op)

    def gt(self, op):
        self.b = self.acc > op

    def gt_block(self):
        self.start_block(None, self.gt, 0)

    def ge(self, op):
        self.b = self.acc >= op

    def ge_block(self):
        self.start_block(None, self.ge, 0)

    def eq(self, op):
        self.b = self.acc == op

    def eq_block(self):
        self.start_block(None, self.eq, 0)

    def ne(self, op):
        self.b = self.acc != op

    def ne_block(self):
        self.start_block(None, self.ne, 0)

    def le(self, op):
        self.b = self.acc <= op

    def le_block(self):
        self.start_block(None, self.le, 0)

    def lt(self, op):
        self.b = self.acc < op

    def lt_block(self):
        self.start_block(None, self.lt, 0)


    def store(self, addr, op):
        val = self.acc
        self._store(addr, val, op)


    def _store(self, addr, val, op):
        if op == 'M':
            self.mem[addr] = val
        elif op == 'O':
            self.io.mem[addr] = val

    def store_n(self, addr, op):
        val = self.acc
        self._store(addr, -val, op)

    def load(self, op):
        self.acc = op

    def load_n(self, op):
        self.load(-op)

    def set(self, addr, type_):
        if self.b:
            if type_ == 'M':
                self.mem.set_bit(addr)
            elif type_ == 'O':
                self.io.set_bit(addr, 'out')
            else:
                #@TODO add runtime error
                pass

    def reset(self, addr, type_):
        if self.b:
            if type_ == 'M':
                self.mem.reset_bit(addr)
            elif type_ == 'O':
                self.io.reset_bit(addr, 'out')
            else:
                #@TODO add runtime error
                pass

    def equalb(self, addr, op):
        if self.b:
            self.set(addr, op)
        else:
            self.reset(addr, op)

    def andf(self, op):
        if self.b == None:
            self.b = True
        if self.b:
            if op:
                self.b = True
            else:
                self.b = False

    def and_block(self):
        self.start_block(self.andf)

    def nand(self, op):
        if self.b == None:
            self.b = True
        if self.b:
            if not op:
                self.b = True
            else:
                self.b = False

    def nand_block(self):
        self.start_block(self.nand)

    def orf(self, op):
        if self.b == None:
            self.b = False
        if op:
            self.b = True

    def or_block(self):
        self.start_block(self.orf)

    def nor(self, op):
        if self.b == None:
            self.b = False
        if not op:
            self.b = True

    def nor_block(self):
        self.start_block(self.nor)

    def xor(self, op):
        if self.b == None:
            self.b = op
            return
        if self.b != op:
            self.b = True
        else:
            self.b = False

    def xor_block(self):
        self.start_block(self.xor)

    def dprint(self, op):
        print('[*D*]', op)

    def dprintb(self, op):
        self.dprint(op)

    def jmp(self, tag):
        self.exe_file.jmp(tag)

    def jmpc(self, tag):
        if self.b:
            self.jmp(tag)

    def jmpcn(self, tag):
        if not self.b:
            self.jmp(tag)

    def ret(self):
        self.exe_file.ret()
        self.callf = ''
        return True

    def retc(self):
        if self.b:
            self.ret()

    def retcn(self):
        if not self.b:
            self.ret()

    def call(self, fname):
        self.callf = fname
        return True

    def callc(self, fname):
        if self.b:
            self.call(fname)

    def callcn(self, fname):
        if not self.b:
            self.call(fname)

    def hook(self, name):
        self.hooks[name](self)
