#tr2-delimitation
Multilocus species delimitation using a trinomial distribution model

Authour: Tomochika Fujisawa: <<t.fujisawa05@gmail.com>>

##Description
The tr2 is a program for multilocus species delimitation. It is written in Python. It delimits species groups from unlinked multilocus gene trees by measuring incongruence of tree topology within species and congruence between species. Topological congruence is measured by counting the topology of rooted triplets and fitting them to two types of trinomial distribution models.

**This is an older version of tr2-delimitation. A newer version in Python3 is available at** 

https://bitbucket.org/tfujisawa/tr2-delimitation-python3

**This Python2 version is still maintained, but new functions are added only to the Python3 version.**

Please see the following paper for detailed descriptions of the method and performance tests.

http://sysbio.oxfordjournals.org/content/65/5/759

A manual more detailed than this README file is available on my website.

https://tmfujis.wordpress.com/software/#tr2

##Software Dependency
1. Python and packages Numpy and Scipy are required to run the tr2. Visit Python website (https://www.python.org/) and numpy/scipy download page (http://www.scipy.org/scipylib/download.html) for detials of installation. The easiest way to install these dependencies is to install Anaconda (http://continuum.io/downloads), which includes Python and all required packages. 

2. Java is requred to run Triplec to build a rooted triple consensus tree. 

3. The tr2 uses the Triplec program to build a consensus guide tree from a set of gene trees. To obtain Triplec, visit http://www.cibiv.at/software/triplec.

##Software Download
If you have an environment with Mercurial installed, use
```
hg clone https://tfujisawa@bitbucket.org/tfujisawa/tr2-delimitation
```
to download the software with all changesets.

An alternative way to download software is to click the "Downloads" icon at the left of this page (an icon with cloud like shape). You will see "Download repository" link for downloading files.

##Installation
You can put the tr2-delimitation directory wherever you want. If you want to run Triplec, download the Triplec.jar from its website, then create a directory named "bin" in the tr2-delimitation directory and put the Triplec.jar in the created "bin" directory.

##Examples
There three modes of delimitation. They are called from "run_tr2.py".

###1. Calculation of a posterior probability score of a given delimitation hypothesis
```
./run_tr2.py -t sim4sp/simulated.gene.trees.nex10.4sp.tre -a sim4sp/sp.assoc.4sp.txt
```
t : multiple gene trees in Newick format

a : tab delimited text file specifying sample - species association

###2. Delimitation of species using a user specified guide tree
```
./run_tr2.py -t sim4sp/simulated.gene.trees.nex10.4sp.tre -g sim4sp/guide.tree.4sp.tre
```
t : multiple gene trees in Newick format

g : a guiding tree in Newick format. tips of guide tree must include all tip names of gene tree.

###3. Delimitation of species using a consensus tree (optional)
```
./run_tr2.py -t sim4sp/simulated.gene.trees.nex10.4sp.tre
```
t : multiple gene trees in Newick format

Results are written in files with prefix specified by "-o" option.

*  *prefix*.table.txt contains the best scoring delimitation.
*  *prefix*.tre contains a guide tree with support of delimitation. Nodes with "\*" sign are the best scoring set of MRCA nodes which define species groups.

If "-o" option is omitted, outputs are written to stdout.

##License
tr2-delimitation: multilocus species delimitation with a trinomial distribution model
Copyright (C) 2015 Tomochika Fujisawa

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
