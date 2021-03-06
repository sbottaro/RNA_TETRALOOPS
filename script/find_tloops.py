import sys
import mdtraj as md
import glob as glob
import numpy as np
from mdtraj.formats.pdb.pdbstructure import PdbStructure
sys.path.append('BARNABA_DIR')
from barnaba import annotate

# only standard RNA bases 
rnas = ["U","rU","RU","RU5","RU3","U3","U5",\
       "C","rC","RC","RC5","RC3","C3","C5",\
       "G","rG","RG","RG5","RG3","G3","G5",\
       "A","rA","RA","RA5","RA3","A3","A5"]
stack = ["<<",">>","<>","><","XX"]
oks = ["CA","O5'","C1'","C2"]

outname = sys.argv[1]
files=sys.argv[2:]
nn=8
qq=0
fh_out = open("contacts_%s.txt" % outname,"w")
# loop over files
for ff in files:
    
    try:
        pdb = md.load_pdb(ff)
        pdb_struct = PdbStructure(open(ff))
        residues_s = list(pdb_struct.iter_residues())
    except:
        print "# Skipping", ff
        continue

    top = pdb.topology

    #exit()
    insertions=[resi.insertion_code for resi in residues_s]
    assert(len(insertions)== len(list(top.residues)))

    # create list of atoms  and residue indeces for contacts calculations
    list_at_0 = [at for at in top.atoms if at.name in oks]
    list_resi_0 = [at.residue.index for at in list_at_0]
    
    # loop over chains
    for i in xrange(top.n_chains):
        chain = top.chain(i)
        # loop over residues in chain
        for j in range(chain.n_residues-nn):
            # check that at least C1' is present
            idx_atoms = []
            idx_c1p = []
            bonds = []

            for k in range(j,j+nn):
                if(chain.residue(k).name in rnas):
                    try:
                        idx_c1p.append(chain.residue(k).atom("C1'").index)
                        chain.residue(k).atom("C2").index
                        chain.residue(k).atom("C4").index
                        chain.residue(k).atom("C6").index
                        idx_atoms.extend([at.index for at in chain.residue(k).atoms])
                    except:
                        continue
                if(k>j and k <j+nn):
                    try:
                        bb = [chain.residue(k).atom("O3'").index,chain.residue(k+1).atom("P").index]
                        bonds.append(bb)
                    except:
                        continue
                
            if(len(idx_c1p)==nn and len(bonds) == nn-1):

                bdist = md.compute_distances(pdb,bonds)
                # iterate over models
                for l in range(pdb.xyz.shape[0]):

                    # check chain consistency:
                    if(len(np.where(bdist[l]>0.17)[0])!=0):
                        print "# broken chain",ff,top.atom(idx_c1p[0]).residue
                        continue
                    
                    # calculate distance between residue 1-8 and 2-7
                    dd1=pdb.xyz[l,idx_c1p[0]]-pdb.xyz[l,idx_c1p[7]]
                    dd2=pdb.xyz[l,idx_c1p[1]]-pdb.xyz[l,idx_c1p[6]]
                    diff1 = np.sqrt(np.sum((dd1**2)))
                    diff2 = np.sqrt(np.sum((dd2**2)))
                    # continue if they are less than 1.4 nm
                    if((diff1<1.4 and diff2 < 1.4)):

                        # slice atoms 
                        ss = pdb[l].atom_slice(idx_atoms)
                        if(ss.topology.n_residues!=nn):
                            print "# somthing wrong. only %d residues. skipping." % ss.topology.n_residues
                            continue
                        # do annotation
                        pairs, annotations = annotate.annotate_traj(ss)
                        
                        # check that bases 1-8 and 2-6 are interacting
                        interactions = 0
                        for i,el in enumerate(pairs[0]):
                            if(el == [0,7] and annotations[0][i]  not in stack):
                                interactions += 1
                            if(el == [1,6] and annotations[0][i]  not in stack):
                                interactions += 1
                        if(interactions>1):
                            
                            # check for contacts
                            list_at_1 = [top.atom(at) for at in idx_atoms if top.atom(at).name in oks]
                            list_resi_1 = [at.residue.index for at in list_at_1]
                            at_pairs = []
                            for i1 in range(len(list_at_1)):
                                for i2 in range(len(list_at_0)):
                                    if(list_at_0[i2] not in list_at_1):
                                        dist_resi1 = np.abs(list_resi_0[i2]-list_resi_1[0])
                                        dist_resi2 = np.abs(list_resi_0[i2]-list_resi_1[-1])
                                        if(dist_resi1 > 3 and dist_resi2> 3):
                                            aa1 = list_at_1[i1].index
                                            aa2 = list_at_0[i2].index
                                            at_pairs.append([aa1,aa2])
                            
                            ss.center_coordinates()
                            resn = top.atom(idx_c1p[0]).residue
                            seq = "".join([top.atom(idx_c1p[m]).residue.name for m in range(nn)])
                            seq_id = [top.atom(idx_c1p[m]).residue for m in range(nn)]
                            namef = "%s_%s_%05d.pdb" % (ff.split("/")[-1][:-4],str(resn),qq)
                            anno = annotate.get_string(0,pairs[0],annotations[0],seq_id,hread=False)
                            if(len(at_pairs) != 0):
                                dist = md.compute_distances(pdb,at_pairs)[l]
                                idxs = np.where(dist<1.0)
                                sh =  idxs[0].shape[0]
                                stri = "%40s %s %4d %4d %6.3f %s\n" % (namef,seq,sh,len(list_resi_1),1.*sh/len(list_resi_1),anno)
                            else:
                                stri = "%40s %s %4d %4d %6.3f %s\n" % (namef,seq,0.0,len(list_resi_1),0.0,anno)
                            fh_out.write(stri)
                            fh_out.flush()
                            #print namef,insertions[resn.index:resn.index+nn]
                            ss.save_pdb("TLOOPS/"+namef,insertions=insertions[resn.index:resn.index+nn])
                            qq += 1
fh_out.write("# script ended successfully \n")
fh_out.close()


