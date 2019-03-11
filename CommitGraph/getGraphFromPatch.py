import json
from enum import Enum
from itertools import combinations
from dijkstar import Graph as dGraph,algorithm
from patch_reader import PatchReader

from change import Change

LabelledLine = Change.LabelledLine
import os

DEBUG = False
BACKUP = False


THRESHOLD = 0.6

calling = ((1/float(THRESHOLD))-1)/2
calling = float("{0:.2f}".format(calling))
called = ((1/float(THRESHOLD))-1)/2
called = float("{0:.2f}".format(calling))
definition = ((1/float(THRESHOLD))-1)
definition = float("{0:.2f}".format(definition))


#TODO: add a method to calculate the values from threshold
class EdgeType(Enum):
	CALLING = calling
	CALLED = calling
	DEF = definition
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
	if tempStr[0]=='while':
		return 'while(1)'
	if tempStr[0]=='if':
		return 'if(1)'
	elif tempStr[1]=='':
		leftName = tempStr[0]
		params = tempStr[2].split(')')[0]
		try:
			rightName = tempStr[2].split(')')[2]
		except IndexError:
			rightName=''
		count = params.count('<')
		params = params.replace(',', '', count)
		params = params.split(',')
		strParams = ''.join(params)
		if params == ['']:
			finalParamCount = 0
		else:
			finalParamCount = len(params)
		finalName = leftName + '(' + str(finalParamCount) + ')' + rightName
		return finalName
	else:
		leftName = tempStr[0]
		params = tempStr[1].split(')')[0]
		try:
			rightName = tempStr[1].split(')')[1]
		except IndexError:
			rightName=''

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
		node = normalizeMethodNames(node)
		node= node+"=="+hashForNodes
		return node


def checkForIfWhile(name):
	tempStr = ''.join(name.split(' '))
	tempStr = tempStr.split('(')

	if tempStr[0]=='if':
		return True
	if tempStr[0]=='while':
		return True



def createGraph(methods, hashForNodes):
	djikstraGraph = dGraph()

	modifiedNodes = set()

	for totalEntry in methods:
		for entry in totalEntry:
			className = list(entry.keys())[0]
			className= className.line

			calledCalling = list(entry.values())

			callingMethods = list(calledCalling[0])

			for i in range(len(callingMethods)-1):
				for j in range(i+1,len(callingMethods)):
					if type(callingMethods[i])==LabelledLine:
						if (checkForIfWhile(callingMethods[i].line)):
							continue

						if callingMethods[i].modified==True:
							modifiedNodes.add(callingMethods[i].line)
						callingMethods[i]=callingMethods[i].line

					if type(callingMethods[j])==LabelledLine:
						if (checkForIfWhile(callingMethods[j].line)):
							continue

						if callingMethods[j].modified==True:
							modifiedNodes.add(callingMethods[j].line)
						callingMethods[j]= callingMethods[j].line

					#encrypt the methods
					callingMethods[i]= encryptNode(callingMethods[i], hashForNodes)
					callingMethods[j]= encryptNode(callingMethods[j], hashForNodes)

					djikstraGraph.add_edge(callingMethods[i], callingMethods[j], {'cost': EdgeType.DEF.value})
					djikstraGraph.add_edge(callingMethods[j], callingMethods[i], {'cost': EdgeType.DEF.value})


			for key,value in calledCalling[0].items() if len(calledCalling[0])>0 else []:

				for s in list(value):


					if type(key) == LabelledLine:
						if (checkForIfWhile(key.line)):
							continue

						if key.modified == True:
							modifiedNodes.add(key.line)
						key = key.line

					if type(s) == LabelledLine:
						if (checkForIfWhile(s.line)):
							continue
						if s.modified == True:
							modifiedNodes.add(s.line)
						s = s.line

					key= encryptNode(key, hashForNodes)
					s= encryptNode(s, hashForNodes)
					djikstraGraph.add_edge(key, s, {'cost': EdgeType.CALLING.value})
					djikstraGraph.add_edge(s, key, {'cost': EdgeType.CALLED.value})

	return djikstraGraph, modifiedNodes

def findPath(graph, method1, method2):
	cost_func = lambda u, v, e, prev_e: e['cost']

	try:
		path = algorithm.find_path(graph, method1, method2, cost_func=cost_func)
	except:
		path = "No Path Found"

	return path


