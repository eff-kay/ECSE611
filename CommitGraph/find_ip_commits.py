from getGraphFromPatch import calculateScoresFromCommits


if __name__=='__main__':

    # project = 'hbase'
    # commitId1 = '114d67c614847da0eb08bc2b27cde120bda2b3ff'
    # commitId2 = '4a8d243f4e4bb16bc627eb9de2f6d801250170e9'
    #
    # project = 'hbase'
    # commitId3 = '4a8d243f4e4bb16bc627eb9de2f6d801250170e9'
    # commitId4 = '89af8294f42a9a16b91a09f7808653a71648718f'

    project = 'hbase'
    commitId1 = 'a9acbeab0800dd1d3c13aaaea07d2975b0f49cb4'
    commitId2 = '5b1bd1f8f2d614c945f6a5889a9d4f25b87fe172'

    # project = 'hbase'
    commitId3 = 'cbb844d5f0be591c76e84e325b40fc313851d57c'
    commitId4 = '5463de47b3f41a254eb3159b6963f3c92f660388'

    print(calculateScoresFromCommits(project, commitId1, commitId2, commitId3, commitId4))