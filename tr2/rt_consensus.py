#wrapper of Triplec program

import os
import sys
import subprocess

from newick_io import *
#from rooted_triple import *

def run_triplec(treefile, nrep=1000, bindir="bin"):
	cmd= "java -jar " + os.path.join(bindir, "Triplec.jar") + " %d "%nrep + treefile 
	#result = os.system(cmd)
	result = subprocess.check_output(cmd, shell=True)	
	return result

if __name__=="__main__":
	rtc = run_triplec(sys.argv[1], nrep=int(sys.argv[2]))

	print rtc
	print parse_newick(rtc)
	#for trpl in RootedTriple.triples_from_tree(parse_newick(rtc)):
	#	print trpl