def calculateHashForNodes(c1, c2):
	return c1[:4]+c2[:4]

def createGraphFromCommits(project, commitId1, commitId2):
	patchName = commitId1+commitId2+".patch"

	# if patchName not in os.listdir("Patches/"):
	# print('inside test', os.listdir("Patches/"))
	# patchFile = open('Patches/' + patchName, 'w+')
	methods = PatchReader(project, commitId1, commitId2).methods()
	print(methods)
		
	# 	# json.dump(methods, patchFile, cls=SetEncoder)
	# else:
	# 	patchFile = open('Patches/' + patchName)
	# 	methods = json.loads(patchFile.read())
	# methods = [[{LabelledLine(line='public class HLog', modified=False): {LabelledLine(line=' consolidateOldLog(Path srcDir, Path dstFile, FileSystem fs, Configuration conf)', modified=False): set(), LabelledLine(line=' HLog(FileSystem fs, Path dir, Configuration conf)', modified=False): set(), LabelledLine(line=' computeFilename(long filenum)', modified=False): set(), LabelledLine(line=' obtainSeqNum(int num)', modified=False): {LabelledLine(line='obtainSeqNum()', modified=False)}, LabelledLine(line=' completeCacheFlush(Text regionName, Text tableName, long logSeqId)', modified=False): set()}}, {LabelledLine(line='public class HLog', modified=False): {LabelledLine(line=' consolidateOldLog(Path srcDir, Path dstFile, FileSystem fs, Configuration conf)', modified=False): set(), LabelledLine(line=' HLog(FileSystem fs, Path dir, Configuration conf)', modified=False): set(), LabelledLine(line=' computeFilename(long filenum)', modified=False): set(), LabelledLine(line=' obtainSeqNum(int num)', modified=False): {LabelledLine(line='obtainSeqNum()', modified=False)}, LabelledLine(line=' completeCacheFlush(Text regionName, Text tableName, long logSeqId)', modified=False): set()}}, {LabelledLine(line='public class HLog', modified=False): {LabelledLine(line=' consolidateOldLog(Path srcDir, Path dstFile, FileSystem fs, Configuration conf)', modified=False): set(), LabelledLine(line=' HLog(FileSystem fs, Path dir, Configuration conf)', modified=False): set(), LabelledLine(line=' computeFilename(long filenum)', modified=False): set(), LabelledLine(line=' obtainSeqNum(int num)', modified=False): {LabelledLine(line='obtainSeqNum()', modified=False)}, LabelledLine(line=' completeCacheFlush(Text regionName, Text tableName, long logSeqId)', modified=False): set()}}], [{LabelledLine(line='class HMemcacheScanner', modified=False): {LabelledLine(line=' HMemcacheScanner(long timestamp, Text targetCols[], Text firstRow)', modified=True): set(), LabelledLine(line=' catch(Exception ex)', modified=False): set(), LabelledLine(line=' findFirstRow(int i, Text firstRow)', modified=False): set(), LabelledLine(line=' getNext(int i)', modified=False): set(), LabelledLine(line=' closeSubScanner(int i)', modified=False): set()}}], [{LabelledLine(line='public class HRegion', modified=False): {LabelledLine(line=' closeAndMerge(HRegion srcA, HRegion srcB)', modified=False): set()}}, {LabelledLine(line='public class HRegion', modified=False): {LabelledLine(line=' closeAndMerge(HRegion srcA, HRegion srcB)', modified=False): set()}}, {LabelledLine(line='private class HScanner', modified=False): {LabelledLine(line=' closeScanner(int i)', modified=False): set()}}], [{LabelledLine(line='public class HServerAddress', modified=False): {LabelledLine(line=' HServerAddress(String hostAndPort)', modified=False): set(), LabelledLine(line=' HServerAddress(String bindAddress, int port)', modified=False): set(), LabelledLine(line=' HServerAddress(HServerAddress other)', modified=False): {LabelledLine(line='address.getPort()', modified=False)}, LabelledLine(line=' readFields(DataInput in)', modified=False): set(), LabelledLine(line=' write(DataOutput out)', modified=False): set()}}], [{LabelledLine(line='public class HStore', modified=False): {LabelledLine(line=' HStore(Path dir, Text regionName, Text colFamily, int maxVersions, ...)', modified=False): set(), LabelledLine(line=' flushCache(TreeMap<HStoreKey, BytesWritable> inputCache, ...)', modified=False): {LabelledLine(line='flushCacheHelper(inputCache, logCacheFlushId, true)', modified=False)}, LabelledLine(line=' flushCacheHelper(TreeMap<HStoreKey, BytesWritable> inputCache, ...)', modified=False): {LabelledLine(line='getAllMapFiles()', modified=False)}, LabelledLine(line=' compactHelper(boolean deleteSequenceInfo)', modified=False): {LabelledLine(line='processReadyCompaction()', modified=False)}, LabelledLine(line=' get(HStoreKey key, int numVersions)', modified=False): set(), LabelledLine(line=' getLargestFileSize(Text midKey)', modified=False): set(), LabelledLine(line=' obtainFileLabel(Path prefix)', modified=False): set(), LabelledLine(line=' getScanner(long timestamp, Text targetCols[], ...)', modified=False): set()}}, {LabelledLine(line='public class HStore', modified=False): {LabelledLine(line=' HStore(Path dir, Text regionName, Text colFamily, int maxVersions, ...)', modified=False): set(), LabelledLine(line=' flushCache(TreeMap<HStoreKey, BytesWritable> inputCache, ...)', modified=False): {LabelledLine(line='flushCacheHelper(inputCache, logCacheFlushId, true)', modified=False)}, LabelledLine(line=' flushCacheHelper(TreeMap<HStoreKey, BytesWritable> inputCache, ...)', modified=False): {LabelledLine(line='getAllMapFiles()', modified=False)}, LabelledLine(line=' compactHelper(boolean deleteSequenceInfo)', modified=False): {LabelledLine(line='processReadyCompaction()', modified=False)}, LabelledLine(line=' get(HStoreKey key, int numVersions)', modified=False): set(), LabelledLine(line=' getLargestFileSize(Text midKey)', modified=False): set(), LabelledLine(line=' obtainFileLabel(Path prefix)', modified=False): set(), LabelledLine(line=' getScanner(long timestamp, Text targetCols[], ...)', modified=False): set()}}, {LabelledLine(line='public class HStore', modified=False): {LabelledLine(line=' HStore(Path dir, Text regionName, Text colFamily, int maxVersions, ...)', modified=False): set(), LabelledLine(line=' flushCache(TreeMap<HStoreKey, BytesWritable> inputCache, ...)', modified=False): {LabelledLine(line='flushCacheHelper(inputCache, logCacheFlushId, true)', modified=False)}, LabelledLine(line=' flushCacheHelper(TreeMap<HStoreKey, BytesWritable> inputCache, ...)', modified=False): {LabelledLine(line='getAllMapFiles()', modified=False)}, LabelledLine(line=' compactHelper(boolean deleteSequenceInfo)', modified=False): {LabelledLine(line='processReadyCompaction()', modified=False)}, LabelledLine(line=' get(HStoreKey key, int numVersions)', modified=False): set(), LabelledLine(line=' getLargestFileSize(Text midKey)', modified=False): set(), LabelledLine(line=' obtainFileLabel(Path prefix)', modified=False): set(), LabelledLine(line=' getScanner(long timestamp, Text targetCols[], ...)', modified=False): set()}}, {LabelledLine(line='public class HStore', modified=False): {LabelledLine(line=' HStore(Path dir, Text regionName, Text colFamily, int maxVersions, ...)', modified=False): set(), LabelledLine(line=' flushCache(TreeMap<HStoreKey, BytesWritable> inputCache, ...)', modified=False): {LabelledLine(line='flushCacheHelper(inputCache, logCacheFlushId, true)', modified=False)}, LabelledLine(line=' flushCacheHelper(TreeMap<HStoreKey, BytesWritable> inputCache, ...)', modified=False): {LabelledLine(line='getAllMapFiles()', modified=False)}, LabelledLine(line=' compactHelper(boolean deleteSequenceInfo)', modified=False): {LabelledLine(line='processReadyCompaction()', modified=False)}, LabelledLine(line=' get(HStoreKey key, int numVersions)', modified=False): set(), LabelledLine(line=' getLargestFileSize(Text midKey)', modified=False): set(), LabelledLine(line=' obtainFileLabel(Path prefix)', modified=False): set(), LabelledLine(line=' getScanner(long timestamp, Text targetCols[], ...)', modified=False): set()}}], [{LabelledLine(line='public class HStoreFile', modified=False): {LabelledLine(line=' HStoreFile(Configuration conf)', modified=False): set(), LabelledLine(line=' HStoreFile(Configuration conf, Path dir, Text regionName, ...)', modified=False): set(), LabelledLine(line=' getMapDir(Path dir, Text regionName, Text colFamily)', modified=False): set(), LabelledLine(line=' getInfoDir(Path dir, Text regionName, Text colFamily)', modified=False): set(), LabelledLine(line=' getHStoreDir(Path dir, Text regionName, Text colFamily)', modified=False): set(), LabelledLine(line=' getHRegionDir(Path dir, Text regionName)', modified=False): set(), LabelledLine(line=' obtainNewHStoreFile(Configuration conf, Path dir, ...)', modified=False): set(), LabelledLine(line=' loadHStoreFiles(Configuration conf, Path dir, ...)', modified=False): set(), LabelledLine(line=' splitStoreFile(Text midKey, HStoreFile dstA, HStoreFile dstB, ...)', modified=False): set(), LabelledLine(line=' mergeStoreFiles(Vector<HStoreFile> srcFiles, FileSystem fs, ...)', modified=False): set(), LabelledLine(line=' loadInfo(FileSystem fs)', modified=False): {LabelledLine(line='in.readLong()', modified=False)}, LabelledLine(line=' writeInfo(FileSystem fs, long infonum)', modified=False): set(), LabelledLine(line=' write(DataOutput out)', modified=False): set(), LabelledLine(line=' readFields(DataInput in)', modified=False): set(), LabelledLine(line=' compareTo(Object o)', modified=False): set(), LabelledLine(line=' equals(Object o)', modified=False): {LabelledLine(line='this.compareTo(o)', modified=False)}}}], [{LabelledLine(line='public class HStoreKey', modified=False): {LabelledLine(line=' extractFamily(Text col)', modified=False): set(), LabelledLine(line=' HStoreKey(Text row)', modified=False): set(), LabelledLine(line=' HStoreKey(Text row, long timestamp)', modified=False): set(), LabelledLine(line=' HStoreKey(Text row, Text column)', modified=False): set(), LabelledLine(line=' HStoreKey(Text row, Text column, long timestamp)', modified=False): set(), LabelledLine(line=' setRow(Text newrow)', modified=False): set(), LabelledLine(line=' setColumn(Text newcol)', modified=False): set(), LabelledLine(line=' setVersion(long timestamp)', modified=False): set(), LabelledLine(line=' matchesRowCol(HStoreKey other)', modified=False): set(), LabelledLine(line=' matchesWithoutColumn(HStoreKey other)', modified=False): set(), LabelledLine(line=' compareTo(Object o)', modified=False): set(), LabelledLine(line=' write(DataOutput out)', modified=False): set(), LabelledLine(line=' readFields(DataInput in)', modified=False): set()}}]]

	hashForNodes = calculateHashForNodes(commitId1, commitId2)
	djikstraGraph,modifiedNodes = createGraph(methods, hashForNodes)

	return djikstraGraph,modifiedNodes


