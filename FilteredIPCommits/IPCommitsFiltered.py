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
        defectNum = defectInfo[0]

        pp = pprint.PrettyPrinter(indent=4)

        # pp.pprint(initial)
        if not lastDefectNum == '':
            mapID[lastDefectNum][-1] = (mapID[lastDefectNum][-1][0], commit)


        if not defectNum.isupper or not re.match(r'[H]',defectNum):
            unusedArray.append(defectNum)

        elif defectNum in mapID:
            mapID[defectNum].append((commit, ''))
            lastDefectNum = defectNum

        else:
            mapID[defectNum] = [(commit, '')]
            lastDefectNum = defectNum

    # pp.pprint(mapID)

    for key, val in mapID.items():
        if len(val) > 1:
            ipCommits[key] = val
    pp.pprint(ipCommits)

    # for defectNum in mapID.keys():
    #         path = prefix + [defectNum]
    #         if not isinstance(mapID[defectNum], dict):
    #             print(os.path.join(*path))
    #         else:
    #             get_files(mapID[defectNum], path)
    # pp.pprint(mapID)

if __name__=="__main__":
    print(fileParse("log.txt"))
