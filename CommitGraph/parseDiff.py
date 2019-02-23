import whatthepatch

# with open('RawData/head.patch') as f:
with open('RawData/144998.patch') as f:
	text = f.read()


diffFile = open("testDiff1", "w+")
diff = [x for x in whatthepatch.parse_patch(text)]

print(diff[0].changes)