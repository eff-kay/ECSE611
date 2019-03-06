import json
from enum import Enum

from itertools import combinations

from dijkstar import Graph as dGraph, find_path


from patch_reader import PatchReader



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

	# patch_reader = PatchReader('hbase', 'f0032c925510877396b1b0979abcc2ce83e67529', '482b505796e1dfe33551c1d20af2ff9d1d6a38dc')
	# methods = patch_reader.methods()


	methods = [[{'public final class JsonMapper': {' writeMapAsString(Map<String, Object> map)': {'writeObjectAsString(map)'}, ' writeObjectAsString(Object object)': {'MAPPER.writeValueAsString(object)', 'GSON.toJson(object)'}}}], [{'public final class GsonUtil': []}], [{'public class JSONBean': {' write(MBeanServer mBeanServer, ObjectName qry, String attribute, boolean description)': {'flush()'}, ' open(final PrintWriter writer)': set(), ' write(String key, String value)': set(), ' write(MBeanServer mBeanServer, ObjectName qry, String attribute, ...)': {'JSONBean.write(jsonWriter, mBeanServer, qry, attribute, description)'}, ' write(JsonWriter writer, MBeanServer mBeanServer, ObjectName qry, ...)': set()}}, {'public class JSONBean': {' write(MBeanServer mBeanServer, ObjectName qry, String attribute, boolean description)': {'flush()'}, ' open(final PrintWriter writer)': set(), ' write(String key, String value)': set(), ' write(MBeanServer mBeanServer, ObjectName qry, String attribute, ...)': {'JSONBean.write(jsonWriter, mBeanServer, qry, attribute, description)'}, ' write(JsonWriter writer, MBeanServer mBeanServer, ObjectName qry, ...)': set()}}, {'public class JSONBean': {' write(MBeanServer mBeanServer, ObjectName qry, String attribute, boolean description)': {'flush()'}, ' open(final PrintWriter writer)': set(), ' write(String key, String value)': set(), ' write(MBeanServer mBeanServer, ObjectName qry, String attribute, ...)': {'JSONBean.write(jsonWriter, mBeanServer, qry, attribute, description)'}, ' write(JsonWriter writer, MBeanServer mBeanServer, ObjectName qry, ...)': set()}}, {'public class JSONBean': {' write(MBeanServer mBeanServer, ObjectName qry, String attribute, boolean description)': {'flush()'}, ' open(final PrintWriter writer)': set(), ' write(String key, String value)': set(), ' write(MBeanServer mBeanServer, ObjectName qry, String attribute, ...)': {'JSONBean.write(jsonWriter, mBeanServer, qry, attribute, description)'}, ' write(JsonWriter writer, MBeanServer mBeanServer, ObjectName qry, ...)': set()}}], [{'public final class JSONMetricUtil': {' getMBeanAttributeInfo(ObjectName bean)': {'mbinfo.getAttributes()'}, ' getValueFromMBean(ObjectName bean, String attribute)': set(), ' dumpBeanToString(String qry)': {'sw.toString()'}, ' buildObjectName(String pattern)': set(), ' getRegistredMBeans(ObjectName name, MBeanServer mbs)': {'mbs.queryNames(name, null)'}, ' getLastGcDuration(ObjectName gcCollector)': set(), ' calcPercentage(long a, long b)': set()}}], [{'public class RESTApiClusterManager': {' setConf(Configuration conf)': set(), ' start(ServiceType service, String hostname, int port)': set(), ' stop(ServiceType service, String hostname, int port)': set(), ' restart(ServiceType service, String hostname, int port)': set(), ' isRunning(ServiceType service, String hostname, int port)': set(), ' kill(ServiceType service, String hostname, int port)': set(), ' suspend(ServiceType service, String hostname, int port)': set(), ' resume(ServiceType service, String hostname, int port)': set(), ' performClusterManagerCommand(ServiceType role, String hostname, RoleCommand command)': set(), ' doRoleCommand(String serviceName, String roleName, RoleCommand roleCommand)': set(), ' getHealthSummary(String serviceName, String roleType, String hostId)': {'getRolePropertyValue(serviceName, roleType, hostId, "healthSummary")'}, ' getHostId(String hostname)': set(), ' getJsonNodeFromURIGet(URI uri)': set(), ' getRoleName(String serviceName, String roleType, String hostId)': {'getRolePropertyValue(serviceName, roleType, hostId, "name")'}, ' getRolePropertyValue(String serviceName, String roleType, String hostId, ...)': set(), ' getRoleState(String serviceName, String roleType, String hostId)': {'getRolePropertyValue(serviceName, roleType, hostId, "roleState")'}, ' getServiceName(Service service)': set()}}], [{'public class BlockCacheUtil': {' toString(final CachedBlock cb, final long now)': set()}}, {'public class BlockCacheUtil': {' toString(final CachedBlock cb, final long now)': set(), ' write(JsonWriter out, FastLongHistogram value)': set(), ' read(JsonReader in)': set()}}, {'public class BlockCacheUtil': {' toString(final CachedBlock cb, final long now)': set(), ' write(JsonWriter out, FastLongHistogram value)': set(), ' read(JsonReader in)': set()}}]]

	for entry in methods:


		className = list(entry[0].keys())[0]
		print("classname", className)

		calledCalling = list(entry[0].values())

		for key,value in calledCalling[0].items() if len(calledCalling[0])>0 else []:
			print("key", key)
			for s in list(value):
				print("value", s)

		# for en in entry:
		# 	print("en ", en)



	# A='''{"JsonMapper": {"writeMapAsString": "writeObjectAsString", "writeObjectAsString":"toJSON", "JsonMapper":""}}'''
	# hashMap = json.loads(A)
	#
	# # print(hashMap)
	# className = list(hashMap.keys())[0]
	#
	#
	# graph = Graph()
	# for k,v in hashMap[className].items():
	# 	node = Node(k)
	#
	# 	if v !="":
	# 		endingNode = Node(v)
	# 		e = Edge(endingNode, EdgeType.CALLING)
	# 		node.outGoingEdges.add(e)
	# 		e2 = Edge(node, EdgeType.CALLED)
	# 		endingNode.outGoingEdges.add(e2)
	# 		if endingNode.name not in graph.getNodeNames():
	# 			graph.addNode(endingNode)
	#
	# 	if node.name not in graph.getNodeNames():
	# 		graph.addNode(node)
	#
	#
	# #create a def relation between each node
	#
	# for n1, n2 in list(combinations(graph.nodes,2)):
	# 	e = Edge(n1, EdgeType.DEF)
	# 	n2.outGoingEdges.add(e)
	# 	e = Edge(n2, EdgeType.DEF)
	# 	n1.outGoingEdges.add(e)
	#
	#
	# g = dGraph()
	# # for node in graph.nodes:
	# # 	for edge in node.outGoingEdges:
	# # 		g.add_edge(node.name, edge.endingNode.name, {'cost': edge.edgeType.value})
	#
	#
	#
	# g.add_edge('writeMapAsString', 'writeObjectAsString', {'cost': 0.21})
	# g.add_edge('writeObjectAsString', 'writeMapAsString', {'cost': 0.21})
	# g.add_edge('writeObjectAsString', 'toJSON', {'cost': 0.21})
	# g.add_edge('toJSON', 'writeObjectAsString', {'cost': 0.21})
	# g.add_edge('JsonMapper', 'writeMapAsString', {'cost': 0.42})
	# g.add_edge('writeMapAsString', 'JsonMapper', {'cost': 0.42})
	# g.add_edge('JsonMapper', 'writeObjectAsString', {'cost': 0.42})
	# g.add_edge('writeObjectAsString', 'writeMapAsString', {'cost': 0.42})
	# g.add_edge('writeMapAsString', 'writeObjectAsString', {'cost': 0.42})
	#
	#
	# # g.add_edge('B', 'D', {'cost': 2})
	# # g.add_edge('E', 'D', {'cost': 1})
	# # g.add_edge('A', 'C', {'cost': 2})
	# # g.add_edge('C', 'E', {'cost': 5})
	# # g.add_edge('B', 'C', {'cost': 3})
	# # g.add_edge('C', 'B', {'cost': 1})
	#
	# cost_func = lambda u, v, e, prev_e: e['cost']
	# #
	# print(find_path(g, 'writeMapAsString', 'toJSON', cost_func=cost_func))
	# # print(find_path(g, 'A', 'C', cost_func=cost_func))
	# # print(find_path(g, 'A', 'D', cost_func=cost_func))
	# # print(find_path(g, 'A', 'E', cost_func=cost_func))
	#
	#
	#
	#
	#
	#
	# # nodes = list(graph.nodes)
	#
	# # e = Edge(nodes[0], EdgeType.Def)
	# #
	# # for node in nodes[1:]:
	# # 	node.outGoingEdges.add(e)
	# # 	e = Edge(node, EdgeType.Def)
	# #
	# # e = Edge(nodes[-1], EdgeType.Def)
	# #
	# # for node in reversed(nodes[:-1]):
	# # 	node.outGoingEdges.add(e)
	# # 	e = Edge(node, EdgeType.Def)






