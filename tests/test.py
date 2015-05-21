keystr = "BL"

for line in open('ele.list','r'):
    line = ''.join(line.strip().split())
    if line.startswith(keystr+":line"):
        print line.replace(keystr + ':line=', '').replace('(','').replace(')','')
