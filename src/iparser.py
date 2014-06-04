import byte_compiler
from err import GenError



class Parser(GenError):
#Parser Object
#erzeugt Tokens für den ByteCompiler aus einem .il File
	
    def __init__(self, fname):
	#paramter fname: Datei die in Tokens gewandelt werden soll
        GenError()
        self.err = []
        self.name = fname
        self.parse_err = []
        self.parse(fname)

    
    def parse(self, filename):
    #liest Datei filename ein
        lines = []
        #Einlesen der Datei und in Zeilen trennen
        try:
            with open(filename) as f:
                for line in f:
                    l = line.replace('\n', '')
                    lines.append(l)
        except:
            self.add_err("File %s exsistiert nicht" % filename)
            self.fault()
        #Entfernt Kommentare
        code_with_tags = self.remove_comments(lines)
        #Prüft auf fehler
        self.check_err()
        #Sammelt alle Tags
        self.code, self.tags = self.collect_tags(code_with_tags)
        #Prüft auf fehler
        self.check_err()

    def remove_comments(self, lines):
    #entfernt in einem Array aus Strings alle vorhanden Kommentare
    #da diese den Code nur stören
        code = []
        remove = False
        for l in lines:
            end = l.find('*)')
            start = l.find('(*')
            s = ''
            if end != -1:
                s += l[:end-1]
            if end != -1:
                s += l[start+2:]
            if start == -1 and end == -1:
                s = l
            code.append(s)
        return code

    def collect_tags(self, tag_code):
    #sammelen aller Tags 
        code = []
        tags = {}
        cnt = 1
        i = 0
        for c in tag_code:
            find = c.find(':')
            if find > -1:
                tag = c[:find]
                if tag in tags:
                    self.add_err("Marke %s in %d bereits definiert"
                                      % (tag, cnt))
                tags[tag] = i
            else:
                code.append(c)
                i += 1
            cnt += 1
        return (code, tags)
