import pprint
from collections import defaultdict
import re

def fileParse(filepath):

    lines = open(filepath, "r")
    mapID = {}
    ipCommits = {}
    unusedArray = []

    for line in lines:
        commit, issueID = line.strip().split("&=&")
        # print(commit, issueID)
        defectInfo = issueID.strip().split(" ")
        defectNum = defectInfo[0]
        # print(defectNum)

        pp = pprint.PrettyPrinter(indent=4)
        if not defectNum.isupper or not re.match(r'[H]',defectNum):
            unusedArray.append(defectNum)
        elif defectNum in mapID:
            mapID[defectNum].append(commit)
        else:
            mapID[defectNum] = [commit]
    # pp.pprint(mapID)

        # defectID = infoSplit[0]
        # issueNumbers.insert(0, defectID)

        # for id in issueNumbers:
        #     if fileLine.__contains__(id):

    for key, val in mapID.items():
        if len(val) > 1:
            ipCommits[key] = val
    pp.pprint(ipCommits)


fileParse("log.txt")
