def write_to_file(scores):
    with open("scores.txt","a") as myfile:
        myfile.write(scores+"\n")

if __name__ == '__main__':
    with open('Issue2Commits.txt', 'r') as f:
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
            temp_list = k+","+commitId1+" "+commitId2+" "+commitId3+" "+commitId4+","+str(score)
            print("True Positive Count: ",tp)
            print("False Negative Count: ", fn)
            print("Total Pairs Analyzed: ",pairs)
            write_to_file(temp_list)
        except Exception:
            pass

    print(temp_list)
