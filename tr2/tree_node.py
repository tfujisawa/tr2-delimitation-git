#binary tree
#for tree decomposition
#with static method
#22/01/13
import string

class TreeNode:
	def __init__(self, name="", length=None, parent=None, str=None):#length must be None or 0.0??? 22/10/13
		#initial formats
		self.name = name
		self.length = length
		self.parent = parent
		self.left = None
		self.right = None
		self.label = None
		
	def __str__(self):
		if self.is_terminal():
			if self.name:
				if type(self.name) == type([]) and len(self.name)==1:
					str = "%s" % self.name[0]
				elif type(self.name) == type([]) and len(self.name) > 1:
					str = "<>".join([n for n in self.name])
				else:
					str = "%s" % self.name
			else:	
				str = " "
			if not self.length == None:
				str += ":%0.3f" % self.length

			if self.is_root():
				str += ";"
			return str
				
		else:
			str = "("
			str += self.left.__str__() + ","
			str += self.right.__str__()
			str += ")"
			if self.label:
				str += self.label
			if self.length:
				str += ":%0.3f" % self.length
			
			if self.is_root():
				str += ";"

			return str
	
	def is_terminal(self):
		return (self.left==None and self.right==None)
	
	def is_root(self):
		return (self.parent==None)
	
	def traverse(self):
		yield (self)
		if self.left:
			for node in self.left.traverse():
				yield (node)
		if self.right:
			for node in self.right.traverse():
				yield (node)
	def clone(self):
		nod = TreeNode(name=self.name, length=self.length)
		if self.left:
			nod.left = self.left.clone()
			nod.left.parent = nod
		if self.right:
			nod.right = self.right.clone()
			nod.right.parent = nod
		return nod	

	@staticmethod	#??? classmethod ???
	def tree_from_newick(str):
		node = TreeNode()
		
		str = str.strip().strip(';')	#remove front and last space and semicolon
		colon = str.rfind(':')
		node.length = float(str[colon+1:])	#use last number after ": "as branch length
			
		str = str[:colon].strip()
		if str.count('(') == 0:	#terminal, replace name with tip name
			node.name = str.strip()
		else:	#internal
			str = str[1:-1]	#remove outer parentheses
				
			#new part... obtains tip names by removing "(", ")", "," and ":" from str
			tmpstr = string.replace(string.replace(str, "(", ""), ")", "")
			node.name = [tmp.split(":")[0] for tmp in tmpstr.split(",")]
			
			#recursively create subtrees
			index = 0
			pardepth = 0
			for i in range(len(str)):
				if str[i] == '(':
					pardepth += 1
				elif str[i] == ')':
					pardepth -= 1
				elif str[i] == ',' and pardepth == 0:
					node.left=TreeNode.tree_from_newick(str[index:i])
					node.left.parent = node
					index = i+1
			node.right=TreeNode.tree_from_newick(str[index:len(str)-1])	#indent twice...??
			node.right.parent = node
			
		return node
				
if __name__ == "__main__":
	import sys
	
	with open(sys.argv[1], "r") as f:
		for line in f:
			print line
			
			#tr = TreeNode(str=line)
			tr = TreeNode.tree_from_newick(line)
			#print tr.name
			#print tr.is_terminal()
			print tr
			for node in tr.traverse():
				print node.name#, node.is_root(), node.is_terminal()
				
