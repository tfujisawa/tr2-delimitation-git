import sys
import itertools

try:
	import numpy
	from scipy import misc
	from scipy import optimize
except ImportError:
	print "ImportError:"
	print "Python library numpy / scipy is not installed."
	sys.exit()

#trinomial distribution in log
def trinomial_dist_log(n1, n2, n3, prob=numpy.ones([3])/3):
	n = numpy.array([n1,n2,n3])
	N = numpy.sum(n)
	C1 = numpy.sum(numpy.log(numpy.arange(1, N+1)))
	C2 = numpy.where(n!=0, map(lambda x: numpy.sum(numpy.log(numpy.arange(1,x+1))), n), 0)	#??????
	C = C1 - numpy.sum(C2)
	
	return C + numpy.sum(n*numpy.log(prob))

#trinomial distribution
def trinomial_dist(n1,n2,n3, prob=numpy.ones([3])/3):
	n = numpy.array([n1,n2,n3])
	N = numpy.sum(n)
	C1 = numpy.sum(numpy.log(numpy.arange(1, N+1)))
	C2 = numpy.where(n!=0, map(lambda x: numpy.sum(numpy.log(numpy.arange(1,x+1))), n), 0)	#??????
	C = C1 - numpy.sum(C2)
	
	return numpy.exp(C+numpy.sum(n*numpy.log(prob)))

#distribution of null model A, trinomial density	
class NullLikelihood:
	def __init__(self):
		self.prob = numpy.ones([3])/3
		self.eps = numpy.finfo(float).eps

	def dist(self, *count):
		return trinomial_dist_log(*count, prob=self.prob)

	def aic(self, *count):
		return -2*trinomial_dist_log(*count, prob=self.prob)

	def calculate(self, counts):
		return sum((self.aic(*count) for count in counts))		
		#return sum((self.dist(*count) for count in counts))		
		#return numpy.sum([self.dist(*count) for count in counts])

#distribution of alternative model A, trinomial density with skewed probability
def alt_dist_log(lambd, n1 ,n2, n3):
	e = numpy.exp(-lambd)
	prob = numpy.array([1-2*e/3, e/3, e/3]).flatten()	#make sure prob is 1D vector...
	
	return trinomial_dist_log(n1, n2, n3, prob=prob)

#return negative value for minimization
def negative(func):	
	def _negative(*args, **kw):
		return -func(*args, **kw)
	return _negative

#return negative value if argument is positive.	target function for minimization
def target_func(func):
	def target(*args, **kw):
		if args[0] < 0:
			return float("inf")
		else:
			return -func(*args, **kw)
	return target

#alternative likelihood A with parameter optimization
def alt_dist_log_opt(n1, n2, n3):
	opt = optimize.fmin(target_func(alt_dist_log), x0=1, args=(n1,n2,n3), full_output=True, disp=False)
	
	return -opt[1]

#mean of three possible combinations. average-then-optimize lambda (single parameter) 05/02/14
def alt_dist_log_ave(lambd, n1, n2, n3):
	d1 = numpy.exp(alt_dist_log(lambd, n1, n2, n3)) 
	d2 = numpy.exp(alt_dist_log(lambd, n2, n1, n3))
	d3 = numpy.exp(alt_dist_log(lambd, n3, n1, n2))

	return numpy.log((d1+d2+d3)/3)

#optimize alt_dist_log_ave
def alt_dist_log_ave_opt(n1, n2, n3):
	opt = optimize.fmin(target_func(alt_dist_log_ave), x0=1, args=(n1,n2, n3), full_output=True, disp=False)

	return -opt[1]


#mean of three possible combination. optimize-then-average(3 parameters) ...???20/12/13
def mean_dist(n1,n2,n3):
	d1 = numpy.exp(alt_dist_log_opt(n1,n2,n3))	#take arithmetic mean or geometric mean????
	d2 = numpy.exp(alt_dist_log_opt(n2,n1,n3))
	d3 = numpy.exp(alt_dist_log_opt(n3,n1,n2))

	return numpy.log((d1+d2+d3)/3)

	#d1 = alt_dist_log_opt(n1,n2,n3)	#take arithmetic mean or geometric mean????
	#d2 = alt_dist_log_opt(n2,n1,n3)	#take arithmetic mean!! ... 05/02/14
	#d3 = alt_dist_log_opt(n3,n1,n2)
	#return (d1+d2+d3)/3

	

