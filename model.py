import networkx as nx
import random
import math
from llist import sllist
import timeit

#
# Author: Youssef El Faqir El Rhazoui
# Date: 16/11/2018
# Distributed under the terms of the GPLv3 license.
#


DEBUG = 0

class Model:
	mean_hub_degree = 0
	mean_density = 0
	mean_distance = 0
	mean_clustering_coeff = 0
	mean_connected_comp = 0
	mean_edges = 0
	mean_degree = 0


	def __init__(self, num_nodes, sims):
		super(Model, self).__init__()
		self.sims = sims
		self.num_nodes = num_nodes


	def calculate_metrics(self, graph):
		self.mean_edges += nx.number_of_edges(graph)
		self.mean_hub_degree += len(nx.degree_histogram(graph))-1
		self.mean_clustering_coeff += nx.average_clustering(graph)
		self.mean_density += nx.density(graph)
		cc = nx.number_connected_components(graph)
		avg = float('inf')
		if not math.isinf(self.mean_distance) and cc is 1:
			#avg = nx.average_shortest_path_length(graph)
			avg = calculate_avg_distance(graph)
		self.mean_connected_comp += cc
		self.mean_distance += avg


	def run(self, out_name):
		g = []
		for i in range(self.sims):
			print('Starting simulation {} ...'.format(i+1))
			g = self.create_graph()
			self.calculate_metrics(g)
			print('Simulation {} done!!'.format(i+1))
		self.mean_hub_degree = self.mean_hub_degree / self.sims
		self.mean_density = self.mean_density / self.sims
		self.mean_distance = self.mean_distance / self.sims
		self.mean_clustering_coeff = self.mean_clustering_coeff / self.sims
		self.mean_connected_comp = self.mean_connected_comp / self.sims
		self.mean_degree = self.mean_degree / self.sims
		self.mean_edges = self.mean_edges / self.sims
		self.mean_degree = 2 * self.mean_edges / self.num_nodes
		nx.write_gml(g, out_name)
		g.clear()


class ErdosRenyiModel(Model):
	SUB_CRITICAL = 0
	CRITICAL = 1
	SUPER_CRITICAL = 2
	CONECTED = 3
	

	def __init__(self, num_nodes, state, sims, p):
		super().__init__(num_nodes, sims)
		if p is not -1:
			self.p = p
			return
		if state is self.SUB_CRITICAL:
			self.p = 1 / self.num_nodes * 0.6
		if state is self.CRITICAL:
			self.p = 1 / self.num_nodes
		if state is self.SUPER_CRITICAL:
			# 1/n < log10(n)/n < ln(n)/n | n > 10
			self.p = math.log10(self.num_nodes) / self.num_nodes
		if state is self.CONECTED:
			self.p = math.log(self.num_nodes) / self.num_nodes * 1.6


	def create_graph(self):
		graph = nx.Graph()
		graph.add_nodes_from(range(self.num_nodes))
		for i in range(self.num_nodes):
			for j in range(i + 1, self.num_nodes):
				r = random.randint(0, 1000000) / 1000000
				if r <= self.p:
					graph.add_edge(i, j)

		return graph


	def __str__(self):
		_str = '----------------------------------------------------\n'
		_str += 'Nodes = {0}, Edges = {1}, P = {2}, Sims = {3}\n\n'\
				.format(self.num_nodes, self.mean_edges, self.p, self.sims)
		_str += "Hub degree: {}\n".format(self.mean_hub_degree)
		_str += "<K>: {}\n".format(self.mean_degree)
		_str += "Density: {}\n".format(self.mean_density)   
		_str += "Dinstance: {}\n".format(self.mean_distance)
		_str += "Cluster coefficient: {}\n".format(self.mean_clustering_coeff)
		_str += "Connected components: {}\n".format(self.mean_connected_comp)
		_str += '----------------------------------------------------\n'
		return _str


class BarabasiAlbertModel(Model):


	def __init__(self, m, t, sims):
		super().__init__(m + 1 + t, sims)
		self.m = m
		self.m_0 = m + 1
		self.t = t
		


	def create_graph(self):
		graph = nx.Graph()
		#initial nodes
		graph.add_nodes_from(range(self.m_0))
		for i in range(self.m_0):
			for j in range(i + 1, self.m_0):
				graph.add_edge(i, j)

		# nodes in t time
		for i in range(self.m_0, self.t + self.m_0):
			graph.add_node(i)
			for j in range(self.m):
				n = self.roulette_wheel(graph)
				while n in nx.neighbors(graph, i):
					n = self.roulette_wheel(graph)
				graph.add_edge(i, n)

		#print('Num nodes: {}'.format(nx.number_of_nodes(graph)))
		#print('Num edges: {}'.format(nx.number_of_edges(graph)))
		return graph


	def roulette_wheel(self, graph):
		ds = graph.degree()

		aux, ds = zip(*ds)
		total = sum(ds)
		prop = [d / total for d in ds]
		r = random.randint(0, 1000000) / 1000000
		total = 0
		for i in range(len(prop)):
			total += prop[i]
			if r <= total:
				return i
		return nx.number_of_nodes(graph)-1




	def __str__(self):
		_str = '--------------------------------------------------------------\n'
		_str += 'Nodes = {0}, Edges = {1}, M = {2}, T = {3}, Sims = {4}\n\n'\
				.format(self.num_nodes, self.mean_edges, self.m, self.t, self.sims)
		_str += "Hub degree: {}\n".format(self.mean_hub_degree)
		_str += "Density: {}\n".format(self.mean_density)   
		_str += "Dinstance: {}\n".format(self.mean_distance)
		_str += "Cluster coefficient: {}\n".format(self.mean_clustering_coeff)
		_str += '--------------------------------------------------------------\n'
		return _str
		



def calculate_avg_distance(graph):
	"""
	Based on gephi's code
	"""
	n = nx.number_of_nodes(graph)
	totalPaths = 0
	avgDist = 0
	count = 0

	for s in graph:
		if DEBUG and not count % 500:
			start = timeit.default_timer()
		d = [-1 for i in range(n)]
		d[s] = 0

		Q = sllist()
		Q.appendright(s)
		while Q.size:
			v = Q.popleft()
			edgeIter = nx.neighbors(graph, v)
			for reachable in edgeIter:
				if d[reachable] < 0:
					Q.appendright(reachable)
					d[reachable] = d[v] + 1
				
		reachable = 0
		for num in d:
			if num > 0:
				avgDist += num
				reachable += 1

		totalPaths += reachable
		count += 1
		if DEBUG and not count % 500:
			print('Nodes procesed: {0}   in: {1}'
				.format(count, timeit.default_timer() - start))

	avgDist /= totalPaths
	return avgDist