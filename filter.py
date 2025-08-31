import os
import re
f = open("assetlist02152021.csv")
for i1 in f:
    i = re.sub('"',"",i1)
    l = i.split(",")
    #print(len(l))
    if re.search(" CHASSIS ",l[2]) or l[2] == '':
        pass
    else:
        print("{},{},{},{}".format(l[0],l[2],l[3],l[9]))
        # print("That's all folks")
