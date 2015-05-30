#coding=utf-8
import sys
if sys.version[0]=='2':
    input=raw_input

import hashlib
import random
import json
import base64

BASE16_stoi={
    '0':0,'1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,
    '9':9,'a':10,'b':11,'c':12,'d':13,'e':14,'f':15
}
BASE16_itos='0123456789abcdef'
LEVEL=8086

def _MD100(pswin):
    psw1=hashlib.sha224()
    psw1.update(pswin.encode())
    psw2=hashlib.sha256()
    psw2.update(pswin[::-1].encode())
    psw3=hashlib.sha384()
    psw3.update(pswin.center(100,'a').encode())
    psw4=hashlib.sha512()
    psw4.update(pswin.swapcase().encode())
    psw5=hashlib.sha1()
    psw5.update(base64.b64encode(pswin.encode()))
    psw6=hashlib.md5()
    psw6.update(base64.b32encode(pswin.rjust(100,'a').encode()))
    return psw1.hexdigest()[0:16]+psw2.hexdigest()[0:16]+\
           psw3.hexdigest()[0:16]+psw4.hexdigest()[0:16]+\
           psw5.hexdigest()[0:16]+psw6.hexdigest()[0:16]

def oricode(pswin):
    def _plus(a,b):
        return BASE16_itos[(BASE16_stoi[a]+BASE16_stoi[b])%16]
    
    table={}
    ori=_MD100(pswin)
    start=ori
    for turn in range(LEVEL):
        start=_MD100(start)
    return ''.join((_plus(ori[x],start[x]) for x in range(len(ori))))

def maskcode(ori):
    def _not(x):
        return random.choice([a for a in BASE16_itos if a!=x])

    ans=[]
    for _ in range(3):
        lucky=random.sample(range(len(ori)),32)
        ans.append(''.join((
            (ori[ind] if ind in lucky else _not(ori[ind]))\
                for ind in range(len(ori))
        )))
    return '-'.join(ans)

def verify(ori,maskstr):
    masks=maskstr.split('-')
    for ind in range(len(masks)):
        if len([
                None for x in range(len(masks[ind])) if masks[ind][x]==ori[x]
                ])!=32:
            return False
    return True

def encode_psw(salt,username,password):
    return maskcode(oricode(json.dumps(
        [salt,username,password]
    )))

def verify_psw(masks,salt,username,password):
    test_ori=oricode(json.dumps([salt,username,password]))
    for mask in masks:
        if verify(test_ori,mask):
            return True
    return False

if __name__=='__main__':
    print(encode_psw(input('Salt: '),input('Username: '),input('Password: ')))
