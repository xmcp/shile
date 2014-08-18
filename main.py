#coding=utf-8

from __future__ import division

import cherrypy
from cherrypy.lib.static import serve_file
from mako.template import Template
import os
import shutil
from password_generator import encode_psw

server_path=os.getcwd().replace('\\','/')
home_path=server_path

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
            return template.render(origins=origin(path[:-2]),urllikes=path[:-2],files=os.listdir(origin(path)))
        except Exception as e:
            return err(e)

    @cherrypy.expose
    def down(self,path):
        chk()
        try:
            return serve_file(origin(path),"application/x-download", "attachment")
        except Exception as e:
            return err(e)

    @cherrypy.expose
    def login(self,password=None):
        if not password:
            template=Template(filename=server_path+'/views/login.html',input_encoding='utf-8')
            return template.render()
        with open('pass.txt') as f:
            truepsw=f.read()
        if truepsw!=encode_psw(password):
            raise cherrypy.HTTPRedirect('/login')
        else:
            cherrypy.session['login']=True
            raise cherrypy.HTTPRedirect('/')

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
            del cherrypy.session['login']
        raise cherrypy.HTTPRedirect('/')

    @cherrypy.expose
    def upload(self,path,upfile):
        chk()
        if path[-1]!='2f':
            path+='2f'
        try:
            with open(origin(path)+upfile.filename,'wb') as f:
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
            os.rename(origin(path)+'/'+origin(old),origin(path)+'/'+origin(new))
        except Exception as e:
            return err(e)
        else:
            raise cherrypy.HTTPRedirect('/view/'+path)

    @cherrypy.expose
    def newfolder(self,path,name):
        chk()
        try:
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
            for now in range(0,len(cmdhex),2):
                cmdin+=chr(int(cmdhex[now:now+2],16))
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
            return txt
        except Exception as e:
            return err(e)

    @cherrypy.expose
    def newfile(self,path,filename,text):
        try:
            with open(origin(path)+'/'+filename,'w') as f:
                f.write(text)
        except Exception as e:
            return err(e)
        else:
            raise cherrypy.HTTPRedirect('/view/'+path)

cherrypy.config.update({'tools.staticdir.root':server_path+'/public'})
cherrypy.quickstart(shile(),'','app.conf')