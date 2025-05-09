def getrevision():
  # Extract board revision from cpuinfo file
  myrevision = "0000"
  try:
    f = open('/proc/cpuinfo','r')
    for line in f:
      if line[0:8]=='Revision':
        length=len(line)
        myrevision = line[11:length-1]
    f.close()
  except:
    myrevision = "0000"

  return myrevision

myrevision = getrevision()

print(myrevision)

if(myrevision[2:6] == '3111'):
  print('Board is probably a Pi 4')
else: print('Assume not a Pi 4')

print(myrevision[2:6])
