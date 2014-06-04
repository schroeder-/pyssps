
class GenError:
    def __init__(self):
        pass

    def add_err(self, mes):
        #@TODO add max err check
        self.err.append(mes)

    def check_err(self):
        if len(self.err) > 0:
            self.fault()

    def fault(self):
        for m in self.err:
            print(m)
        print("Programm wird benndet mit %d Fehlern" % len(self.err))
        exit(-1)


