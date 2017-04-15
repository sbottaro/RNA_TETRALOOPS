import urllib2
import os

url = 'http://www.rcsb.org/pdb/rest/search'

names = ["XRAY","NMR","EM"]
files = ["query_xray.xml","query_nmr.xml","query_em.xml"]
#files = ["query_em.xml"]
#names = ["EM"]

for ii,ff in enumerate(files):
    fh = open(ff)
    queryText =  fh.read()
    print "querying %s...\n" % (ff)
    req = urllib2.Request(url, data=queryText)
    f = urllib2.urlopen(req)
    result = f.read()
    if result:
        print "Found number of PDB entries:", result.count('\n')
    else:
        print "Failed to retrieve results" 

    # create directory
    os.system("mkdir %s" % names[ii])
    for pdb in result.split():
        print "# PDB:", pdb,        
        if(os.path.isfile(("%s/%s.pdb") % (names[ii],pdb))):
            print " - is already here!"
            continue
        
        nn = pdb.lower()
        # if file is em - try to get information first (it is not possible to query resolution)
        if(ff=="query_em.xml"):
            
            cmd = "wget \"http://www.rcsb.org/pdb/rest/customReport?pdbids=%s&customReportColumns=structureId,structureTitle,resolution\" -O %s.report -q" % (nn,nn)
            out_tmp = os.system(cmd)
            if(out_tmp!=0):
                print "# fatal error", cmd
                exit(1)
                    
            # read resolution
            try:
                lines = [float((line.replace(">","<").split("<"))[2]) for line in open("%s.report"%  nn) if "dimStructure.resolution" in line]
            except:
                lines = [(line.replace(">","<").split("<"))[2] for line in open("%s.report"%  nn) if "dimStructure.resolution" in line]
                print " skipping:  not possible to find resolution (%s) " % (lines[0])
                continue
                    
            if(lines[0]>3.5):
                print " skipping: low resolution %4.2f " % (lines[0])
                continue
            else:
                print " Good good: ok resolution %4.2f " % (lines[0]),

        cmd = "wget https://files.rcsb.org/download/%s.pdb -O %s/%s.pdb -q" % (pdb,names[ii],pdb)
        out_0 = os.system(cmd)
        if(out_0==0):
            print " - OK"
        else:
            # remove file
            os.system("rm %s/%s.pdb" % (names[ii],pdb))
            if(os.path.isfile(("%s/%s.tar.gz") % (names[ii],pdb))):
                print " - is already here!"
                continue
            
            cmd = "wget http://ftp.wwpdb.org/pub/pdb/compatible/pdb_bundle/%s/%s/%s-pdb-bundle.tar.gz -O %s/%s.tar.gz -q" % (nn[1:3],nn,nn,names[ii],pdb)
            out_01 = os.system(cmd)
            if(out_01!=0):
                print "# fatal error", cmd
                print out_0, out_01
                exit(1)
            # untar
            cmd = "tar -xf %s/%s.tar.gz -C %s/" % (names[ii],pdb,names[ii])
            out_01 = os.system(cmd)
            if(out_01==0):
                print "- OK - tar.gz downloaded and extracted"
            else:
                print "# fatal error", cmd
                exit(1)
                
