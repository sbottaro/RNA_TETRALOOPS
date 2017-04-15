#!bin/bash

#################### ATT!! ########################################################
# this script requires the ''library'' branch of the software program baRNAba     #
# freely available at https://github.com/srnas/barnaba. The entire path has to be #
# specified in the python files find_tloops.py; create_gvecs.py; analysis.py      #
# send me an email for more info: sandro dot bottaro guess_what gmail dot com     #
###################################################################################

# first, fetch all structured from PDB database
python fetch.py

# find tetraloops in PDB structures. This is slow, as a number of
# checks on structure are performed. better done in parallel.
# a contacts.txt file is created containing information on the number of contacts (column 3) as well as the annotation (column 6-)
mkdir TLOOPS


python find_tloops.py contacts_XRAY XRAY/*.pdb
python find_tloops.py contacts_NMR NMR/*.pdb
python find_tloops.py contacts_EM EM/*.pdb

# create gvectors from structures in TLOOPS directory
python create_gvecs.py gvecs TLOOPS/*pdb

# do cluster analysis
python analysis.py gvecs.dat > results.dat



