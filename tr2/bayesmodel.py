import sys
import itertools

try:
	import numpy
	from scipy import misc
	from scipy import integrate
	from scipy import optimize
	from scipy import special

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
	#C = 1
	
	return C + numpy.sum(n*numpy.log(prob))

#trinomial distribution
def trinomial_dist(n1,n2,n3, prob=numpy.ones([3])/3):
	n = numpy.array([n1,n2,n3])
	N = numpy.sum(n)
	C1 = numpy.sum(numpy.log(numpy.arange(1, N+1)))
	C2 = numpy.where(n!=0, map(lambda x: numpy.sum(numpy.log(numpy.arange(1,x+1))), n), 0)	#??????
	C = C1 - numpy.sum(C2)
	#C = 1

	return numpy.exp(C+numpy.sum(n*numpy.log(prob)))

#distribution of alternative model A, trinomial density with skewed probability
def alt_dist_log(lambd, n1 ,n2, n3):
	e = numpy.exp(-lambd)
	prob = numpy.array([1-2*e/3, e/3, e/3]).flatten()	#make sure prob is 1D vector...
	
	return trinomial_dist_log(n1, n2, n3, prob=prob)

#alternative model without log-transform
def alt_dist(lambd, n1, n2, n3):
	e = numpy.exp(-lambd)
	prob = numpy.array([1-2*e/3, e/3, e/3])
	
	return trinomial_dist(n1,n2,n3, prob=prob)

def alt_dist_integrate(n1, n2, n3, L=5):
	i = integrate.quad(alt_dist, 0, L, args=(n1,n2,n3))

	return i[0]

def ibeta(a, b, x):
	return special.betainc(a, b, x)*special.beta(a, b)


def alt_dist_betaintegrate(n1, n2, n3, L=5):
	n = numpy.array([n1,n2,n3])
	N = numpy.sum(n)
	
	if n1 == N:
		return alt_dist_integrate(n1, n2, n3, L)
	else:
		C1 = numpy.sum(numpy.log(numpy.arange(1, N+1)))
		C2 = numpy.where(n!=0, map(lambda x: numpy.sum(numpy.log(numpy.arange(1,x+1))), n), 0)	#??????
		lC = C1 - numpy.sum(C2)

		la = numpy.log(0.5)*(N-n1)
		
		lB = numpy.log(ibeta(N-n1, n1+1, 2/3.0)-ibeta(N-n1, n1+1, 2*numpy.exp(-L)/3.0))

		return numpy.exp(la+lC+lB)


def alt_posterior(n1, n2, n3, L=5):
	i1 = alt_dist_betaintegrate(n1,n2,n3, L=L)
	i2 = alt_dist_betaintegrate(n2,n1,n3, L=L)
	i3 = alt_dist_betaintegrate(n3,n2,n1, L=L)

	return [i1,i2,i3]

def model_posterior(n1,n2,n3, L=5):
	i_a = sum(alt_posterior(n1,n2,n3,L=L))
	i_n = 3*L*trinomial_dist(n1,n2,n3)
	
	i_a = i_a if i_a != 0 else numpy.finfo(i_a).tiny
	i_n = i_n if i_n != 0 else numpy.finfo(i_n).tiny

	d = i_a + i_n
	#print "i_a:%f , i_n: %f" % (i_a, i_n)
	#print "%d, %d, %d" % (n1,n2,n3)
	#print i_a/d > numpy.finfo(0.0).tiny, i_n/d > numpy.finfo(0.0).tiny

	return {"ALT":i_a/d, "NULL":i_n/d, None:1.0}

class ModelPosterior:
	def __init__(self):
		self.cache = {}
		self.f = self.memoize(model_posterior) 

	def __call__(self, *N):
		return self.f(*N)

	def memoize(self, func):
		def memoized(*args):
			if args in self.cache:
				#print "memoized"
				return self.cache[args]
			else:
				val = func(*args)
				self.cache[args] = val
				return val

		return memoized		

	def log_posterior(self, model, *N):
		return numpy.log(self.f(*N)[model])

	def calculate(self, counts, categ):
		return -sum((self.log_posterior(cat, *cn) for cn, cat in itertools.izip(counts, categ)))

if __name__=="__main__":

	test0 = [0,0,0]
	print test0
	print alt_dist_betaintegrate(*test0)
	print alt_posterior(*test0)
	print model_posterior(*test0)

	test = [5,4,6]
	print test
	print alt_dist_betaintegrate(*test)
	print alt_posterior(*test)
	print model_posterior(*test)
	
	test2 = [10,2,3]
	print test2
	print alt_dist_betaintegrate(*test2)
	print model_posterior(*test2)

	test3 = [500, 255, 245]
	print test3
	print alt_dist_betaintegrate(*test3)
	print model_posterior(*test3)

	pp = ModelPosterior()
	print pp(*test2)

	#sys.exit()

	nloci = 18
	ntrial = 100
	#for l in range(0, 5, 1):
	for l in [0.0, -0.162, -0.357, -0.598, -0.916, -1.386, -2.302]:
		#test = [numpy.random.multinomial(15, numpy.ones([3])/3) for i in range(10)]
		e = numpy.exp(l)
		prob = numpy.array([1-2*e/3, e/3, e/3]).flatten()
		test = [numpy.random.multinomial(nloci, prob) for i in range(ntrial)]
		#test = [tuple(t) for t in test]
		#print test[0:10]

		res = numpy.array([pp(*N)["ALT"] for N in test])

		#print res, 1-res
		#print res > 1-res
		print 1-2*e/3, numpy.count_nonzero(res > 1-res)/float(ntrial)
		#for r in res:
		#	print r
	
		print "alt:", pp.calculate(test, ["ALT"]*ntrial)
		print "null:", pp.calculate(test, ["NULL"]*ntrial)


