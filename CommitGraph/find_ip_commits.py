import ast

from getGraphFromPatch import calculateScoresFromCommits

def write_to_file(filename, data):
    with open(filename,"a+") as myfile:
        myfile.write(data+"\n")


def testFiles():
    with open('../Patches/Issue2Commits.txt', 'r+') as f:
        s = f.read()
        fileData = ast.literal_eval(s)
    score = 0
    tp = 0
    fn = 0
    pairs = 0

    for k, v in fileData.items():
        print("For issue Number: ", k)
        temp_list = ""
        project = 'hbase'
        commitId1 = v[0][0]
        commitId2 = v[0][1]

        project = 'hbase'
        commitId3 = v[1][0]
        commitId4 = v[1][1]
        try:
            score = calculateScoresFromCommits(project, commitId1, commitId2, commitId3, commitId4)
            if Decimal(score) > 0.5:
                tp = tp + 1
            else:
                fn = fn + 1
            pairs = pairs + 1
            print(commitId1," ", commitId2," ", commitId3," ", commitId4)
            print(score)
            temp_list = k+","+commitId1+","+commitId2+","+commitId3+","+commitId4+","+str(score)
            print("True Positive Count: ",tp)
            print("False Negative Count: ", fn)
            print("Total Pairs Analyzed: ",pairs)
            write_to_file("scores.txt", temp_list)
        except Exception:
            error_issue = k + "," + commitId1 + "," + commitId2 + "," + commitId3 + "," + commitId4
            write_to_file("error.txt", error_issue)

if __name__ == '__main__':
    with open('../Patches/Issue2Commits.txt', 'r+') as f:
        s = f.read()
        fileData = ast.literal_eval(s)
    score = 0

    for k, v in fileData.items():
        print("For issue Number: ", k)
        temp_list = ""
        project = 'hbase'
        commitId1 = v[0][0]
        commitId2 = v[0][1]

        project = 'hbase'
        commitId3 = v[1][0]
        commitId4 = v[1][1]
        try:
            score = calculateScoresFromCommits(project, commitId1, commitId2, commitId3, commitId4)
            print(commitId1," ", commitId2," ", commitId3," ", commitId4)
            print(score)
            temp_list = k+","+commitId1+","+commitId2+","+commitId3+","+commitId4+","+str(score)
            write_to_file("scores.txt", temp_list)
        except Exception:
            error_issue = k + "," + commitId1 + "," + commitId2 + "," + commitId3 + "," + commitId4
            write_to_file("error.txt", error_issue)