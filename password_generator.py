#coding=utf-8
import hashlib
def encode_psw(prefix,pswin):
    pswin=prefix+pswin
    psw1=hashlib.sha224()
    psw1.update(pswin.encode())
    psw2=hashlib.sha256()
    psw2.update(pswin[::-1].encode())
    psw3=hashlib.sha384()
    psw3.update(pswin.center(50,'a').encode())
    psw4=hashlib.sha512()
    psw4.update(pswin.swapcase().encode())
    return psw1.hexdigest()[0:8]+psw2.hexdigest()[8:16]+psw3.hexdigest()[16:24]+psw4.hexdigest()[24:32]

if __name__=='__main__':
    print(encode_psw(input(),input()))
