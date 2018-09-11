import sys

from newick_io import *
from tree_node import TreeNode

class GuideTree:
	def __init__(self, tree, sep="<>"):
		#self.root = tree.clone()	#need to clone node?
		self.root = tree
		for node in self.root.traverse():
			if type(node.name) == list:
				node.name = [n.strip("\"").split(sep) for n in node.name]
				node.name = reduce(lambda x, y: x+y, node.name)

		self.species_nodes = [self.root]
		self.species_tips = []
		self.score = 0.0

	def __str__(self):
		return str(self.root)
	
	def list_species(self):
		sample_sp = {}
		for i, node in enumerate(self.species_nodes+self.species_tips):
			#print i+1, node.name
			for n in node.name:
				sample_sp[n] = i+1	
		return sample_sp

	#def update_species_nodes(self):
	#	tmp = self.species_nodes.pop()
	#	self.species_nodes.append(tmp.left)
	#	self.species_nodes.append(tmp.right)
	
	def reset_species_nodes(self):
		self.species_nodes = [self.root]
		self.species_tips = []

	def update_species_nodes(self, method="bf"):
		if method=="bf":
			target = self.species_nodes.pop(0)
		elif method == "df":
			target = self.species_nodes.pop()

		left = target.left
		right = target.right

		if left.is_terminal():
			self.species_tips.append(left)
		else:
			self.species_nodes.append(left)
		if right.is_terminal():
			self.species_tips.append(right)
		else:
			self.species_nodes.append(right)

				
	def breadth_first_search(self):
		self.reset_species_nodes()
		yield self.list_species()	#null model

		while self.species_nodes:	#alternative models
			self.update_species_nodes()			

			yield self.list_species()
	

if __name__=="__main__":
	with open(sys.argv[1], "r") as f:
		for line in f:
			tr = parse_newick(line.rstrip("\n"))
			gtr = GuideTree(tr)
			print tr
			print gtr
			#print gtr.list_species()
		
			#print gtr.update_species_nodes()
			#print gtr.list_species()

			for l in gtr.breadth_first_search():		
				print l


