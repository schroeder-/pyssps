import array
import threading

#Basis Klasse für alle IO Schnitstellen
#die Methoden change muss erstellt werden
#die Methode set kann überschrieben werden
class BasicIO:
    # gibt die Offsetadresse sowie die in und out geröße an
    def __init__(self, addr_offset, size_in, size_out):
        self.size_out = size_out
        self.size_in = size_in
        self.addr_offset = addr_offset
        self.changes = {}
        self.con = None
        tmp = [0] * size_in
        self.mem_i = array.array('l', tmp)
        tmp = [0] * size_out
        self.mem_o = array.array('l', tmp)
        #Erzeugt einen Lock wegen Parallele zugriffen
        self.l = threading.Lock()
        #Timer im 20ms Takt der Änderungen Pollt
        self.t = threading.Timer(0.02, self.update)
        self.t.start()
        
    #Wird beim verbinden aufgerufen um die Daten zu Synchronisieren
    def init_io(self):
        mem = []
        i = 0
        for val in  self.mem_i[x]:
            mem.append((i, val))
            i += 1
        self.con.send(mem)

   
    #Sucht geänderte Werte
    def flush(self):
        ret_o = []
        for x in range(0, self.size_out):
            y = self.mem_o[x]
            if y != 0:
                ret_o.append((x,y))
        ret_i = []
        for x in range(0, self.size_in):
            y = self.mem_i[x]
            if y != 0:
                ret_i.append((x,y))
        return (ret_o, ret_i)

    #Udatet Werte übergeben wird eine Array aus (Addresse, Wert) Tupeles
    def con_flash(self, addr_val):
        for ad, val in addr_val:
            self.mem_i[ad] = val
            self.change(ad, val)

    #Muss von Basis Klasse überschrieben werden, wenn ein Wert von der
    #Gegenstelle gesetzt wird muss die Klasse hiere Änderungen durchführen
    def change(self, ad, val):
        assert(False)

    def set_bit(self, addr):
        self._bit_op(addr, True)

    def reset_bit(self, addr):
        self._bit_op(addr, False)

    #Ein Wert wurde von dieser Seite der Verbindung gesetzt
    def set(self, addr, b):
        pass

    def _set(self, addr, val):
        self.l.acquire()
        self.changes[addr] = val
        self.mem_o[addr] = val
        self.l.release()
        
    #setzt bit
    def __setitem__(self, rel_addr, val):
        addr = int(rel_addr) - self.addr_offset
        self.set(addr, val)
        self._set(addr, val)

    
    def _bit_op(self, addr, b):
        ad, bit = addr.split('.')
        mask = 1 << int(bit)
        data = self.get_out(ad)
        if b:
            data = data | mask
        else:
            data = data & ~mask
        self[int(ad)] = data
    #Timer funktionen die änderungen Pollt
    def update(self):
        self.flash_mem()
        self.t = threading.Timer(0.01, self.update)
        self.t.start()

    #Sendet Änderungen
    def flash_mem(self):
        mem = []
        if self.con == None:
            return
        self.l.acquire()
        for key in self.changes:
            mem.append((key, self.changes[key]))
        if len(mem) > 0:
            self.con.send(mem)
        self.changes = {}
        self.l.release()

    def get_in(self, addr):
        return self.mem_i[int(addr)]

    def get_out(self, addr):
        return self.mem_o[int(addr)]

    def get_bit(self, addr, _type):
        ad, bit = addr[1].split('.')
        if _type == 'i':
            data = self.get_in(ad)
        else:
            data = self.get_out(ad)
        mask = 1 << int(bit)
        return data & mask