def updateGraph(djikstraGraph, methods, currHashForNodes, prevHashForNodes):

	for totalEntry in methods:
		for entry in totalEntry:
			className = list(entry.keys())[0]

			calledCalling = list(entry.values())

			callingMethods = list(calledCalling[0])


			for i in range(len(callingMethods)-1):
				for j in range(i+1,len(callingMethods)):
					if type(callingMethods[i])==LabelledLine:
						if (checkForIfWhile(callingMethods[i].line)):
							continue

						callingMethods[i]=callingMethods[i].line


					if type(callingMethods[j])==LabelledLine:
						if (checkForIfWhile(callingMethods[j].line)):
							continue
						callingMethods[j]= callingMethods[j].line

					#encrypt the methods

					currKey = encryptNode(callingMethods[i], currHashForNodes)
					currS= encryptNode(callingMethods[j], currHashForNodes)

					prevKey = encryptNode(callingMethods[i], prevHashForNodes)
					prevS = encryptNode(callingMethods[j], prevHashForNodes)

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
						if type(key) == LabelledLine:
							if (checkForIfWhile(key.line)):
								continue
							key = key.line

						if type(s) == LabelledLine:
							if (checkForIfWhile(s.line)):
								continue
							s = s.line

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

	if DEBUG:
		methods= [[{LabelledLine(line='class HMemcacheScanner', modified=False): {LabelledLine(line=' HMemcacheScanner(long timestamp, Text targetCols[], Text firstRow)', modified=True): set(), LabelledLine(line=' catch(Exception ex)', modified=False): set(), LabelledLine(line=' findFirstRow(int i, Text firstRow)', modified=False): set(), LabelledLine(line=' getNext(int i)', modified=False): set(), LabelledLine(line=' closeSubScanner(int i)', modified=False): set()}}], [{LabelledLine(line='public class HMsg', modified=False): {LabelledLine(line=' HMsg(byte msg)', modified=False): set(), LabelledLine(line=' HMsg(byte msg, HRegionInfo info)', modified=False): set(), LabelledLine(line=' write(DataOutput out)', modified=True): set(), LabelledLine(line=' readFields(DataInput in)', modified=True): set()}}], [{LabelledLine(line='public class HRegionServer', modified=False): {}}]]
	else:
		methods = PatchReader(project, currCommitId1, currCommitId2).methods()

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

	sx=tempSum/float(len(graph1Nodes)) if len(graph1Nodes)>0 else tempSum
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

	sy = tempSum / float(len(graph2Nodes)) if len(graph2Nodes)>0 else tempSum
	return sy



