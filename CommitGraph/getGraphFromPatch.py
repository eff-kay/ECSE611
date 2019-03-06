import json
from enum import Enum
from itertools import combinations
from dijkstar import Graph as dGraph,algorithm
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



def normalizeMethodNames(name):
	
	tempStr = ''.join(name.split(' '))

	tempStr = tempStr.split('(')

	leftName = tempStr[0]
	params = tempStr[1].split(')')[0]
	rightName = tempStr[1].split(')')[1]
	count= params.count('<')
	params = params.replace(',','', count)
	params = params.split(',')
	finalParamCount = len(params)
	finalName = leftName+'('+str(finalParamCount)+')'+rightName
	return finalName





def createGraph(methods):
	djikstraGraph = dGraph()

	for entry in methods:
		className = list(entry[0].keys())[0]
		print("classname", className)

		calledCalling = list(entry[0].values())

		callingMethods = list(calledCalling[0])

		for i in range(1, len(callingMethods)):

			callingMethods[i-1]= normalizeMethodNames(callingMethods[i-1])
			callingMethods[i] = normalizeMethodNames(callingMethods[i])
			djikstraGraph.add_edge(callingMethods[i-1], callingMethods[i], {'cost': 0.42})
			djikstraGraph.add_edge(callingMethods[i], callingMethods[i-1], {'cost': 0.42})


		for key,value in calledCalling[0].items() if len(calledCalling[0])>0 else []:

			for s in list(value):

				key = normalizeMethodNames(key)
				s= normalizeMethodNames(s)
				djikstraGraph.add_edge(key, s, {'cost': 0.21})
				djikstraGraph.add_edge(s, key, {'cost': 0.21})
				print("key", key, "value", s)

	return djikstraGraph

def findPath(graph, method1, method2):
	cost_func = lambda u, v, e, prev_e: e['cost']

	return algorithm.find_path(djikstraGraph, normalizeMethodNames(method1), normalizeMethodNames(method2), cost_func=cost_func)


if __name__=='__main__':

	methods = [[{'public final class JsonMapper': {' writeMapAsString(Map<String, Object> map)': {'writeObjectAsString(map)'}, ' writeObjectAsString(Object object)': {'MAPPER.writeValueAsString(object)', 'GSON.toJson(object)'}}}]]
	methods2 = [[{'public final class GsonUtil': []}], [{'public class JSONBean': {' write(MBeanServer mBeanServer, ObjectName qry, String attribute, boolean description)': {'flush()'}, ' open(final PrintWriter writer)': set(), ' write(String key, String value)': set(), ' write(MBeanServer mBeanServer, ObjectName qry, String attribute, ...)': {'JSONBean.write(jsonWriter, mBeanServer, qry, attribute, description)'}, ' write(JsonWriter writer, MBeanServer mBeanServer, ObjectName qry, ...)': set()}}, {'public class JSONBean': {' write(MBeanServer mBeanServer, ObjectName qry, String attribute, boolean description)': {'flush()'}, ' open(final PrintWriter writer)': set(), ' write(String key, String value)': set(), ' write(MBeanServer mBeanServer, ObjectName qry, String attribute, ...)': {'JSONBean.write(jsonWriter, mBeanServer, qry, attribute, description)'}, ' write(JsonWriter writer, MBeanServer mBeanServer, ObjectName qry, ...)': set()}}, {'public class JSONBean': {' write(MBeanServer mBeanServer, ObjectName qry, String attribute, boolean description)': {'flush()'}, ' open(final PrintWriter writer)': set(), ' write(String key, String value)': set(), ' write(MBeanServer mBeanServer, ObjectName qry, String attribute, ...)': {'JSONBean.write(jsonWriter, mBeanServer, qry, attribute, description)'}, ' write(JsonWriter writer, MBeanServer mBeanServer, ObjectName qry, ...)': set()}}, {'public class JSONBean': {' write(MBeanServer mBeanServer, ObjectName qry, String attribute, boolean description)': {'flush()'}, ' open(final PrintWriter writer)': set(), ' write(String key, String value)': set(), ' write(MBeanServer mBeanServer, ObjectName qry, String attribute, ...)': {'JSONBean.write(jsonWriter, mBeanServer, qry, attribute, description)'}, ' write(JsonWriter writer, MBeanServer mBeanServer, ObjectName qry, ...)': set()}}], [{'public final class JSONMetricUtil': {' getMBeanAttributeInfo(ObjectName bean)': {'mbinfo.getAttributes()'}, ' getValueFromMBean(ObjectName bean, String attribute)': set(), ' dumpBeanToString(String qry)': {'sw.toString()'}, ' buildObjectName(String pattern)': set(), ' getRegistredMBeans(ObjectName name, MBeanServer mbs)': {'mbs.queryNames(name, null)'}, ' getLastGcDuration(ObjectName gcCollector)': set(), ' calcPercentage(long a, long b)': set()}}], [{'public class RESTApiClusterManager': {' setConf(Configuration conf)': set(), ' start(ServiceType service, String hostname, int port)': set(), ' stop(ServiceType service, String hostname, int port)': set(), ' restart(ServiceType service, String hostname, int port)': set(), ' isRunning(ServiceType service, String hostname, int port)': set(), ' kill(ServiceType service, String hostname, int port)': set(), ' suspend(ServiceType service, String hostname, int port)': set(), ' resume(ServiceType service, String hostname, int port)': set(), ' performClusterManagerCommand(ServiceType role, String hostname, RoleCommand command)': set(), ' doRoleCommand(String serviceName, String roleName, RoleCommand roleCommand)': set(), ' getHealthSummary(String serviceName, String roleType, String hostId)': {'getRolePropertyValue(serviceName, roleType, hostId, "healthSummary")'}, ' getHostId(String hostname)': set(), ' getJsonNodeFromURIGet(URI uri)': set(), ' getRoleName(String serviceName, String roleType, String hostId)': {'getRolePropertyValue(serviceName, roleType, hostId, "name")'}, ' getRolePropertyValue(String serviceName, String roleType, String hostId, ...)': set(), ' getRoleState(String serviceName, String roleType, String hostId)': {'getRolePropertyValue(serviceName, roleType, hostId, "roleState")'}, ' getServiceName(Service service)': set()}}], [{'public class BlockCacheUtil': {' toString(final CachedBlock cb, final long now)': set()}}, {'public class BlockCacheUtil': {' toString(final CachedBlock cb, final long now)': set(), ' write(JsonWriter out, FastLongHistogram value)': set(), ' read(JsonReader in)': set()}}, {'public class BlockCacheUtil': {' toString(final CachedBlock cb, final long now)': set(), ' write(JsonWriter out, FastLongHistogram value)': set(), ' read(JsonReader in)': set()}}]]

	djikstraGraph = createGraph(methods)

	print(findPath(djikstraGraph, ' writeMapAsString(Map<String, Object> map)', 'writeObjectAsString(map)'))




	# # g.add_edge('B', 'D', {'cost': 2})
	# # g.add_edge('E', 'D', {'cost': 1})
	# # g.add_edge('A', 'C', {'cost': 2})
	# # g.add_edge('C', 'E', {'cost': 5})
	# # g.add_edge('B', 'C', {'cost': 3})
	# # g.add_edge('C', 'B', {'cost': 1})
