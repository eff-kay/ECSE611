
from collections import defaultdict
from collections import namedtuple

f= open("RawData/log.txt")

lines = [line for line in f.readlines()]

# CommitIssue = namedtuple('CommitIssue', ('commit', 'issue'))
# commitIssueArray=[]
issueHash = defaultdict(list)



for line in lines:
	try:
		commit, msg = line.split("&=&")
	except ValueError:
		print(line)

	msgArray = msg.split(" ")

	if msgArray[0]=="Revert":
		msgArray.insert(0, msgArray[1])

	issueNumber = msgArray[0]


	issueHash[issueNumber].append(commit)
	
	# commitIssueArray.append(CommitIssue(commit, msgArray[0].split("-")[1]))



# for val in commitIssueArray:
# 	print(val.commit, val.issue)

for key,val in issueHash.items():
	print(key,val)

print(len(lines))