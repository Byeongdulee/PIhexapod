from collections import OrderedDict

def decode_KEN(s):
    if isinstance(s, OrderedDict):
        for key, val in s.items():
            if val=='KSD':
                return key
    m = s.split('\n')
    for l in m:
        if 'KSD' in l:
            f = l.split('=')
            return f[0].strip()

def decode_KET(s):
    isNotfound = True
    if isinstance(s, OrderedDict):
        try:
            return s['KSD']
        except KeyError:
            return None
    m = s.split('\n')
    for l in m:
        print(l)
        if 'KSD' in l:
            f = l.split('=')
            isNotfound = False
            return f[1].strip()
    if isNotfound:
        return None

def decode_KLT(s):
    m = s.split('\n')
    cslist = []
    for l in m:
        mydic = {}
        fd = l.split('\t')
        for f in fd:
            kv = f.split('=')
            if len(kv)==2:
                val =  str2num(kv[1])
                if val==None:
                    mydic[kv[0]]=kv[1].strip()
                else:
                    mydic[kv[0]]=val
        cslist.append(mydic)
    return cslist

def str2num(x):
    try:
        return float(x)
    except ValueError:
        return None