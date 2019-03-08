import pprint
from collections import defaultdict
import re
from collections import namedtuple

def fileParse(filepath):

    lines = open(filepath, "r")
    mapID = {}
    ipCommits = {}
    unusedArray = []
    lastDefectNum = ''
    for line in lines:
        commit, issueID = line.strip().split("&=&")
        # print(commit, issueID)
        defectInfo = issueID.strip().split(" ")
        # print(defectInfo)
        defectNum = defectInfo[0]

        pp = pprint.PrettyPrinter(indent=4)

        # pp.pprint(initial)
        if not lastDefectNum == '':
            mapID[lastDefectNum][-1] = (mapID[lastDefectNum][-1][0], commit)

        # if not defectNum.isupper or not re.match(r'[H|E]',defectNum):
        # if not defectNum.isupper or not re.match(r'[H]', defectNum):
        #     unusedArray.append(defectNum)

        if defectNum in mapID:
            mapID[defectNum].append((commit, ''))
            lastDefectNum = defectNum

        else:
            mapID[defectNum] = [(commit, '')]
            lastDefectNum = defectNum

    for key, val in mapID.items():
       if key.isupper and re.match(r'[H]', key) and len(val) > 1:
        ipCommits[key] = val

    pp.pprint(ipCommits)


fileParse("log.txt")
