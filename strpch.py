#!/usr/bin/python
import sys
import deffile_structure
import stress_table
import math
import cmath
import os
import logging
version = "   0.3.0 "
filename = "strpch.log"
helpfile = "/home/turcmax/.bin/strpch_help.txt"
logging.basicConfig(filename=filename, encoding='utf-8', level=logging.INFO)
logging.info("Version "+ version)
try:
    def print_ascii(fout_name, mos, eid):
        fileout = open (fout_name, 'a')
        fileout.write("%15i," % eid)
        fileout.write("%15.4e\n" % mos)
        fileout.close()

    def create_altair_ascii(name, lcid, lcid_str):
        
        fname = name + '_' + lcid_str + ".hwascii"
        if not os.path.exists(fname):
            fascii = open(fname, 'w')
            fascii.write("ALTAIR ASCII FILE\n")
            fascii.write("$TITLE = " + lcid_str + "\n")
            fascii.write("$SUBCASE_ID =    " + str(lcid) + 	"   \"" + lcid_str + "\"\n")
            fascii.write("$BINDING = ELEMENT\n")
            fascii.write("$COLUMN_INFO = ENTITY_ID\n")
            fascii.write("$RESULT_TYPE = MOS (s)\n")
            fascii.write("$DELIMITER = ,\n")
            fascii.close()

    def tocomplex(mag, phase):
        rad = phase * math.pi /180.0
        real = mag * math.cos(rad)
        im = mag * math.sin(rad)
        # print("mag " + str(mag))
        # print("phase " + str(phase))
        # print("real " + str(real))
        # print("im " + str(im))
        return complex(real,im)

    def read_def(fin):
        # Create definition file object
        deffile = deffile_structure.definition()
        # READ line by line the definition file
        Lines = fin.readlines()
        # count = 0
        for line in Lines:
            if line[0] != '#':
                # print(line)
                values = line.split(',')
                if len(values) == 9:
                    # create line object
                    newline = deffile_structure.defline(values[0],values[1],values[2],values[3],values[4],values[5],values[6],values[7],values[8])
                    # pout = newline.showout()
                    # fout.write(pout)
                    deffile.listoflines.append(newline)
                else:
                    fout.write("Error in definition file (9 arguments must be present on every line)")
        return deffile

    def compute_vm_linear(eid, i, Lines, defline, lcid):
        # Find VonMises at Z1
        vmz1 = float(Lines[i+2].split()[2])
        # Find VonMises at Z2
        vmz2 = float(Lines[i+5].split()[1])
        # Find Max VonMises
        vm = max(vmz1, vmz2)
        # Compute Yield MoS
        mos1 = ( defline.allow1 / defline.fs1 / vm ) - 1
        # Compute Ultimate MoS
        mos2 = ( defline.allow2 / defline.fs2 / vm ) - 1
        defline.updatemin(eid, mos1, mos2, lcid)
        # print(str(mos1) + " : " + str(defline.mos1))
        return [mos1, mos2, vm]

    def compute_comp_linear(eid, i, Lines, defline, lcid):
        # Find XX at Z1
        xx1 = float(Lines[i].split()[2])
        # Find YY at Z1
        yy1 = float(Lines[i].split()[3])
        # Find XY at Z1
        xy1 = float(Lines[i+1].split()[1])
        # Find XX at Z2
        xx2 = float(Lines[i+3].split()[1])
        # Find YY at Z2
        yy2 = float(Lines[i+3].split()[2])
        # Find XY at Z2
        xy2 = float(Lines[i+3].split()[3])
        # compute ra
        raz1 =  math.pow(math.pow(abs(xx1),3.0) + math.pow(abs(yy1),3.0), 0.33333) / defline.allow1
        raz2 =  math.pow(math.pow(abs(xx2),3.0) + math.pow(abs(yy2),3.0), 0.33333) / defline.allow1
        # compute rs 
        rsz1 = abs(xy1) / defline.allow2
        rsz2 = abs(xy2) / defline.allow2
        # compute MoS
        ra_rs = max(raz1 + rsz1, raz2 + rsz2)
        mos1 = (1 / defline.fs1 / ra_rs ) -1
        # print(eid)
        # print("xx: " + str(xx1) + " yy: " + str(yy1) + " xy: " + str(xy1))
        # print("xx: " + str(xx2) + " yy: " + str(yy2) + " xy: " + str(xy2))
        defline.updatemin(eid, mos1, mos1, lcid)
        return [mos1, mos1, ra_rs]

    def compute_vm_freq(eid, i, Lines, defline, lcid):
        # print(Lines[i])
        
        #  Z1
        # Find Z1 XX mag
        xx_m_z1 = float(Lines[i].split()[2])
        # Find Z1 XX ph
        xx_p_z1 = float(Lines[i].split()[3])
        # Find Z1 YY mag
        yy_m_z1 = float(Lines[i+1].split()[1])
        # Find Z1 YY ph
        yy_p_z1 = float(Lines[i+1].split()[2])
        # Find Z1 XY mag
        xy_m_z1 = float(Lines[i+1].split()[3])
        # Find Z1 XY ph
        xy_p_z1 = float(Lines[i+2].split()[1])

        #  Z2
        # Find Z1 XX mag
        xx_m_z2 = float(Lines[i+2].split()[3])
        # Find Z1 XX ph
        xx_p_z2 = float(Lines[i+3].split()[1])
        # Find Z1 YY mag
        yy_m_z2 = float(Lines[i+3].split()[2])
        # Find Z1 YY ph
        yy_p_z2 = float(Lines[i+3].split()[3])
        # Find Z1 XY mag
        xy_m_z2 = float(Lines[i+4].split()[1])
        # Find Z1 XY ph
        xy_p_z2 = float(Lines[i+4].split()[2])
        
        # Convert to complex numbers
        xx_z1 = tocomplex(xx_m_z1, xx_p_z1)
        yy_z1 = tocomplex(yy_m_z1, yy_p_z1)
        xy_z1 = tocomplex(xy_m_z1, xy_p_z1)
        xx_z2 = tocomplex(xx_m_z2, xx_p_z2)
        yy_z2 = tocomplex(yy_m_z2, yy_p_z2)
        xy_z2 = tocomplex(xy_m_z2, xy_p_z2)
        
        
        vm_z1 = cmath.sqrt( xx_z1 * xx_z1 - xx_z1 * yy_z1 + yy_z1 * yy_z1 + 3.0 * xy_z1 * xy_z1 )
        vm_z2 = cmath.sqrt( xx_z2 * xx_z2 - xx_z2 * yy_z2 + yy_z2 * yy_z2 + 3.0 * xy_z2 * xy_z2 )
        
        # Find Max VonMises
        vm = max(abs(vm_z1), abs(vm_z2))
        
        # Compute Yield MoS
        mos1 = ( defline.allow1 / defline.fs1 / vm ) - 1
        # Compute Ultimate MoS
        mos2 = ( defline.allow2 / defline.fs2 / vm ) - 1
        
        
        defline.updatemin(eid, mos1, mos2, lcid)
        # if eid == 200261:
            # print("EID: "+  str(eid) + ":   xx z1: " + str(xx_m_z1) + " yy z1: " + str(yy_m_z1) + " xy: z1" + str(xy_m_z1) + " VM z1: " + str(abs(vm_z1)) + " REAL: " + str(vm_z1.real) + " COMPLEX : " + str(vm_z1.imag))
            # print("EID: "+  str(eid) + ":   xx z2: " + str(xx_m_z2) + " yy z2: " + str(yy_m_z2) + " xy z2: " + str(xy_m_z2) + " VM z2: " + str(abs(vm_z2)) + " REAL: " + str(vm_z2.real) + " COMPLEX : " + str(vm_z2.imag))
            # print(vm_z2)
        return [mos1, mos2, vm]

    def compute_comp_freq(eid, i, Lines, defline, lcid):
        # print(Lines[i])
        
        #  Z1
        # Find Z1 XX mag
        xx_m_z1 = float(Lines[i].split()[2])
        # Find Z1 XX ph
        # xx_p_z1 = float(Lines[i].split()[3])
        # Find Z1 YY mag
        yy_m_z1 = float(Lines[i+1].split()[1])
        # Find Z1 YY ph
        # yy_p_z1 = float(Lines[i+1].split()[2])
        # Find Z1 XY mag
        xy_m_z1 = float(Lines[i+1].split()[3])
        # Find Z1 XY ph
        # xy_p_z1 = float(Lines[i+2].split()[1])

        #  Z2
        # Find Z1 XX mag
        xx_m_z2 = float(Lines[i+2].split()[3])
        # Find Z1 XX ph
        # xx_p_z2 = float(Lines[i+3].split()[1])
        # Find Z1 YY mag
        yy_m_z2 = float(Lines[i+3].split()[2])
        # Find Z1 YY ph
        # yy_p_z2 = float(Lines[i+3].split()[3])
        # Find Z1 XY mag
        xy_m_z2 = float(Lines[i+4].split()[1])
        # Find Z1 XY ph
        # xy_p_z2 = float(Lines[i+4].split()[2])
        
        # Convert to complex numbers
        # xx_z1 = tocomplex(xx_m_z1, xx_p_z1)
        # yy_z1 = tocomplex(yy_m_z1, yy_p_z1)
        # xy_z1 = tocomplex(xy_m_z1, xy_p_z1)
        # xx_z2 = tocomplex(xx_m_z2, xx_p_z2)
        # yy_z2 = tocomplex(yy_m_z2, yy_p_z2)
        # xy_z2 = tocomplex(xy_m_z2, xy_p_z2)
        
        ra_z1 = math.pow( math.pow(xx_m_z1, 3) + math.pow(yy_m_z1, 3), 0.3333) / defline.allow1
        ra_z2 = math.pow( math.pow(xx_m_z2, 3) + math.pow(yy_m_z2, 3), 0.3333) / defline.allow1
        rs_z1 = xy_m_z1 / defline.allow2
        rs_z2 = xy_m_z2 / defline.allow2
        rars_z1 = ra_z1 + rs_z1
        rars_z2 = ra_z2 + rs_z2
        
        # Find Max ratio
        rars = max(rars_z1, rars_z2)
        
        
        # Compute Yield MoS
        mos1 = (1 / defline.fs1 / rars ) - 1

        
        
        defline.updatemin(eid, mos1, mos1, lcid)
        # if eid == 200261:
            # print("EID: "+  str(eid) + ":   xx z1: " + str(xx_m_z1) + " yy z1: " + str(yy_m_z1) + " xy: z1" + str(xy_m_z1) + " VM z1: " + str(abs(vm_z1)) + " REAL: " + str(vm_z1.real) + " COMPLEX : " + str(vm_z1.imag))
            # print("EID: "+  str(eid) + ":   xx z2: " + str(xx_m_z2) + " yy z2: " + str(yy_m_z2) + " xy z2: " + str(xy_m_z2) + " VM z2: " + str(abs(vm_z2)) + " REAL: " + str(vm_z2.real) + " COMPLEX : " + str(vm_z2.imag))
            # print(vm_z2)
        return [mos1, mos1, rars]

    def compute_vm_random(eid, i, Lines, defline, lcid):
        # Find VonMises at Z1
        xx_z1 = float(Lines[i].split()[2])
        yy_z1 = float(Lines[i].split()[3])
        xy_z1 = float(Lines[i+1].split()[1])
        xx_z2 = float(Lines[i+1].split()[3])
        yy_z2 = float(Lines[i+2].split()[1])
        xy_z2 = float(Lines[i+2].split()[2])
        vm_z1 = math.sqrt( (xx_z1 * xx_z1) - (xx_z1 * yy_z1) + (yy_z1 * yy_z1) + (3.0 * xy_z1 * xy_z1) )
        vm_z2 = math.sqrt( (xx_z2 * xx_z2) - (xx_z2 * yy_z2) + (yy_z2 * yy_z2) + (3.0 * xy_z2 * xy_z2) )
        # Find Max VonMises
        vm = max(vm_z1, vm_z2) * 3.0
        # Compute Yield MoS
        mos1 = ( defline.allow1 / defline.fs1 / vm ) - 1
        # Compute Ultimate MoS
        mos2 = ( defline.allow2 / defline.fs2 / vm ) - 1
        defline.updatemin(eid, mos1, mos2, lcid)
        # print(str(mos1) + " : " + str(defline.mos1))
        return [mos1, mos2, vm]

    def compute_comp_random(eid, i, Lines, defline, lcid):
        xx_z1 = float(Lines[i].split()[2])
        yy_z1 = float(Lines[i].split()[3])
        xy_z1 = float(Lines[i+1].split()[1])
        xx_z2 = float(Lines[i+1].split()[3])
        yy_z2 = float(Lines[i+2].split()[1])
        xy_z2 = float(Lines[i+2].split()[2])
        # compute ra
        raz1 =  math.pow(math.pow(abs(xx_z1),3.0) + math.pow(abs(yy_z1),3.0), 0.33333) / defline.allow1
        raz2 =  math.pow(math.pow(abs(xx_z2),3.0) + math.pow(abs(yy_z2),3.0), 0.33333) / defline.allow1
        # compute rs 
        rsz1 = abs(xy_z1) / defline.allow2
        rsz2 = abs(xy_z2) / defline.allow2
        # compute MoS
        ra_rs = max(raz1 + rsz1, raz2 + rsz2) * 3.0
        mos1 = (1 / defline.fs1 / ra_rs ) -1
        defline.updatemin(eid, mos1, mos1, lcid)
        return [mos1, mos1, ra_rs]

    def compute_mos(eid, j, i, Lines, deffile, analtype, lcid):
        # get stress method
        method = deffile.listoflines[j].method
        # print("eid: " + str(eid) + " lcid: " + str(lcid) + " method: " + str(method))
        if method == 1 and analtype ==1:
            # LINEAR - VONMISES
            moss = compute_vm_linear(eid, i, Lines, deffile.listoflines[j], lcid)
        elif method == 2 and analtype ==1:
            # LINEAR - COMPOSITE STRESS
            moss = compute_comp_linear(eid, i, Lines, deffile.listoflines[j], lcid)
        elif method == 1 and analtype ==2:
            # SINE - VONMISES
             moss = compute_vm_freq(eid, i, Lines, deffile.listoflines[j], lcid)
        elif method == 2 and analtype ==2:
            # SINE - COMPOSITE STRESS
            moss = compute_comp_freq(eid, i, Lines, deffile.listoflines[j], lcid)
        elif method == 1 and analtype == 3:
            # RANDOM - VONMISES
            moss = compute_vm_random(eid, i, Lines, deffile.listoflines[j], lcid)
        elif method == 2 and analtype == 3:
            # RANDOM - COMPOSITE STRESS
            moss = compute_comp_random(eid, i, Lines, deffile.listoflines[j], lcid)
        return moss
              
    def process_pch(deffile, fout, fpch, s_table):
        Lines = fpch.readlines()
        stressflag = False
        analtype = 0
        etypefound = False
        looptodo = True
        # for i in range(len(Lines)):
        i = 0
        while i < len(Lines):
            line = Lines[i]
            if line.startswith('$ELEMENT STRESSES'):
                stressflag = True
                if line.startswith('$ELEMENT STRESSES - RMS'):
                    analtype = 3
                    # print("Random detected")
                # print("Stress flag detected")
            elif stressflag and line.startswith('$REAL OUTPUT') and not analtype == 3:
                analtype = 1
                # print("Static load case detected")
            elif stressflag and line.startswith('$MAGNITUDE-PHASE OUTPUT') and not analtype == 3:
                analtype = 2
                is_freq = True
                # print("Sine load case detected")
            if line.startswith('$SUBTITLE='):
                label = line.split('=')[1].rstrip("\n")
            if stressflag and (line.startswith('$SUBCASE ID =') or line.startswith('$RANDOM ID =')):
                lcid = int(line.split()[3])
                # print('je suis ici')
                if analtype == 1 or analtype == 3:
                    s_table.add_lc(lcid, analtype, label)
                    create_altair_ascii(str(os.path.basename(fout.name)).split('.')[0], lcid, str(lcid))
                    # print('LC added: ' + str(lcid))
            if stressflag and (analtype > 0):
                if line.startswith('$ELEMENT TYPE ='):
                    etype = int(line.split()[3])
                    etypefound = True
         
            if etypefound and (etype == 33 or etype ==74):
                # Element type supported
                # print("element type supported")
                if analtype ==1:
                    # We can start looping into element
                    i += 1
                    while stressflag and (i < (len(Lines) - 5)):
                        # print(str(i < (len(Lines) - 5))+ ":" + str(i) + ":" + str(len(Lines)))
                        line = Lines[i]
                        if line.startswith('$'):
                            stressflag = False
                            analtype = 0
                            etypefound = False
                            break
                            # print("B-----" + line + "-----E")
                        # Determine if element is in def file
                        eid = int(Lines[i].split()[0])
                        indx = deffile.get_indexes(eid)
                        # Compute MOS
                        for j in indx:
                            moss = compute_mos(eid, j, i, Lines, deffile, analtype, lcid)
                            if deffile.listoflines[j].threshold == 1:
                                fout_name = str(os.path.basename(fout.name)).split('.')[0] + "_" +str(lcid) + ".hwascii"
                                print_ascii(fout_name, moss[1], eid)
                                
                            # add MoSs to the stress table
                            s_table.assign_mos(moss, eid, lcid, j)
                        i = i + 6
                        # print("-----")
                        # print("LCid: " + str(lcid)+ " : " + str(eid) + "   i:" + str(i) + "   len(Lines)=" + str(len(Lines)) + "   Indexes: " + str(indx))
                        # skip 5 line
                        if i > (len(Lines)-2):
                            stressflag = False
                            analtype = 0
                            etypefound = False
                            break
                elif analtype == 2:
                    i += 1
                    line = Lines[i]
                    eid = int(Lines[i].split()[3])
                    i += 1
                    line = Lines[i]
                    while stressflag and (i < (len(Lines) - 1)):
                        line = Lines[i]
                        # print(line + " : " + str(i))
                        if line.startswith('$'):
                                stressflag = False
                                analtype = 0
                                etypefound = False
                                looptodo = False
                                break
                        freq = float(line.split()[0])
                        label_lc = label + "_" + str(freq) + "Hz"
                        if looptodo:
                            s_table.add_lc(lcid, analtype, label_lc)
                            lcidplus = int(str(lcid) + str(int(freq * 1000)))
                            create_altair_ascii(str(os.path.basename(fout.name)).split('.')[0], lcidplus, label_lc)
                        # Determine if element is in def file
                        indx = deffile.get_indexes(eid)
                        # Compute MOS
                        for j in indx:
                            moss = compute_mos(eid, j, i, Lines, deffile, analtype, lcid)
                            if deffile.listoflines[j].threshold == 1:
                                fout_name = str(os.path.basename(fout.name)).split('.')[0] + "_" +str(label_lc) + ".hwascii"
                                print_ascii(fout_name, moss[1], eid)
                            # print(label_lc + str(eid))
                            s_table.assign_mos(moss, eid, lcid, j, label_lc)
                        i = i + 5
                        if i > (len(Lines) - 1):
                            stressflag = False
                            analtype = 0
                            etypefound = False
                            break
                elif analtype == 3:
                    # We can start looping into element
                    i += 1
                    while stressflag and (i < (len(Lines) - 5)):
                        # print(str(i < (len(Lines) - 5))+ ":" + str(i) + ":" + str(len(Lines)))
                        line = Lines[i]
                        if line.startswith('$'):
                            stressflag = False
                            analtype = 0
                            etypefound = False
                            break
                            # print("B-----" + line + "-----E")
                        # Determine if element is in def file
                        eid = int(Lines[i].split()[0])
                        indx = deffile.get_indexes(eid)
                        # Compute MOS
                        for j in indx:
                            moss = compute_mos(eid, j, i, Lines, deffile, analtype, lcid)
                            if deffile.listoflines[j].threshold == 1:
                                fout_name = str(os.path.basename(fout.name)).split('.')[0] + "_" +str(lcid) + ".hwascii"
                                print_ascii(fout_name, moss[1], eid)
                            # add MoSs to the stress table
                            s_table.assign_mos(moss, eid, lcid, j)
                        i = i + 3
                        # print("-----")
                        # print("LCid: " + str(lcid)+ " : " + str(eid) + "   i:" + str(i) + "   len(Lines)=" + str(len(Lines)) + "   Indexes: " + str(indx))
                        # skip 5 line
                        if i > (len(Lines)-2):
                            stressflag = False
                            analtype = 0
                            etypefound = False
                            break
                
            i += 1 

    def process(fin, fout, fpch):
        deffile = read_def(fin)
        s_table = stress_table.table(deffile)
        process_pch(deffile, fout, fpch, s_table)

        # PRINT
        for line in deffile.listoflines:
            pout = line.showout()
            fout.write(pout)
        fout.write("|-Load Case id|,|---------------Load Case--------------|,|-----Part Name-----|,|-Max Stress--|,|-Allowable 1-|,|-Allowable 2-|,|----MoS 1----|,|----MoS 2----|,|---Min EID---|\n")
        for lc in s_table.load_cases:
            for part in lc.parts:
                fout.write("%15i," % lc.lcid)
                fout.write("%40s," % lc.label)
                fout.write("%21s," % part.name)
                fout.write("%15.2f," % part.maxstress)
                fout.write("%15.2f," % part.allowable1)
                fout.write("%15.2f," % part.allowable2)
                fout.write("%15.2f," % part.minmos1)
                fout.write("%15.2f," % part.minmos2)
                fout.write("%15i\n" % part.eid)


    if len(sys.argv) != 3 and len(sys.argv) != 4 :
        fout = open(filename, "w")
        fout.write("----------------------------------------------------------\n")
        fout.write("----- Punch Stress Structural Post Processor (PSSPP) -----\n")
        fout.write("----------------------------------------------------------\n")
        fout.write("----- Version: " + str(version) + " ---------------------------------\n")
        fout.write("----------------------------------------------------------\n")
        fout.write("Error: 2 or 3 argument but be used as follow:\nstrpch.py definitionfile punchfile\nor\nstrpch.py definitionfile punchfile outfile\n")
        fout.write("----------------------------------------------------------\n")
    elif len(sys.argv) == 3:
        punchstring = sys.argv[2]
        outbase = punchstring.split('.')
        fout = open(outbase[0] + ".strout", "w")
        fout.write("----------------------------------------------------------\n")
        fout.write("----- Punch Stress Structural Post Processor (PSSPP) -----\n")
        fout.write("----------------------------------------------------------\n")
        fout.write("----- Version: " + str(version) + " ---------------------------------\n")
        fout.write("----------------------------------------------------------\n")
        fin = open(str(sys.argv[1]), "r")
        fpch = open(str(sys.argv[2]), "r")
        process(fin, fout, fpch)
        fin.close()
        fpch.close()
    else:
        punchstring = sys.argv[2]
        fout = open(str(sys.argv[3]) + ".strout", "w")
        fout.write("----------------------------------------------------------\n")
        fout.write("----- Punch Stress Structural Post Processor (PSSPP) -----\n")
        fout.write("----------------------------------------------------------\n")
        fout.write("----- Version: " + str(version) + " ---------------------------------\n")
        fout.write("----------------------------------------------------------\n")
        fin = open(str(sys.argv[1]), "r")
        fpch = open(str(sys.argv[2]), "r")
        process(fin, fout, fpch)
        fin.close()
        fpch.close()
    with open(helpfile, 'r') as infile:
        fout.write(infile.read())

    fout.close()

except:
    logging.error('Error 10001: Top level error')

