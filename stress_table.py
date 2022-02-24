import math

class table:
    def __init__(self, deffile):
        self.deffile = deffile
        self.listoflc = []
        self.listoflabels = []
        self.load_cases = []
    
    def add_lc(self, lcid, analtype, label):
        if analtype == 1 or analtype == 3:
            if not lcid in self.listoflc:
                self.insert_lc(lcid, label)
        elif analtype == 2:
            if not label in self.listoflabels:
                self.insert_lc(lcid, label)
                
            
    def insert_lc(self, lcid, label):
        self.listoflc.append(lcid)
        self.listoflabels.append(label)
        self.load_cases.append(load_case(self.deffile, lcid, label))
    

    
    def assign_mos(self, mos_array, eid, lcid, line_id, label = ""):
        # get lc index
        if label == "":
            # LINEAR LOAD CASE DETECTED
            i = self.listoflc.index(lcid)
            
        else:
            # FREQUENCY LOAD CASE DETECTED
            i = self.listoflabels.index(label)
        if  math.isnan(self.load_cases[i].parts[line_id].minmos1) or self.load_cases[i].parts[line_id].minmos1 > mos_array[0]:
            self.load_cases[i].parts[line_id].minmos1 = mos_array[0]
            self.load_cases[i].parts[line_id].minmos2 = mos_array[1]
            self.load_cases[i].parts[line_id].maxstress = mos_array[2]
            self.load_cases[i].parts[line_id].eid = eid
        
    
class load_case:
    def __init__(self, deffile, lcid, label):
        self.lcid = lcid
        self.label = label
        self.parts = []
        for line in deffile.listoflines:
            new_part = part(line.name, line.allow1, line.allow2)
            self.parts.append(new_part)
                  
class part:
    def __init__(self, name, allowable1, allowable2):
        self.name = name
        self.minmos1 = float("NaN")
        self.minmos2 = float("NaN")
        self.eid = 0
        self.maxstress = float("NaN")
        self.allowable1 = allowable1
        self.allowable2 = allowable2