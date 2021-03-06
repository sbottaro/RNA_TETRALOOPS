import sys
import mdtraj as md
import glob as glob
import numpy as np

sys.path.append('BARNABA_DIR')
from barnaba import dump
from barnaba import cluster


out = sys.argv[1]
fh = open("%s.dat" % out,"w")
files = sys.argv[2:]
print "# reading %d files" % len(files)
for ff in files:
    try:
        pdb = md.load_pdb(ff)
    except:
        print "# Skipping", ff
        continue    
    seq,gvecs = dump.dump_gvec(pdb)
    for k in range(gvecs.shape[0]):
        if(gvecs[k].reshape(-1).shape[0]==256):
            ss = "%s %s "  % (ff, dump.get_string(seq,gvecs[k],hread=False))
            fh.write(ss)
        else:
            print "# skipping ",ff, k
            continue
fh.close()
