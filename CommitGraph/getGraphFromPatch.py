import json
from enum import Enum

from itertools import combinations


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


if __name__=='__main__':
	A='''{"JsonMapper": {"writeMapAsString": "writeObjectAsString", "writeObjectAsString":"", "JsonMapper":""}}'''
	hashMap = json.loads(A)

	print(hashMap)
	className = list(hashMap.keys())[0]


	graph = Graph()
	for k,v in hashMap[className].items():
		node = Node(k)

		if v !="":
			endingNode = Node(v)
			e = Edge(endingNode, EdgeType.CALLING)
			node.outGoingEdges.add(e)
			e2 = Edge(node, EdgeType.CALLED)
			endingNode.outGoingEdges.add(e2)
			if endingNode.name not in graph.getNodeNames():
				graph.addNode(endingNode)

		if node.name not in graph.getNodeNames():
			graph.addNode(node)


	#create an between each node

	for n1, n2 in list(combinations(graph.nodes,2)):
		e = Edge(n1, EdgeType.DEF)
		n2.outGoingEdges.add(e)
		e = Edge(n2, EdgeType.DEF)
		n1.outGoingEdges.add(e)


	# nodes = list(graph.nodes)

	# e = Edge(nodes[0], EdgeType.Def)
	#
	# for node in nodes[1:]:
	# 	node.outGoingEdges.add(e)
	# 	e = Edge(node, EdgeType.Def)
	#
	# e = Edge(nodes[-1], EdgeType.Def)
	#
	# for node in reversed(nodes[:-1]):
	# 	node.outGoingEdges.add(e)
	# 	e = Edge(node, EdgeType.Def)






