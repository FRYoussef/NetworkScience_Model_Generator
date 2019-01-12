import sys
from model import ErdosRenyiModel, BarabasiAlbertModel

"""
This script supports the following command line parameters:

	-model:e|b	To run (e)rdos or (b)arabasi model; default value (e)

	-p:#		Probability of Erdos model; default [ErdosRenyiModel.SUB_CRITICAL, 
				ErdosRenyiModel.CRITICAL, 
				ErdosRenyiModel.SUPER_CRITICAL, ErdosRenyiModel.CONECTED]

	-nodes:#	The number of the graph's nodes: default value [500, 1000, 5000]

	-m:#		The number of links in Barabasi model; default values [3, 4]

	-sims:#		The number of simulations; default value 10

E.G: python main.py -model:b -m:4,5 -sims:3

"""
#
# Author: Youssef El Faqir El Rhazoui
# Date: 16/11/2018
# Distributed under the terms of the GPLv3 license.
#


ERDOS = 0
BARABASI = 1

def run_erdos(args):
	states = args['p'] if args['p'] is not -1 else args['state']
	aux = '{}_stats.txt'.format(args['out_name'])
	with open(aux, 'w+', encoding='utf8') as file:
		for node in args['nodes']:
			for st in states:

				er = ErdosRenyiModel(num_nodes = node, state = st, 
						p = -1 if args['p'] is -1 else st, sims = args['sims'])

				er.run('{0}_n={1}_p={2}.gml'.format(args['out_name'], 
					er.num_nodes, er.p))
				_str = er.__str__()
				print(_str)
				file.write(_str)

def run_barabasi(args):
	aux = '{}_stats.txt'.format(args['out_name'])
	with open(aux, 'w+', encoding='utf8') as file:
		for nodes in args['nodes']:
			for links in args['m']:

				ba = BarabasiAlbertModel(m = links, t = nodes - links - 1,
					sims = args['sims'])

				ba.run('{0}_t={1}_m={2}.gml'.format(args['out_name'], 
					ba.t, ba.m))
				_str = ba.__str__()
				print(_str)
				file.write(_str)



def main(*args):
	opts = {'model': ERDOS, 
			'state': [ErdosRenyiModel.SUB_CRITICAL, ErdosRenyiModel.CRITICAL, 
				ErdosRenyiModel.SUPER_CRITICAL, ErdosRenyiModel.CONECTED],
			'p': -1,
			'nodes': [500, 1000, 5000],
			'm': [3, 4],
			'sims': 10,
			'out_name': 'erdos_renyi'}
	local_args = sys.argv[1:]

	for arg in local_args:
		option, sep, value = arg.partition(':')
		if option.startswith('-'):
				option = option[1:]
				if option == 'model':
					opts[option] = value or input(
						  'Enter the model (e or b): ')
					if opts[option] is 'e':
						opts[option] = ERDOS
					elif opts[option] is 'b':
						opts[option] = BARABASI
						opts['out_name'] = 'barabasi_albert'
					else:
						print('value \'{}\' is not allowed'
							.format(opts[option]))
						return 1
					continue
				elif option == 'p':
					opts[option] = value or input(
						  'Enter a probality (number): ')
					opts[option] = opts[option].split(',')
					opts[option] = list(map(lambda x: float(x), opts[option]))
					opts[option] = list(filter(lambda x: x >= 0 and x <= 1, 
						opts[option]))
					continue
				elif option == 'm':
					opts[option] = value or input(
						  'Enter a m (number): ')
					opts[option] = opts[option].split(',')
					opts[option] = list(map(lambda x: int(x), opts[option]))
					continue
				elif option == 'nodes':
					opts[option] = value or input(
						  'Enter the number of nodes: ')
					opts[option] = opts[option].split(',')
					opts[option] = list(map(lambda x: int(x), opts[option]))
					continue
				elif option == 'sims':
					opts[option] = value or input(
						  'Enter the number of simulations: ')
					opts[option] = int(opts[option])
					continue

	if opts['model'] is ERDOS:
		run_erdos(opts)
	elif opts['model'] is BARABASI:
		run_barabasi(opts)



sys.exit(main())