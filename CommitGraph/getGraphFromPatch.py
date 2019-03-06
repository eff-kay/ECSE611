import json
from enum import Enum
from itertools import combinations
from dijkstar import Graph as dGraph,algorithm
from patch_reader import PatchReader

import os

class EdgeType(Enum):
	CALLING = 0.21
	CALLED = 0.21
	DEF = 0.42
	EQUAL = 1

class Node:
	def __init__(self, name):
		self.name = name
		self.outGoingEdges = set()

	def __str__(self):
		return self.name

class Edge:
	def __init__(self, endingNode, edgeType):
		self.endingNode = endingNode
		self.edgeType = edgeType

	def __str__(self):
		return str(self.edgeType)+ " " +str(self.endingNode)


class Graph:
	def __init__(self):
		self.nodes = set()

	def addNode(self, node):
		self.nodes.add(node)

	def getNodeNames(self):
		return [node.name for node in graph.nodes]



def normalizeMethodNames(name):
	
	tempStr = ''.join(name.split(' '))

	tempStr = tempStr.split('(')

	leftName = tempStr[0]
	params = tempStr[1].split(')')[0]
	rightName = tempStr[1].split(')')[1]
	count= params.count('<')
	params = params.replace(',','', count)
	params = params.split(',')
	strParams = ''.join(params)
	if params==['']:
		finalParamCount=0
	else:
		finalParamCount = len(params)
	finalName = leftName+'('+str(finalParamCount)+')'+rightName
	return finalName




def encryptNode(node, hashForNodes):
	if node.split("==")[-1]==hashForNodes:
		return node
	else:
		node= node+"=="+hashForNodes
		return node


def createGraph(methods, hashForNodes):
	djikstraGraph = dGraph()

	for entry in methods:
		className = list(entry[0].keys())[0]

		calledCalling = list(entry[0].values())

		callingMethods = list(calledCalling[0])

		for i in range(1, len(callingMethods)):

			callingMethods[i-1]= normalizeMethodNames(callingMethods[i-1])
			callingMethods[i] = normalizeMethodNames(callingMethods[i])

			#encrypt the methods
			callingMethods[i - 1]= encryptNode(callingMethods[i-1], hashForNodes)
			callingMethods[i]= encryptNode(callingMethods[i], hashForNodes)

			djikstraGraph.add_edge(callingMethods[i-1], callingMethods[i], {'cost': EdgeType.DEF.value})
			djikstraGraph.add_edge(callingMethods[i], callingMethods[i-1], {'cost': EdgeType.DEF.value})


		for key,value in calledCalling[0].items() if len(calledCalling[0])>0 else []:

			for s in list(value):
				key = normalizeMethodNames(key)
				key= encryptNode(key, hashForNodes)
				s= normalizeMethodNames(s)
				s= encryptNode(s, hashForNodes)
				djikstraGraph.add_edge(key, s, {'cost': EdgeType.CALLING.value})
				djikstraGraph.add_edge(s, key, {'cost': EdgeType.CALLED.value})

	return djikstraGraph

def findPath(graph, method1, method2):
	cost_func = lambda u, v, e, prev_e: e['cost']

	try:
		path = algorithm.find_path(graph, normalizeMethodNames(method1), normalizeMethodNames(method2), cost_func=cost_func)
	except:
		path = "No Path Found"

	return path


def calculateHashForNodes(c1, c2):
	return c1[:4]+c2[:4]

def createGraphFromCommits(project, commitId1, commitId2):
	patchName = commitId1+commitId2+".patch"

	if patchName not in os.listdir("Patches/"):
		print('inside test', os.listdir("Patches/"))
		patchFile = open('Patches/' + patchName, 'w+')
		methods = PatchReader(project, commitId1, commitId2).methods()

		json.dump(methods, patchFile, cls=SetEncoder)
	else:

		patchFile = open('Patches/' + patchName)
		methods = json.loads(patchFile.read())

	hashForNodes = calculateHashForNodes(commitId1, commitId2)
	djikstraGraph = createGraph(methods, hashForNodes)

	return djikstraGraph


def updateGraph(djikstraGraph, methods, currHashForNodes, prevHashForNodes):

	for entry in methods:
		className = list(entry[0].keys())[0]

		calledCalling = list(entry[0].values())

		callingMethods = list(calledCalling[0])

		for i in range(1, len(callingMethods)):

			callingMethods[i-1]= normalizeMethodNames(callingMethods[i-1])
			callingMethods[i] = normalizeMethodNames(callingMethods[i])

			if callingMethods[i]=="HMemcacheScanner(3)":
				print("inside")

			#encrypt the methods
			currKey = encryptNode(callingMethods[i-1], currHashForNodes)
			currS= encryptNode(callingMethods[i], currHashForNodes)

			prevKey = encryptNode(callingMethods[i-1], prevHashForNodes)
			prevS = encryptNode(callingMethods[i], prevHashForNodes)

			if prevKey in djikstraGraph:
				djikstraGraph.add_edge(currKey, prevKey, {'cost': 1})
				djikstraGraph.add_edge(prevKey, currKey, {'cost': 1})

			if prevS in djikstraGraph:
				djikstraGraph.add_edge(currS, prevS, {'cost': 1})
				djikstraGraph.add_edge(prevS, currS, {'cost': 1})

			djikstraGraph.add_edge(currKey, currS, {'cost': EdgeType.DEF.value})
			djikstraGraph.add_edge(currS, currKey, {'cost': EdgeType.DEF.value})


		for key,value in calledCalling[0].items() if len(calledCalling[0])>0 else []:

			for s in list(value):
				key = normalizeMethodNames(key)
				s = normalizeMethodNames(s)
				currKey= encryptNode(key, currHashForNodes)
				currS= encryptNode(s, currHashForNodes)

				prevKey = encryptNode(key, prevHashForNodes)
				prevS = encryptNode(s, prevHashForNodes)

				if prevKey in djikstraGraph:
					djikstraGraph.add_edge(currKey, prevKey, {'cost': 1})
					djikstraGraph.add_edge(prevKey, currKey, {'cost': 1})

				if prevS in djikstraGraph:
					djikstraGraph.add_edge(currS, prevS, {'cost': 1})
					djikstraGraph.add_edge(prevS, currS, {'cost': 1})

				djikstraGraph.add_edge(currKey, currS, {'cost': EdgeType.CALLING.value})
				djikstraGraph.add_edge(currS, currKey, {'cost': EdgeType.CALLED.value})

	return djikstraGraph

