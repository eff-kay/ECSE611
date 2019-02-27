import pandas as pd
import pprint
from collections import defaultdict
# filepath = "log2.txt"

def fileParse(filepath):

    lines = open(filepath, "r")
    mapID = {}
    ipCommits = {}

    for line in lines:
        commit, issueID = line.strip().split("&=&")
        # print(commit, issueID)
        defectInfo = issueID.strip().split(" ")
        defectNum = defectInfo[0]
        # print(defectNum)

        # hash = defaultdict(list)
        # hash[defectNum].append(arrayCommits)

        pp = pprint.PrettyPrinter(indent=4)
        if defectNum in mapID:
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


fileParse("log2.txt")
