#function to parse newick format
#31/07/13

import sys
from tree_node import TreeNode

#implementation using modified Dijkstra's 2 stack algorithm

op = ("(", ")", ":", ",", ";")
opprec = {"(":0, ")":0, ":":2, ",":1, ";":0}
	
def read_newickstr(strg):
	
	#print strg
	token = ""	
	for ch in list(strg):
		if ch in op:
			if token:
				yield token
			yield ch
			token = ""
		elif ch == " ":	#skip whitespace
			continue
		else:
			token += ch

def operate(op, l, r):
	if op == ":":
		return "%s:len=%s" % (l, r)
	elif op == ",":
		return "node(%s, %s)" % (l, r)

def operate_tn(op, l, r):
	if op == ":": #':' operator adds the length of branch (and create node if no node exists)
		if isinstance(l, TreeNode):
			l.length = float(r)
			return l
		else:
			nod = TreeNode(name=[l], length=float(r))	#added [] 18/10/13...to give all tip names as node.name
			return nod	
		
	elif op == ",": #',' operator creat a subtree from 2 nodes
		if not isinstance(l, TreeNode):
			l = TreeNode(name=[l])	#added [] 18/10/13...to give all tip names as node.name
			
		if not isinstance(r, TreeNode):
			r = TreeNode(name=[r])	#added [] 18/10/13...to give all tip names as node.name
		
		nod = TreeNode(name=l.name+r.name)	#added [] 18/10/13...to give all tip names as node.name. need refactoring.
		l.parent = nod
		r.parent = nod
		nod.left, nod.right = l, r
		
		return nod

def parse_newick(strg):
	stackval = []
	stackop = []

	lasttoken = ""
	for token in read_newickstr(strg):
		#print stackop
		#print stackval
		#print lasttoken, token
		if token in op:	#token is an operator
			if token == ";":	#end of string
				while stackop:
					curop = stackop.pop()
					right = stackval.pop()
					left = stackval.pop()
					
					#val = operate(curop, left, right)
					val = operate_tn(curop, left, right)
					stackval.append(val)

			elif token == "(":	#right parenthesis
				stackop.append(token)
			elif token == ")":	#left parenthesis
				while stackop[-1] != "(":
					curop = stackop.pop()
					right = stackval.pop()
					left = stackval.pop()
					
					#val = operate(curop, left, right)
					val = operate_tn(curop, left, right)
					#print val
					stackval.append(val)
				stackop.pop(-1)
 
			else:	#";" or "," operator 
				if stackop:
					if opprec[token] >= opprec[stackop[-1]]:
						stackop.append(token)
					else:
						curop = stackop.pop()
						right = stackval.pop()
						left = stackval.pop()
					
						#val = operate(curop, left, right)
						val = operate_tn(curop, left, right)
						#print val
						stackop.append(token)
						stackval.append(val)
				else:
					stackop.append(token)
			lasttoken = token
	
		else:	#token is not an operator
			if lasttoken != ")":	#append if previous token is not ")"
				stackval.append(token)
			else:	#if previous token is ")", node label is added
				if isinstance(stackval[-1], TreeNode):
					pass					
					#stackval[-1].label = token
			lasttoken = token
	
			

	if stackval:
		return stackval.pop()
	else:
		return ""

def test_parse():
	tr = ["", ";", "();"]
	tr.extend(["(t8,t7);","t1:1.0;", "(t1:1.0, t2:1.1):1.0;"])
	tr.append("((t8,t7),((t5,t1),((t4,(t2,(t9,t10))),(t6,t3))));")
	tr.append("((((t3:0.55060,t1:0.76907):0.97137,t4:0.0039527):0.39322,t5:0.64626):0.12201,t2:0.0098804);")
	tr.append("((((t3:0.55060,t1:0.76907):0.97137,t4:0.0039527):0.39322,t5:0.64626):0.12201,t2:0.0098804):1.0;")
	tr.append("(((t3:0.5891516672,((t5:0.1585097628,(t1:0.006379363945,t9:0.006379363945):0.1521303988):0.04108452768,(t2:0.1904483613,t6:0.1904483613):0.009145929174):0.3895573768):0.324444488,(t7:0.05090455425,t8:0.05090455425):0.862691601):0.07187695207,(t10:0.1627158809,t4:0.1627158809):0.8227572264):1.0;")

	tr.append("(t1, t2, t3);")#non-binary tree???	handle exception...
	tr.append("( t1: 0.1, t2 :0.1);")#erratic space???
	tr.append("( t1: 0. 01, t2 :0. 0 1);")#erratic space2???
	
	tr.append("((1,2)A, (3,4)B);")#node labels	
	tr.append("((1:1,2:1)A:1, (3:1,4:1)B:1);")#nodee labels + branch lengths
	tr.append("((t8,t7)A,((t5,t1)B,((t4,(t2,(t9,t10))),(t6,t3))))Root;")	#more complicated example
	tr.append("((t8:1,t7:1)CladeA:1,((t5:1,t1:1):1,((t4:1,(t2:1,(t9:1,t10:1):1):1):1,(t6:1,t3:1):1):1)CladeB:1);")

	#tr.append("((t1, t2);")	#parentheses don't match
	
	for t in tr:
		print parse_newick(t)#.__class__
		print t

	
if __name__=="__main__":
	tr00 = "((t8,t7),((t5,t1),((t4,(t2,(t9,t10))),(t6,t3))));"
	tr01 = "((t1:1, t2:2):3, t3:4):1;"
	tr = "(((t3:0.5891516672,((t5:0.1585097628,(t1:0.006379363945,t9:0.006379363945):0.1521303988):0.04108452768,(t2:0.1904483613,t6:0.1904483613):0.009145929174):0.3895573768):0.324444488,(t7:0.05090455425,t8:0.05090455425):0.862691601):0.07187695207,(t10:0.1627158809,t4:0.1627158809):0.8227572264):1.0;"
	#print [t for t in read_newickstr(tr)]
	#print parse_newick(tr)
	
	test_parse()

	#print isinstance(TreeNode(), TreeNode)
	#print type(TreeNode()) == TreeNode
