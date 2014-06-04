from err import GenError
ARG_BIT_VAL = 1
ARG_CALL = 2
ARG_MEM_BIT = 3
ARG_MEM_VAL = 4
ARG_NONE = 5
ARG_TAG = 6
ARG_VALUE = 7
ARG_STRING = 8

OP_BIT = 0
OP_MEM = 1
OP_MEM_ADDR = 2
OP_BOOL = 3
OP_STRING = 4
OP_INT = 5
OP_NONE = 6
OP_BIT_ADDR = 7

#@TODO Check vm memory
class Compiler(GenError):
#Erzeugt aus dennen vom Parser gelieferten Daten einen Bytecode
    def __init__(self, code ,tags, vm):
        GenError()
        self.err = []
        self.ins = []
        self.link = []
        self.code = code
        self.tags = tags
        self.vm = vm
        self.calls = []
        self.init_func_links()
        self.compile()
        self.ref_files = set(self.link)

    def compile(self):
    #Erzeugt Bytecode
        cnt = 1
        block_cnt = 0
        for ins in self.code:
            func = None
            ops = []
            if ins != '':
                tokens = ins.split(' ')
                opcode = tokens[0].upper()
                tmp = None
                ot = None
                try:
                    #print(tokens)
                    #print(opcode)
                    #erhält befehls information
                    tmp = self.ins_list[opcode]
                    func = tmp[0]
                    if len(tokens) == 0:
                        tokens.append('')
                    err, ot = self.check_arg(tmp[1], tokens[1:])
                    if err != '':
                        self.add_err(err + ' in Zeile %d' % cnt)
                    ops = tokens[1:]
                    assert(ot != None)
                except KeyError:
                    self.add_err("Unbekanter Befehl %s in Zeile %d"
                                        %(opcode, cnt))
                self.ins.append((func, ops, ot))
                block_cnt = block_cnt + tmp[2]
            cnt = cnt + 1
        if block_cnt < 0:
            self.add_err("Nicht abgeschlossener Blöck")
        elif block_cnt > 0:
            self.add_err("Nicht geöffnete Blöcke")
        self.check_err()

    def check_arg(self, arg_type, arg):
    #Überprüfung ob die Argumente zum Befehl passen
        result = ''
        otype = None
        if arg_type == ARG_BIT_VAL:
            if len(arg) not in [1, 2]:
                result = "Keine Bit Addresse oder Bit Wert"
            elif len(arg) == 1:
                if arg[0] not in ['0', '1', 'TRUE', 'FALSE', 'false', 'true']:
                    result = "Wert ist kein Bit Wert"
                otype = OP_BOOL
            elif len(arg) == 2:
                if arg[0].upper() not in ["M", "I", "O"] or '.' not in arg[1]:
                    #@TODO regulärer ausdruck
                    result = "Keine Bit Addresse"
                otype = OP_BIT
        elif arg_type == ARG_CALL:
            if len(arg) < 1:
                result = "Keine Aufruf angeben"
            elif len(arg) > 1:
                result = "Zu viele Parameter"
            else:
                self.links.append(arg[0])
            otype = OP_STRING
        elif arg_type == ARG_MEM_BIT:
            if len(arg) != 2:
                result = "Keine Bit Addresse"
            elif arg[0].upper() not in ['M', 'I', 'O']:
                result = "Keine Bit Addresse"
            elif not '.' in arg[1]:
                #@TODO add reqular expression for better check
                result = "Keine Bit Addresse"
            otype = OP_BIT_ADDR
        elif arg_type == ARG_MEM_VAL:
            if len(arg) != 2:
                result = "Keine Speicher Addresse"
            elif arg[0].upper() not in ['M', 'I', 'O']:
                result = "Keine Speicher Addresse"
            elif not arg[1].isdigit():
                result = "Keine Speicher Addresse"
            otype = OP_MEM_ADDR
        elif arg_type == ARG_NONE:
            if len(arg) > 0:
                result = "Zu viele Parameter"
            otype = OP_NONE
        elif arg_type == ARG_TAG:
            if not arg[0] in self.tags:
                result = "Unbekanntere Marke %s" % (arg[0])
            otype = OP_STRING
        elif arg_type == ARG_STRING:
            if len(arg) > 1:
                result = "Es wird eine Parameter benötigt"
            otype = OP_STRING
        elif arg_type == ARG_VALUE:
            if len(arg) not in [1, 2]:
                result = "Falsche Parameter"
            elif len(arg) == 1:
                if not arg[0].isdigit():
                    result = "Keine Zahlenwert"
                otype = OP_INT
            elif len(arg) == 2:
                if (arg[0].upper() not in ['M', 'I', 'O'] or not arg[1].isdigit()):
                    result = "Keine gültige Speicher Adresse"
                otype = OP_MEM_ADDR

        return (result, otype)

    def init_func_links(self):
        #HASH key = OPCODE
        #Inhalt = Tuppel mit aufzurufender funktions link,
        #         ARGUMENTEN Type zur aufruf überprüfung
        #         Nummer der Block änderung (zur überrüfung ob im File alle
        #         Blöcke geschlossen sind)
        self.ins_list = {
            "NOP": (self.vm.nop, ARG_NONE, 0),
            "LD": (self.vm.load, ARG_VALUE, 0),
            "LDN": (self.vm.load_n, ARG_VALUE, 0),
            "ST": (self.vm.store, ARG_MEM_VAL, 0),
            "STN": (self.vm.store_n, ARG_MEM_VAL, 0),
            "S": (self.vm.set, ARG_MEM_BIT, 0),
            "R": (self.vm.reset, ARG_MEM_BIT, 0),
            "=": (self.vm.equalb, ARG_MEM_BIT, 0),
            "AND": (self.vm.andf, ARG_BIT_VAL, 0),
            "AND(": (self.vm.and_block, ARG_NONE, 1),
            "ANDN": (self.vm.nand, ARG_BIT_VAL, 0),
            "ANDN(": (self.vm.nand_block, ARG_NONE, 1),
            "OR": (self.vm.orf, ARG_BIT_VAL, 0),
            "OR(": (self.vm.or_block, ARG_NONE, 1),
            "ORN": (self.vm.nor, ARG_BIT_VAL, 0),
            "ORN(": (self.vm.nor_block, ARG_NONE, 1),
            "XOR": (self.vm.xor, ARG_BIT_VAL, 0),
            "XOR(": (self.vm.xor_block, ARG_BIT_VAL, 1),
            "ADD": (self.vm.add, ARG_BIT_VAL, 0),
            "ADD(": (self.vm.add_block, ARG_VALUE, 1),
            "SUB": (self.vm.sub, ARG_VALUE, 0),
            "SUB(": (self.vm.sub_block, ARG_VALUE, 1),
            "MUL": (self.vm.mul, ARG_VALUE, 0),
            "MUL(": (self.vm.mul_block, ARG_VALUE, 1),
            "DIV": (self.vm.div, ARG_VALUE, 0),
            "DIV(": (self.vm.div_block, ARG_VALUE, 1),
            "GT": (self.vm.gt, ARG_VALUE, 0),
            "GT(": (self.vm.gt_block, ARG_NONE, 1),
            "GE": (self.vm.ge, ARG_VALUE, 0),
            "GE(": (self.vm.ge_block, ARG_NONE, 1),
            "EQ": (self.vm.eq, ARG_VALUE, 0),
            "EQ(": (self.vm.eq_block, ARG_NONE, 1),
            "NE": (self.vm.ne, ARG_VALUE, 0),
            "NE(": (self.vm.ne_block, ARG_NONE, 1),
            "LE": (self.vm.le, ARG_VALUE, 0),
            "LE(": (self.vm.le_block, ARG_NONE, 1),
            "LT": (self.vm.lt, ARG_VALUE, 0),
            "LT(": (self.vm.lt_block, ARG_NONE, 1),
            "JMP": (self.vm.jmp, ARG_TAG, 0),
            "JMPC": (self.vm.jmpc, ARG_TAG, 0),
            "JMPCN": (self.vm.jmpcn, ARG_TAG, 0),
            "CALL": (self.vm.call, ARG_CALL, 0),
            "CALLC": (self.vm.callc, ARG_CALL, 0),
            "CALLCN": (self.vm.callcn, ARG_CALL, 0),
            "RET": (self.vm.ret, ARG_NONE, 0),
            "RETC": (self.vm.retc, ARG_NONE, 0),
            "RETCN": (self.vm.retcn, ARG_NONE, 0),
            ")": (self.vm.end_block, ARG_NONE, -1),
        # TEST FUNKTIONEN
            "DPRINT": (self.vm.dprint, ARG_VALUE, 0),
            "DPRINTB": (self.vm.dprintb, ARG_BIT_VAL, 0),
        # Interen Funktionen
            "HOOK": (self.vm.hook, ARG_STRING, 0)
            }

