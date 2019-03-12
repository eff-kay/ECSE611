from patch_reader import PatchReader

import ast


def write_to_file(bin):
    with open("Repo/binary_count.txt","a+") as myfile:
        myfile.write(bin+"\n")

if __name__ == '__main__':
    with open('../Patches/Issue2CommitsHive.txt', 'r+') as f:
        s = f.read()
        fileData = ast.literal_eval(s)
    score = 0
    methods1 = methods2 = []
    patchName = ""

    for k, v in fileData.items():
        print("For issue Number: ", k)
        temp_list = ""
        project = 'hive'
        commitId1 = v[0][0]
        commitId2 = v[0][1]

        project = 'hive'
        commitId3 = v[1][0]
        commitId4 = v[1][1]
        patchName = ""
        try:
            patchName = commitId1+commitId2+".patch"
            methods1 = PatchReader(project, commitId1, commitId2).patch
            patchName = commitId3 + commitId4 + ".patch"
            methods2 = PatchReader(project, commitId3, commitId4).patch
            if len(methods1)==0 or len(methods2)==0:
                temp_list = k+","+commitId1+" "+commitId2+" "+commitId3+" "+commitId4+","+str(score)
                write_to_file(temp_list)
        except Exception:
            pass

    print(temp_list)