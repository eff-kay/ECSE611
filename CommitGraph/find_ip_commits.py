from getGraphFromPatch import calculateScoresFromCommits


if __name__=='__main__':

    project = 'hbase'
    commitId1 = '114d67c614847da0eb08bc2b27cde120bda2b3ff'
    commitId2 = '4a8d243f4e4bb16bc627eb9de2f6d801250170e9'

    project = 'hbase'
    commitId3 = '4a8d243f4e4bb16bc627eb9de2f6d801250170e9'
    commitId4 = '89af8294f42a9a16b91a09f7808653a71648718f'

    print(calculateScoresFromCommits(project, commitId1, commitId2, commitId3, commitId4))