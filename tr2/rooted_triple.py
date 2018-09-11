#count triples
#24/01/13
import sys

from tree_node import TreeNode
from newick_io import *

class RootedTriple:
	def __init__(self, left, right, up):
		self._up = frozenset([up])
		self._down = frozenset([left, right])
		self._members = self._up|self._down
		self._topology = frozenset([self._up, self._down])
		
	def __str__(self):
		return ("%s,%s|%s" % tuple(list(self._down)+list(self._up)))
		
	def __eq__(self, trpl):
		return (self._up==trpl._up and self._down==trpl._down)
	
	def members(self):
		return self._members		
		#return (self.up | self.down)
	
	def topology(self):
		return self._topology
		#return frozenset([self.up, self.down])

	@staticmethod
	def triples_from_tree(tr):
		all = tr.name
		for node in tr.traverse():
			if not node.is_root() and not node.is_terminal():
				left = node.left.name
				right = node.right.name
			
				if not left.__class__ == type([]):
						left = [left]
				if not right.__class__ == type([]):
						right = [right]
				
				##operation with set
				if set(node.name) <= set(all):
					up = list(set(all)-set(node.name))
				
				#print left, right, up
				for l in left:
					for r in right:
						for u in up:
							yield RootedTriple(*tuple([l, r, u]))
							
if __name__=="__main__":
	with open(sys.argv[1], "r") as f:
		for line in f:
			print line
			
			tr = parse_newick(line)
			#tr = TreeNode.tree_from_newick(line)
			print len(tr.name)
				
			for i, trpl in enumerate(RootedTriple.triples_from_tree(tr)):
				#print i+1, trpl			
				print i+1, trpl, trpl.members(), trpl.topology()
				#print RootedTriple(*trpl)


#incorrect implementation....
def count_triples_incorrect(tr):	#incorrect???
	for node in tr.traverse():
		if not node.is_root() and not node.is_terminal():
			left = node.left.name
			right = node.right.name
			
			if node.parent.left == node:
				up = node.parent.right.name
			else:
				up = node.parent.left.name
			
			print up
			
			if not left.__class__ == type([]):
				left = [left]
			if not right.__class__ == type([]):
				right = [right]
			if not up.__class__ == type([]):
				up = [up]
			
			print node.name, node.left.name, node.right.name
			for l in left:
				for r in right:
					for u in up:
						yield tuple([l, r, u])
				
