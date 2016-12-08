# RNA_TETRALOOPS

This folder contains the following data:
- projections.dat:
  projection along the first two principal components for each hairpin structure, and corresponding cluster.
  each structure is identified through a labelling that follow the  convention "PDB.CODE_SEQUENCE_FIRST.RESIDUE.NUMBER_FIRST.RESIDUE.TYPE_CHAIN_INSERTION_MODEL"
- 32 subfolders corresponding to 32 clusters, indexed as in supplementary information. Each subfolder contains a center.pdb file (the centroid),a cluster.pdb
  (all structures in the cluster aligned to the centroid) and a .rna file reporting the label of each structure along with the eRMSD from the centroid.
- A unassigned folder with structures not assigned to any cluster.