def updateGraphForSecondCommit(djikstraGraph, project, currCommitId1, currCommitId2, prevCommitId1, prevCommitId2):
	patchName = commitId1+commitId2+".patch"

	if patchName not in os.listdir("Patches/"):
		print('inside test', os.listdir("Patches/"))
		patchFile = open('Patches/' + patchName, 'w+')
		methods = PatchReader(project, currCommitId1, currCommitId2).methods()

		json.dump(methods, patchFile, cls=SetEncoder)
	else:

		patchFile = open('Patches/' + patchName)
		methods = json.loads(patchFile.read())

	currHashForNodes = calculateHashForNodes(currCommitId1, currCommitId2)
	prevHashForNodes = calculateHashForNodes(prevCommitId1, prevCommitId2)

	updateGraph(djikstraGraph, methods, currHashForNodes, prevHashForNodes)

	return djikstraGraph

class SetEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, set):
			return list(obj)

		return json.JSONEncoder.default(self, obj)


def calculateSx(graph1Nodes, graph2Nodes, hashForGraph1, hashForGraph2, djikstraGraph):
	v1Costs=[]
	sx = 0.0
	for v1 in graph1Nodes:
		v1 = encryptNode(v1, hashForGraph1)
		v2Costs=[]
		for v2 in graph2Nodes:
			v2 = encryptNode(v2, hashForGraph2)
			pathInfo= findPath(djikstraGraph, v1, v2)
			if type(pathInfo)!=str:
				v2Costs.append(pathInfo.total_cost)
				# print(pathInfo.total_cost, v1, v2, v2Costs, v1Costs)

		if len(v2Costs) > 0:
			v1Costs.append(min(v2Costs))


	tempSum = 0.0
	for n in v1Costs:
		tempSum+= 1/float(n)

	sx=tempSum/float(len(v1Costs))
	return sx




def calculateSy(graph1Nodes, graph2Nodes, hashForGraph1, hashForGraph2, djikstraGraph):
	v2Costs = []
	sy = 0.0
	numOfUniqueNodes = 0
	for v2 in graph2Nodes:
		v2 = encryptNode(v2, hashForGraph2)
		v1Costs = []
		for v1 in graph1Nodes:
			v1 = encryptNode(v1, hashForGraph1)
			pathInfo = findPath(djikstraGraph, v2, v1)
			if type(pathInfo) != str:
				v1Costs.append(pathInfo.total_cost)
				# print(pathInfo.total_cost, v2, v1, v1Costs, v2Costs)

		if len(v1Costs) > 0:
			v2Costs.append(min(v1Costs))

	tempSum = 0.0
	for n in v2Costs:
		tempSum += 1 / float(n)

	sy = tempSum / float(len(v2Costs))
	return sy

if __name__=='__main__':

	project = 'hbase'
	commitId1 = '114d67c614847da0eb08bc2b27cde120bda2b3ff'
	commitId2 = '4a8d243f4e4bb16bc627eb9de2f6d801250170e9'

	djikstraGraph1 = createGraphFromCommits(project, commitId1, commitId2)
	project = 'hbase'
	commitId3 = '4a8d243f4e4bb16bc627eb9de2f6d801250170e9'
	commitId4 = '89af8294f42a9a16b91a09f7808653a71648718f'

	djikstraGraph2 = createGraphFromCommits(project, commitId3, commitId4)

	#combining the two graphs
	#storing graph1 keys for future reference, also every node is a source node because of two way pointers.
	graph1Nodes = list(djikstraGraph1._data.keys())
	hashForGraph1 = calculateHashForNodes(commitId1, commitId2)
	graph2Nodes = list(djikstraGraph2._data.keys())
	hashForGraph2 = calculateHashForNodes(commitId3, commitId4)

	print(djikstraGraph1._data)


	djikstraGraph3= updateGraphForSecondCommit(djikstraGraph1, project, commitId3, commitId4, commitId1, commitId2)

	sx= calculateSx(graph1Nodes, graph2Nodes, hashForGraph1, hashForGraph2, djikstraGraph3)

	sy= calculateSy(graph1Nodes, graph2Nodes, hashForGraph1, hashForGraph2, djikstraGraph3)

	leftMin = float(sx+sy)/2
	rightMin = sy

	score = max(leftMin, rightMin)

	print(score, leftMin, rightMin)

