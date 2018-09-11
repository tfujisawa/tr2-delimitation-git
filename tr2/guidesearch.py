#code for search using guide tree
import sys

from likmodel import *
from bayesmodel import *
from guidetree import *
from triple_utils import *

#search 1. greedy search using breadth first traverse
def greedy_search(trpl, gtree):
	mixlik = MixedLikelihood()

	gtree.reset_species_nodes()
	minscore = mixlik.calculate(trpl.values(), categorize_triples(trpl, gtree.list_species())) #make this a function
	mindelimit = gtree.list_species()

	while gtree.species_nodes:
		prev_nodes = [nod for nod in gtree.species_nodes]
		prev_tips = [nod for nod in gtree.species_tips]

		gtree.update_species_nodes()	#update nodes with breadth first fashion

		group = gtree.list_species()
		newscore = mixlik.calculate(trpl.values(), categorize_triples(trpl, group))

		if newscore < minscore:	#accept new score if it is smaller than min.
			minscore = newscore
			mindelimit = group

			print "acceptted", minscore

		else:	#reject and ignore target node from now on if new score is larger than min.
			gtree.species_nodes = prev_nodes
			gtree.species_tips = prev_tips

			gtree.species_tips.append(gtree.species_nodes.pop(0))

			print "rejected", newscore, minscore

	print minscore
	return gtree

#search 2. recursive divide&conquer algorithm (call it dynamic programming???)
def recursive_search(trpl, gtree):

	def find_best_nodes(gtree, likmodel, trpl):
		if gtree.root.is_terminal():	#if terminal, just return list of species
			print "terminal"
			return gtree.species_nodes + gtree.species_tips
		
		elif len(gtree.root.name) <= 2:	#if #tips less than or equal to 3, evaluate likelihood
			print "internal triplet"

			#score of root of triplet
			group1 = gtree.list_species()
			score1 = likmodel.calculate(trpl.values(), categorize_triples(trpl, group1))

			prev_nodes = [n for n in gtree.species_nodes]
			prev_tips = [n for n in gtree.species_tips]

			gtree.update_species_nodes()

			#score of children of root
			group2 = gtree.list_species()
			score2 = likmodel.calculate(trpl.values(), categorize_triples(trpl, group2))
			
			print score1, score2
			#eps = numpy.finfo(float).eps
			#gtree.root.label = str((score1+eps)/(score2+eps))
			if score1 <= score2:	#if score doesn't improve, return root grouping
				return prev_nodes + prev_tips
			elif score1 > score2:	#else, return children grouping
				return gtree.species_nodes + gtree.species_tips

		else:	#else, run recursively
			print "internal"
			group1 = gtree.list_species()
			score1 = likmodel.calculate(trpl.values(), categorize_triples(trpl, group1))

			lgtree = GuideTree(gtree.root.left)
			rgtree = GuideTree(gtree.root.right)

			nodes2 = find_best_nodes(lgtree, likmodel, trpl) + find_best_nodes(rgtree, likmodel, trpl)
			group2 = {}
			for i, node in enumerate(nodes2):
				for n in node.name:
					group2[n] = i + 1

			score2 = likmodel.calculate(trpl.values(), categorize_triples(trpl, group2))
			
			print score1, score2
			#eps = numpy.finfo(float).eps
			#gtree.root.label = str((score1+eps)/(score2+eps))
			if score1 <= score2:	#if score doesn't improve, return root grouping
				return gtree.species_nodes + gtree.species_tips
			elif score1 > score2:	#else, return recursive result
				return nodes2
	
	mixlik = MixedLikelihood()
	gtree.reset_species_nodes()	

	best = find_best_nodes(gtree, mixlik, trpl)

	gtree.species_tips = [nod for nod in best if nod.is_terminal()]
	gtree.species_nodes = [nod for nod in best if not nod.is_terminal()]
	return gtree

