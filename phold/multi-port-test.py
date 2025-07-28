import sst

comps = []
for i in range(5):
  comp = sst.Component("comp" + str(i), "phold.Node")
  comp.addParams({"numRings": 1})
  comps.append(comp)

for i in range(5):
  for j in range(i, 5):
    i_port = "port" + str(j)
    j_port = "port" + str(i)
    link = sst.Link("link_" + str(i) + "_" + str(j))
    link.connect((comps[i], i_port, "1ns"), (comps[j], j_port, "1ns"))