def calculateScoresFromCommits(project, commitId1, commitId2, commitId3, commitId4):

	if DEBUG==True:
		# BACKUP
		methods= [[{LabelledLine(line='public class HLog', modified=False): {LabelledLine(line=' consolidateOldLog(Path srcDir, Path dstFile, FileSystem fs, Configuration conf)', modified=False): set(), LabelledLine(line=' HLog(FileSystem fs, Path dir, Configuration conf)', modified=False): set(), LabelledLine(line=' computeFilename(long filenum)', modified=False): set(), LabelledLine(line=' obtainSeqNum(int num)', modified=False): {LabelledLine(line='obtainSeqNum()', modified=False)}, LabelledLine(line=' completeCacheFlush(Text regionName, Text tableName, long logSeqId)', modified=False): set()}}, {LabelledLine(line='public class HLog', modified=False): {LabelledLine(line=' consolidateOldLog(Path srcDir, Path dstFile, FileSystem fs, Configuration conf)', modified=False): set(), LabelledLine(line=' HLog(FileSystem fs, Path dir, Configuration conf)', modified=False): set(), LabelledLine(line=' computeFilename(long filenum)', modified=False): set(), LabelledLine(line=' obtainSeqNum(int num)', modified=False): {LabelledLine(line='obtainSeqNum()', modified=False)}, LabelledLine(line=' completeCacheFlush(Text regionName, Text tableName, long logSeqId)', modified=False): set()}}, {LabelledLine(line='public class HLog', modified=False): {LabelledLine(line=' consolidateOldLog(Path srcDir, Path dstFile, FileSystem fs, Configuration conf)', modified=False): set(), LabelledLine(line=' HLog(FileSystem fs, Path dir, Configuration conf)', modified=False): set(), LabelledLine(line=' computeFilename(long filenum)', modified=False): set(), LabelledLine(line=' obtainSeqNum(int num)', modified=False): {LabelledLine(line='obtainSeqNum()', modified=False)}, LabelledLine(line=' completeCacheFlush(Text regionName, Text tableName, long logSeqId)', modified=False): set()}}], [{LabelledLine(line='class HMemcacheScanner', modified=False): {LabelledLine(line=' HMemcacheScanner(long timestamp, Text targetCols[], Text firstRow)', modified=True): set(), LabelledLine(line=' catch(Exception ex)', modified=False): set(), LabelledLine(line=' findFirstRow(int i, Text firstRow)', modified=False): set(), LabelledLine(line=' getNext(int i)', modified=False): set(), LabelledLine(line=' closeSubScanner(int i)', modified=False): set()}}], [{LabelledLine(line='public class HRegion', modified=False): {LabelledLine(line=' closeAndMerge(HRegion srcA, HRegion srcB)', modified=False): set()}}, {LabelledLine(line='public class HRegion', modified=False): {LabelledLine(line=' closeAndMerge(HRegion srcA, HRegion srcB)', modified=False): set()}}, {LabelledLine(line='private class HScanner', modified=False): {LabelledLine(line=' closeScanner(int i)', modified=False): set()}}], [{LabelledLine(line='public class HServerAddress', modified=False): {LabelledLine(line=' HServerAddress(String hostAndPort)', modified=False): set(), LabelledLine(line=' HServerAddress(String bindAddress, int port)', modified=False): set(), LabelledLine(line=' HServerAddress(HServerAddress other)', modified=False): {LabelledLine(line='address.getPort()', modified=False)}, LabelledLine(line=' readFields(DataInput in)', modified=False): set(), LabelledLine(line=' write(DataOutput out)', modified=False): set()}}], [{LabelledLine(line='public class HStore', modified=False): {LabelledLine(line=' HStore(Path dir, Text regionName, Text colFamily, int maxVersions, ...)', modified=False): set(), LabelledLine(line=' flushCache(TreeMap<HStoreKey, BytesWritable> inputCache, ...)', modified=False): {LabelledLine(line='flushCacheHelper(inputCache, logCacheFlushId, true)', modified=False)}, LabelledLine(line=' flushCacheHelper(TreeMap<HStoreKey, BytesWritable> inputCache, ...)', modified=False): {LabelledLine(line='getAllMapFiles()', modified=False)}, LabelledLine(line=' compactHelper(boolean deleteSequenceInfo)', modified=False): {LabelledLine(line='processReadyCompaction()', modified=False)}, LabelledLine(line=' get(HStoreKey key, int numVersions)', modified=False): set(), LabelledLine(line=' getLargestFileSize(Text midKey)', modified=False): set(), LabelledLine(line=' obtainFileLabel(Path prefix)', modified=False): set(), LabelledLine(line=' getScanner(long timestamp, Text targetCols[], ...)', modified=False): set()}}, {LabelledLine(line='public class HStore', modified=False): {LabelledLine(line=' HStore(Path dir, Text regionName, Text colFamily, int maxVersions, ...)', modified=False): set(), LabelledLine(line=' flushCache(TreeMap<HStoreKey, BytesWritable> inputCache, ...)', modified=False): {LabelledLine(line='flushCacheHelper(inputCache, logCacheFlushId, true)', modified=False)}, LabelledLine(line=' flushCacheHelper(TreeMap<HStoreKey, BytesWritable> inputCache, ...)', modified=False): {LabelledLine(line='getAllMapFiles()', modified=False)}, LabelledLine(line=' compactHelper(boolean deleteSequenceInfo)', modified=False): {LabelledLine(line='processReadyCompaction()', modified=False)}, LabelledLine(line=' get(HStoreKey key, int numVersions)', modified=False): set(), LabelledLine(line=' getLargestFileSize(Text midKey)', modified=False): set(), LabelledLine(line=' obtainFileLabel(Path prefix)', modified=False): set(), LabelledLine(line=' getScanner(long timestamp, Text targetCols[], ...)', modified=False): set()}}, {LabelledLine(line='public class HStore', modified=False): {LabelledLine(line=' HStore(Path dir, Text regionName, Text colFamily, int maxVersions, ...)', modified=False): set(), LabelledLine(line=' flushCache(TreeMap<HStoreKey, BytesWritable> inputCache, ...)', modified=False): {LabelledLine(line='flushCacheHelper(inputCache, logCacheFlushId, true)', modified=False)}, LabelledLine(line=' flushCacheHelper(TreeMap<HStoreKey, BytesWritable> inputCache, ...)', modified=False): {LabelledLine(line='getAllMapFiles()', modified=False)}, LabelledLine(line=' compactHelper(boolean deleteSequenceInfo)', modified=False): {LabelledLine(line='processReadyCompaction()', modified=False)}, LabelledLine(line=' get(HStoreKey key, int numVersions)', modified=False): set(), LabelledLine(line=' getLargestFileSize(Text midKey)', modified=False): set(), LabelledLine(line=' obtainFileLabel(Path prefix)', modified=False): set(), LabelledLine(line=' getScanner(long timestamp, Text targetCols[], ...)', modified=False): set()}}, {LabelledLine(line='public class HStore', modified=False): {LabelledLine(line=' HStore(Path dir, Text regionName, Text colFamily, int maxVersions, ...)', modified=False): set(), LabelledLine(line=' flushCache(TreeMap<HStoreKey, BytesWritable> inputCache, ...)', modified=False): {LabelledLine(line='flushCacheHelper(inputCache, logCacheFlushId, true)', modified=False)}, LabelledLine(line=' flushCacheHelper(TreeMap<HStoreKey, BytesWritable> inputCache, ...)', modified=False): {LabelledLine(line='getAllMapFiles()', modified=False)}, LabelledLine(line=' compactHelper(boolean deleteSequenceInfo)', modified=False): {LabelledLine(line='processReadyCompaction()', modified=False)}, LabelledLine(line=' get(HStoreKey key, int numVersions)', modified=False): set(), LabelledLine(line=' getLargestFileSize(Text midKey)', modified=False): set(), LabelledLine(line=' obtainFileLabel(Path prefix)', modified=False): set(), LabelledLine(line=' getScanner(long timestamp, Text targetCols[], ...)', modified=False): set()}}], [{LabelledLine(line='public class HStoreFile', modified=False): {LabelledLine(line=' HStoreFile(Configuration conf)', modified=False): set(), LabelledLine(line=' HStoreFile(Configuration conf, Path dir, Text regionName, ...)', modified=False): set(), LabelledLine(line=' getMapDir(Path dir, Text regionName, Text colFamily)', modified=False): set(), LabelledLine(line=' getInfoDir(Path dir, Text regionName, Text colFamily)', modified=False): set(), LabelledLine(line=' getHStoreDir(Path dir, Text regionName, Text colFamily)', modified=False): set(), LabelledLine(line=' getHRegionDir(Path dir, Text regionName)', modified=False): set(), LabelledLine(line=' obtainNewHStoreFile(Configuration conf, Path dir, ...)', modified=False): set(), LabelledLine(line=' loadHStoreFiles(Configuration conf, Path dir, ...)', modified=False): set(), LabelledLine(line=' splitStoreFile(Text midKey, HStoreFile dstA, HStoreFile dstB, ...)', modified=False): set(), LabelledLine(line=' mergeStoreFiles(Vector<HStoreFile> srcFiles, FileSystem fs, ...)', modified=False): set(), LabelledLine(line=' loadInfo(FileSystem fs)', modified=False): {LabelledLine(line='in.readLong()', modified=False)}, LabelledLine(line=' writeInfo(FileSystem fs, long infonum)', modified=False): set(), LabelledLine(line=' write(DataOutput out)', modified=False): set(), LabelledLine(line=' readFields(DataInput in)', modified=False): set(), LabelledLine(line=' compareTo(Object o)', modified=False): set(), LabelledLine(line=' equals(Object o)', modified=False): {LabelledLine(line='this.compareTo(o)', modified=False)}}}], [{LabelledLine(line='public class HStoreKey', modified=False): {LabelledLine(line=' extractFamily(Text col)', modified=False): set(), LabelledLine(line=' HStoreKey(Text row)', modified=False): set(), LabelledLine(line=' HStoreKey(Text row, long timestamp)', modified=False): set(), LabelledLine(line=' HStoreKey(Text row, Text column)', modified=False): set(), LabelledLine(line=' HStoreKey(Text row, Text column, long timestamp)', modified=False): set(), LabelledLine(line=' setRow(Text newrow)', modified=False): set(), LabelledLine(line=' setColumn(Text newcol)', modified=False): set(), LabelledLine(line=' setVersion(long timestamp)', modified=False): set(), LabelledLine(line=' matchesRowCol(HStoreKey other)', modified=False): set(), LabelledLine(line=' matchesWithoutColumn(HStoreKey other)', modified=False): set(), LabelledLine(line=' compareTo(Object o)', modified=False): set(), LabelledLine(line=' write(DataOutput out)', modified=False): set(), LabelledLine(line=' readFields(DataInput in)', modified=False): set()}}]]
		hashForGraph1 = calculateHashForNodes(commitId1, commitId2)
		djikstraGraph1,modifiedNodes1 = createGraph(methods, hashForGraph1)

		methods2= [[{LabelledLine(line='class HMemcacheScanner', modified=False): {LabelledLine(line=' HMemcacheScanner(long timestamp, Text targetCols[], Text firstRow)', modified=True): set(), LabelledLine(line=' catch(Exception ex)', modified=False): set(), LabelledLine(line=' findFirstRow(int i, Text firstRow)', modified=False): set(), LabelledLine(line=' getNext(int i)', modified=False): set(), LabelledLine(line=' closeSubScanner(int i)', modified=False): set()}}], [{LabelledLine(line='public class HMsg', modified=False): {LabelledLine(line=' HMsg(byte msg)', modified=False): set(), LabelledLine(line=' HMsg(byte msg, HRegionInfo info)', modified=False): set(), LabelledLine(line=' write(DataOutput out)', modified=True): set(), LabelledLine(line=' readFields(DataInput in)', modified=True): set()}}], [{LabelledLine(line='public class HRegionServer', modified=False): {}}]]
		hashForGraph2 = calculateHashForNodes(commitId3, commitId4)
		djikstraGraph2, modifiedNodes2 = createGraph(methods2, hashForGraph2)

		if BACKUP:
			modifiedNodes1 = list(djikstraGraph1._data.keys())
			modifiedNodes2 = list(djikstraGraph2._data.keys())
	else:
		djikstraGraph1, modifiedNodes1 = createGraphFromCommits(project, commitId1, commitId2)
		hashForGraph1 = calculateHashForNodes(commitId1, commitId2)

		djikstraGraph2, modifiedNodes2 = createGraphFromCommits(project, commitId3, commitId4)
		hashForGraph2 = calculateHashForNodes(commitId3, commitId4)

	djikstraGraph3= updateGraphForSecondCommit(djikstraGraph1, project, commitId3, commitId4, commitId1, commitId2)

	print(djikstraGraph3._data)

	sx= calculateSx(list(modifiedNodes1), list(modifiedNodes2), hashForGraph1, hashForGraph2, djikstraGraph3)

	sy= calculateSy(list(modifiedNodes1), list(modifiedNodes2), hashForGraph1, hashForGraph2, djikstraGraph3)

	leftMin = float(sx+sy)/2
	rightMin = sy

	score = max(leftMin, rightMin)

	print(leftMin, rightMin, score)

	return float("{0:.2f}".format(score))

