import sys
import mdtraj as md
import glob as glob
import numpy as np
from scipy.spatial.distance import pdist, squareform

sys.path.append('BARNABA_DIR')
from barnaba import dump
from barnaba import cluster


filen = sys.argv[2]
fh = open(filen)
gvecs = []
labels = []
for line in fh:
    if(len(line.split())==257):
        labels.append(line.split()[0])
        gvecs.append([float(x) for x in line.split()[1:]])
gvecs = np.asarray(gvecs)
fh.close()
print "# File read,", gvecs.shape

v,w = cluster.pca(gvecs)
eps = float(sys.argv[1])
ms=25

cluster_labels, center_idx = cluster.dbscan(gvecs,labels,eps,ms)

for k in range(len(labels)):
    string = "%40s " % labels[k]
    for p in range(3):
        string += " %13e " % w[k,p]
    if(k in center_idx):
        ww = "C"
    else:
        ww = "X"
    string += " %3d %s \n" % (cluster_labels[k],ww)
    print string, 
