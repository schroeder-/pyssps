

class IOHandler:

    def __init__(self):
        self.io_table = []
    
    def __lookup_mem__(self, addr):
        mem = self._get_io(addr)
        return mem[int(addr)]

    def lookup_bit(self, addr):
        ad, bit = addr.split('.')
        mem = self._get_io(addr)
        data = mem[int(ad)]
        mask = 1 << int(bit)
        return data & mask

    def __setitem__(self, addr, val):
        mem = self._get_io(addr)
        mem[int(addr)] = val

    def _bit_op(self, addr, b):
        ad, bit = addr.split('.')
        mask = 1 << int(bit)
        data = 0
        if b:
            data = data | mask
        else:
            data = data & mask
        mem = self._get_io(addr)
        mem[int(ad)] = data

    def set_bit(self, addr):
        self._bit_op(addr, True)

    def reset_bit(self, addr):
        self._bit_op(addr, False)

    
    

    
    def add(self, io):
        s = io.addr_offset
        i = s + io.size_in
        o = s + io.size_out
        self.io_table.append((io, s, i, o))

    def _get_io(self, addr, t):
        for table in self.io_table:
            if t == 'o':
                end = table[3]
            else:
                end = table[2]
            if addr in range(table[1], end):
                return table[0]
        return None
