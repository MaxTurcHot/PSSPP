import math

class definition:
    def __init__(self):
        self.listoflines = []
        
    def get_indexes(self, id):
        count = 0
        indexes = []
        for line in self.listoflines:
            if line.is_included(id):
                indexes.append(count)
            count += 1
        return indexes

class defline:
    def __init__(self, name, minid, maxid, method, allow1, allow2, threshold, fs1, fs2):
        self.name = name
        self.minid = int(minid)
        self.maxid = int(maxid)
        self.method = int(method)
        self.allow1 = float(allow1)
        self.allow2 = float(allow2)
        self.threshold = float(threshold)
        self.fs1 = float(fs1)
        self.fs2 = float(fs2)
        self.mos1 = float("NaN")
        self.mos2 = float("NaN")
        self.eid = float("NaN")
        self.lcid = 0
        
    def show(self):
        print("-------------------------------")
        print("NAME: " + self.name)
        print("IDs: " + str(self.minid) + " to " + str(self.maxid))
        if self.method ==1:
            print("METHOD (1=VonMises): " + str(self.method))
            print("YIELD: "+ str(self.allow1))
            print("ULTIMATE: "+ str(self.allow2))
            print("PRINT THRESHOLD: "+ str(self.threshold))
            print("YIELD SAFETY FACTOR: " + str(self.fs1))
            print("ULTIMATE SAFETY FACTOR: " + str(self.fs2))
        elif self.method ==2:
            print("METHOD (2= Composite): " + str(self.method))
            print("COMPRESSION: "+ str(self.allow1))
            print("SHEAR: "+ str(self.allow2))
            print("PRINT THRESHOLD: "+ str(self.threshold))
            print("ULTIMATE SAFETY FACTOR: " + str(self.fs1))
            print("ULTIMATE SAFETY FACTOR (N/A)): " + str(self.fs2))
        
    def showout(self):
        
        text = "NAME: " + self.name + "\n"
        text = text + "IDs: " + str(self.minid) + " to " + str(self.maxid) + "\n"
        if self.method ==1:
            text = text + "METHOD (1=VonMises): " + str(self.method) + "\n"
            text = text + "YIELD: "+ str(self.allow1) + "\n"
            text = text + "ULTIMATE: "+ str(self.allow2) + "\n"
            text = text + "PRINT THRESHOLD: "+ str(self.threshold) + "\n"
            text = text + "YIELD SAFETY FACTOR: " + str(self.fs1) + "\n"
            text = text + "ULTIMATE SAFETY FACTOR: " + str(self.fs2) + "\n"
            text = text + "MIN YIELD MOS: " + str(self.mos1) + "\n"
            text = text + "MIN ULTIMATE MOS: " + str(self.mos2) + "\n"
        elif self.method ==2:
            text = text + "METHOD (2= Composite): " + str(self.method) + "\n"
            text = text + "COMPRESSION: "+ str(self.allow1) + "\n"
            text = text + "SHEAR: "+ str(self.allow2) + "\n"
            text = text + "PRINT THRESHOLD: "+ str(self.threshold) + "\n"
            text = text + "ULTIMATE SAFETY FACTOR: " + str(self.fs1) + "\n"
            text = text + "ULTIMATE SAFETY FACTOR (N/A): " + str(self.fs2) + "\n"
            text = text + "MIN COMPOSITE MOS: " + str(self.mos1) + "\n"
        text = text + "ELEMENT ID AT MIN ID: " + str(self.eid) + "\n"
        text = text + "LOAD CASE ID AT MIN ID: " + str(self.lcid) + "\n"
        text = text + "-------------------------------------------------\n"
        return text
        
    def is_included(self, id):
        if self.minid <= id and self.maxid >= id:
            return True
        else:
            return False
            
    def updatemin(self, eid, m1, m2, lcid):
        if  math.isnan(self.mos1) or self.mos1 > m1:
            self.mos1 = m1
            self.mos2 = m2
            self.eid = eid
            self.lcid = lcid
            