#take weighted average of each case...???20/12/13
def weighted_mean_dist(n1,n2,n3):
	N = n1+n2+n3
	d1 = alt_dist_log_opt(n1,n2,n3)*n1/N
	d2 = alt_dist_log_opt(n2,n1,n3)*n2/N
	d3 = alt_dist_log_opt(n3,n1,n2)*n3/N
	return (d1+d2+d3)


class AltLikelihood:
	def __init__(self, model="3L"):
		self.cache = {}
		#self.dist = alt_dist_log_opt
		#self.dist = self.memoize(alt_dist_log_opt)
				
		#self.dist = weighted_mean_dist		
		#self.dist = self.memoize(weighted_mean_dist)	#which is best likelihood function???
		
		#self.dist = self.memoize(mean_dist)	#model with separate optimiazation of 3 parameters
		#self.np = 3

		if model == "1L":
			self.dist = self.memoize(alt_dist_log_ave_opt)	#model with single parameter+averaging 3 orders
			self.np = 1
		elif model == "3L":
			self.dist = self.memoize(mean_dist)	#model with separate optimiazation of 3 parameters
			self.np = 3

	
	#memoization of likelihood calculation, caching results of function
	def memoize(self, func):
		def memoized(*args):
			if args in self.cache:
				return self.cache[args]
			else:
				val = func(*args)
				self.cache[args] = val
				return val

		return memoized		

	def aic(self, *count):
		return -2*self.dist(*count) + 2*self.np	#number of parameters...??? 2 or 6

	def calculate(self, counts):
		#return sum((self.dist(*count) for count in counts))
		#return sum((self.dist(*(sorted(count)[::-1])) for count in counts))	#sorted		
		return sum((self.aic(*(sorted(count)[::-1])) for count in counts))	#sorted, AIC
		

class MixedLikelihood:
	def __init__(self):
		self.nullik = NullLikelihood()
		self.altlik = AltLikelihood()
 
		self.likfunc = {}
		self.likfunc["NULL"] = self.nullik.aic
		self.likfunc["ALT"] = self.altlik.aic
		self.likfunc[None] = lambda *x: 0	#return 0 if a triple doesn't exit

	def calculate(self, counts, categ):
		return sum((self.likfunc[cat](*(sorted(cn)[::-1])) for cn, cat in itertools.izip(counts, categ)))
		#return sum((self.likmodel[cat].aic(*(sorted(cn)[::-1])) for cn, cat in itertools.izip(counts, categ)))
				
		#return sum((self.likmodel[cat].dist(*(sorted(cn)[::-1])) for cn, cat in itertools.izip(counts, categ)))
		#return sum((self.likmodel[cat].dist(*cn) for cn, cat in itertools.izip(counts, categ)))
		

if __name__ == "__main__":

	test = [[5, 4, 6], [8, 3, 4], [4, 7, 4]]
	#test = [numpy.random.multinomial(15, numpy.ones([3])/3) for i in range(10)]
	
	#e = numpy.exp(-0.5)
	#prob = numpy.array([1-2*e/3, e/3, e/3]).flatten()
	#test = [numpy.random.multinomial(15, prob) for i in range(10)]
	print test
	
	print trinomial_dist_log(*test[2])

	nlik0 = NullLikelihood()
	print "null:", nlik0.calculate(test)

	altlik = AltLikelihood()
	print "alt:", altlik.calculate(test)

	mixlik = MixedLikelihood()
	cat1 = ["NULL"]*len(test)
	cat2 = ["ALT"]*len(test)
	print "mixed:", mixlik.calculate(test, cat2)

	#res = []
	#for i in range(100):
	#	#test = [numpy.random.multinomial(15, numpy.ones([3])/3) for i in range(10)]
	#	e = numpy.exp(-0.01)
	#	prob = numpy.array([1-2*e/3, e/3, e/3]).flatten()
	#	test = [numpy.random.multinomial(15, prob) for i in range(10)]	
	#	nlik = nlik0.calculate(test)
	#	alik = altlik.calculate(test)
	#	res.append(alik-nlik)
	
	#print numpy.bincount(numpy.array(res) > 9.1535)
	#print "LR:" + str(alik-nlik)

