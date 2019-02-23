import json
from enum import Enum


class EdgeType(Enum):
	Calling = 0.21
	Called = 0.21
	Def = 0.42
	Equal = 1

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


if __name__=='__main__':
	A='''{"JsonMapper": {"writeMapAsString": "writeObjectAsString", "writeObjectAsString":"", "JsonMapper":""}}'''
	hashMap = json.loads(A)

	print(hashMap)
	className = list(hashMap.keys())[0]

	graph = Graph()
	for key in hashMap[className]:
		node = Node(key)

		if node not in graph.nodes:
			graph.addNode(node)

	#create an between each node

	nodes = list(graph.nodes)

	e = Edge(nodes[0], EdgeType.Def)

	for node in nodes[1:]:
		node.outGoingEdges.add(e)
		e = Edge(node, EdgeType.Def)

	e = Edge(nodes[-1], EdgeType.Def)

	for node in reversed(nodes[:-1]):
		node.outGoingEdges.add(e)
		e = Edge(node, EdgeType.Def)