#search 2.1. modified version of search2
def recursive_search_D(trpl, gtree):
	
	def find_best_nodes_D(gtree, likmodel, trpl):
		if gtree.root.is_terminal():
			#print "terminal"

			group = gtree.list_species()
		
			if len(group) == 1:
				score = 0.0
			else:
				score = likmodel.calculate(trpl.values(), categorize_triples(trpl, group))
			gtree.score = score			

			return gtree			
			#return 0
		elif len(gtree.root.name) <= 2:	
			#print "internal triplet"
			
			group1 = gtree.list_species()
			score1 = likmodel.calculate(trpl.values(), categorize_triples(trpl, group1))

			prev_nodes = [n for n in gtree.species_nodes]
                        prev_tips = [n for n in gtree.species_tips]

                        gtree.update_species_nodes()

			group2 = gtree.list_species()
			score2 = likmodel.calculate(trpl.values(), categorize_triples(trpl, group1))

			print score1, score2, gtree.root
			gtree.root.label =  str((score1-score2)/misc.comb(len(gtree.root.name), 3))
			if score1 <= score2:
				gtree.score = score1
				gtree.species_nodes = prev_nodes
				gtree.species_tips = prev_tips
				return gtree
				#return score1
			elif score1 > score2:
				gtree.score = score2
				return gtree
				#return score2

		else:
			#print "internal tree"
			
			group1 = gtree.list_species()
			score1 = likmodel.calculate(trpl.values(), categorize_triples(trpl, group1))

			lgtree = GuideTree(gtree.root.left)
			rgtree = GuideTree(gtree.root.right)

			prev_nodes = [n for n in gtree.species_nodes]
                        prev_tips = [n for n in gtree.species_tips]

                        gtree.update_species_nodes()

			group2 = gtree.list_species()

			score2m = likmodel.calculate(trpl.values(), categorize_triples(trpl, group2, alt_only=True))
			score2l = find_best_nodes_D(lgtree, likmodel, trpl)
			score2r = find_best_nodes_D(rgtree, likmodel, trpl)

			score2 = score2m + score2l.score + score2r.score

			print score1, score2, gtree.root
			gtree.root.label = str((score1-score2)/misc.comb(len(gtree.root.name), 3))
			if score1 <= score2 or numpy.isclose(score1, score2):	#if score doesn't improve, return original
				gtree.score = score1
				gtree.species_nodes = prev_nodes
				gtree.species_tips = prev_tips
				
				return gtree
				#return score1
			elif score1 > score2 and not numpy.isclose(score1, score2):	#if score improves, return updated one
				gtree.score = score2
				
				gtree.species_nodes = score2l.species_nodes + score2r.species_nodes
				gtree.species_tips = score2l.species_tips + score2r.species_tips
	
				return gtree
				#return score2
			
	#mixlik = MixedLikelihood()
	ppmodel = ModelPosterior()
	gtree.reset_species_nodes()	

	best = find_best_nodes_D(gtree, ppmodel, trpl)

	#for n in best.species_nodes+best.species_tips:
	#	n.label = "*"

	return best

def create_table(gtree):
	text="species\tsample\n"
	for i, sp in enumerate(gtree.species_nodes + gtree.species_tips):
		for n in sp.name:		
			text += "%d\t%s\n" % (i+1, n)

	return text.rstrip("\n")

if __name__=="__main__":
	with open(sys.argv[1], "r") as f:
		trpl = count_triples(f)

	with open(sys.argv[2], "r") as f:
		for i, line in enumerate(f):
			if i > 1:
				print "There are multiple trees in input guide tree file, %s" % sys.argv[2]
				print "First tree is used."
				break	
			gtree = GuideTree(parse_newick(line.rstrip("\n")))
	
	#test of greedy search
	#restree = greedy_search(trpl, gtree)
	#print restree.list_species()

	#restree2 = recursive_search(trpl, gtree)
	restree2 = recursive_search_D(trpl, gtree)
	
	#for nod in restree2.species_nodes:
	#	nod.label = "*" + nod.label
	
	print restree2
	print create_table(restree2)

	
			
		

		
