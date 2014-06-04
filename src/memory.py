import array
import copy
#@TODO änderungen nur bei wirklichen änderungen (bessere Performance)
class memory:
    def __init__(self, size):
        self.size = size
        #erzeugt liste mit size elementen
        mem_tmp = [0] * size
        #kopiert die liste in ein python array für bessere Performance
        self.mem = array.array('l', mem_tmp)


    def __getitem__(self, addr):
        return self.mem[int(addr)]

    def get_bit(self, addr):
        ad, bit = addr.split('.')
        data = self.mem[int(ad)]
        mask = 1 << int(bit)
        return data & mask

    def __setitem__(self, addr, val):
        self.mem[int(addr)] = val

    def _bit_op(self, addr, b):
        ad, bit = addr.split('.')
        mask = 1 << int(bit)
        data = 0
        if b:
            data = data | mask
        else:
            data = data & mask
        self.mem[int(ad)] = data

    def set_bit(self, addr):
        self._bit_op(addr, True)

    def reset_bit(self, addr):
        self._bit_op(addr, False)