if __name__=='__main__':
	project = 'hive'
	# commitId1 = '114d67c614847da0eb08bc2b27cde120bda2b3ff'
	# commitId2 = '4a8d243f4e4bb16bc627eb9de2f6d801250170e9'
	#
	# project = 'hbase'
	# commitId3 = '4a8d243f4e4bb16bc627eb9de2f6d801250170e9'
	# commitId4 = '89af8294f42a9a16b91a09f7808653a71648718f'

	# # project = 'hbase'
	# commitId1 = '7c3d11974bf7c2b4beb1a385cbab68d8175731b3'
	# commitId2 = '66839c4c17b169f5f2b6f39374558d9a5c3bc2e2'

	# project = 'hbase'
	# commitId3 = '66839c4c17b169f5f2b6f39374558d9a5c3bc2e2'
	# commitId4 = 'a2fba1024dc32de7fd21513540f064433e7795b0'

	commitId1= "20e595399f65af6a25ef9c2356e0e46496ec0c0b"
	commitId2= "8f3b312e049c3892b3fd80e009b2c1aa8869e8ea"
	commitId3= "b13eba000e1cce39a7449b289c659c2f236ce9c9"
	commitId4= "0417cef9d5748ed12f5a29dd5d59486ef2e20311"

	# 'HADOOP-1391.': [('7c3d11974bf7c2b4beb1a385cbab68d8175731b3',
	# 				  '66839c4c17b169f5f2b6f39374558d9a5c3bc2e2'),
	# 				 ('66839c4c17b169f5f2b6f39374558d9a5c3bc2e2',
	# 				  'a2fba1024dc32de7fd21513540f064433e7795b0'),

	# commitId3 = '87f5d5dffd96e09d789a9063f8f6d98a75fb24dd'
	# commitId4 = 'f613907a98a732364c5a2a5f1f4ece7bc99f555e'


	# DEBUG=False
	# BACKUP = True


	#update the interface to calculate the threshold.
	print(calculateScoresFromCommits(project, commitId1, commitId2, commitId3, commitId4))

	print(calling, called, definition)

