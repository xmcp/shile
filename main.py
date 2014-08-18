#coding=utf-8

from __future__ import division

import cherrypy
from cherrypy.lib.static import serve_file
from mako.template import Template
import os
import time
import shutil
from password_generator import encode_psw

ver='v7.3'
server_path=os.getcwd().replace('\\','/')
home_path='/home/shile/doc' if os.path.exists('/home/shile/doc') else server_path

def origin(name):
    out=''
    for now in range(0,len(name),2):
        out+=chr(int(name[now:now+2],16))
    return out
def urllike(name):
    out=''
    for a in name.replace('\\','/'):
        out+=hex(ord(a))[2:]
    return out
def chk():
    try:
        cherrypy.session['login']
    except:
        raise cherrypy.HTTPRedirect('/login')
def err(s):
    try:
        template=Template(filename=server_path+'/views/err.html',input_encoding='utf-8')
        return template.render(err=s)
    except Exception as e:
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        return '在处理您的请求时，出现了一个错误导致无法继续：\n\n'+s+'\n\n在处理该错误时，出现了另一个致命错误：\n\n'+e+'\n\nShile'
def l(s):
    log.write('%s  %s\n'%(time.strftime('%Y-%m-%d %X',time.localtime()),s))
    log.flush()
class shile:
    @cherrypy.expose
    def view(self,path):
        chk()
        path=urllike(origin(path))
        try:
            origin(path)
        except Exception as e:
            return err(e)
        if os.path.isfile(origin(path)):
            raise cherrypy.HTTPRedirect('/down/'+path)
        if path[-2:]!='2f':
            path+='2f'
        template=Template(filename=server_path+'/views/list.html',input_encoding='utf-8')
        try:
            l('[%s]View directory: %s'%(cherrypy.session['username'],origin(path)))
            return template.render(origins=origin(path[:-2]),urllikes=path[:-2],files=os.listdir(origin(path)))
        except Exception as e:
            return err(e)

    @cherrypy.expose
    def down(self,path):
        chk()
        try:
            l('[%s]Download file: %s'%(cherrypy.session['username'],origin(path)))
            return serve_file(origin(path),"application/x-download", "attachment")
        except Exception as e:
            return err(e)

    @cherrypy.expose
    def login(self,username=None,password=None):
        if not password or not username:
            template=Template(filename=server_path+'/views/login.html',input_encoding='utf-8')
            return template.render(ver=ver)
        enusername=encode_psw(username)
        enpassword=encode_psw(password)
        for a in passs:
            if a[0]==enusername and a[1]==enpassword:
                cherrypy.session['login']=True
                cherrypy.session['username']=username
                l('[%s]Login successful'%username)
                raise cherrypy.HTTPRedirect('/')
        l('[%s]Login failed'%username)
        raise cherrypy.HTTPRedirect('/login')

    @cherrypy.expose
    def index(self):
        chk()
        raise cherrypy.HTTPRedirect('/view/'+urllike(home_path))

    @cherrypy.expose
    def logout(self):
        try:
            cherrypy.session['login']
        except:
            pass
        else:
            l('[%s]Logout'%cherrypy.session['username'])
            del cherrypy.session['login']
        raise cherrypy.HTTPRedirect('/')

    @cherrypy.expose
    def upload(self,path,upfile):
        chk()
        if path[-1]!='2f':
            path+='2f'
        try:
            with open(origin(path)+upfile.filename,'wb') as f:
                l('[%s]Upload file: %s'%(cherrypy.session['username'],origin(path)+upfile.filename))
                nowprog=-1
                while upfile.file.tell()!=nowprog:
                    nowprog=upfile.file.tell()
                    f.write(upfile.file.read(65536))
        except Exception as e:
            return err(e)
        else:
            raise cherrypy.HTTPRedirect('/view/'+path)

    @cherrypy.expose
    def delete(self,path):
        chk()
        try:
            l('[%s]Delete file: %s'%(cherrypy.session['username'],origin(path)))
            if os.path.isdir(origin(path)):
                shutil.rmtree(origin(path))
            else:
                os.remove(origin(path))
        except Exception as e:
            return err(e)
        else:
            raise cherrypy.HTTPRedirect('/view/'+urllike(os.path.split(origin(path))[0]))

    @cherrypy.expose
    def rename(self,path,old,new):
        chk()
        try:
            l('[%s]Rename file: %s/%s -> %s'%(cherrypy.session['username'],origin(path),origin(old),origin(new)))
            os.rename(origin(path)+'/'+origin(old),origin(path)+'/'+origin(new))
        except Exception as e:
            return err(e)
        else:
            raise cherrypy.HTTPRedirect('/view/'+path)

    @cherrypy.expose
    def newfolder(self,path,name):
        chk()
        try:
            l('[%s]Creat directory: %s/%s'%(cherrypy.session['username'],origin(path),origin(name)))
            os.mkdir(origin(path)+'/'+origin(name))
        except Exception as e:
            return err(e)
        else:
            raise cherrypy.HTTPRedirect('/view/'+path)

    @cherrypy.expose
    def cmd(self,cmdhex):
        chk()
        cmdin=''
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        try:
            cmdin=origin(cmdhex)
            l('[%s]Execute command: %s'%(cherrypy.session['username'],cmdin))
        except Exception as e:
            return '命令处理错误：\n\n'+str(e)
        out=os.popen(cmdin)
        return '> '+str(cmdin)+'\n\n'+out.read()

    @cherrypy.expose
    def prev(self,path):
        chk()
        try:
            with open(origin(path),'rb') as f:
                txt=f.read()
            cherrypy.response.headers['Content-Type'] = 'text/plain'
            l('[%s]Preview file: %s'%(cherrypy.session['username'],origin(path)))
            return txt
        except Exception as e:
            return err(e)

    @cherrypy.expose
    def newfile(self,path,filename,text):
        try:
            l('[%s]Creat file: %s/%s'%(cherrypy.session['username'],origin(path),filename))
            with open(origin(path)+'/'+filename,'w') as f:
                f.write(text)
        except Exception as e:
            return err(e)
        else:
            raise cherrypy.HTTPRedirect('/view/'+path)

#read passwords
passs=[]
with open('pass.txt') as f:
    for a in f.readlines():
        passs.append((a.split(' ')[0],a.split(' ')[1].strip()))

log=open('log.txt','a')
cherrypy.config.update({'tools.staticdir.root':server_path+'/public'})
l('Server start')
cherrypy.quickstart(shile(),'','app.conf')