import cherrypy
from cherrypy.lib.static import serve_file
from mako.template import Template
import os
import hashlib
import shutil
import subprocess

server_path=os.getcwd().replace('\\','/')

def origin(name):
    return name.replace('>','/')
def urllike(name):
    return name.replace('/','>').replace('\\','>')
def chk():
    try:
        cherrypy.session['login']
    except:
        raise cherrypy.HTTPRedirect('/login')

class shile:
    @cherrypy.expose
    def view(self,path):
        chk()
        if not os.path.isdir(origin(path)):
            raise cherrypy.HTTPRedirect('/down/'+path)
        if path[-1]!='>':
            path+='>'
        template=Template(filename=server_path+'/views/list.html',input_encoding='utf-8')
        return template.render(origins=origin(path[:-1]),urllikes=urllike(path[:-1]),files=os.listdir(origin(path)))

    @cherrypy.expose
    def down(self,path):
        chk()
        return serve_file(origin(path),"application/x-download", "attachment")

    @cherrypy.expose
    def login(self,password=None):
        if not password:
            template=Template(filename=server_path+'/views/login.html',input_encoding='utf-8')
            return template.render()
        psw=hashlib.sha256()
        psw.update(password.encode())
        truepsw=hashlib.sha256()
        truepsw.update(open('pass.txt','rb').read())
        if truepsw.hexdigest()!=psw.hexdigest():
            raise cherrypy.HTTPRedirect('/login')
        else:
            cherrypy.session['login']=True
            raise cherrypy.HTTPRedirect('/')

    @cherrypy.expose
    def index(self):
        chk()
        raise cherrypy.HTTPRedirect('/view/c:')

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
        if path[-1]!='>':
            path+='>'
        try:
            f=open(origin(path)+upfile.filename,'wb')
            f.write(upfile.file.read())
            f.close()
        except Exception as e:
            return str(e)
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
            return str(e)
        else:
            uriback=''
            for a in origin(path).split('/')[:-1]:
                    uriback+=(a+'/')
            raise cherrypy.HTTPRedirect('/view/'+urllike(uriback))

    @cherrypy.expose
    def rename(self,path,old,new):
        chk()
        try:
            os.rename(origin(path)+'/'+old,origin(path)+'/'+new)
        except Exception as e:
            return str(e)
        else:
            raise cherrypy.HTTPRedirect('/view/'+path)

    @cherrypy.expose
    def newfolder(self,path,name):
        chk()
        try:
            os.mkdir(origin(path)+'/'+name)
        except Exception as e:
            return str(e)
        else:
            raise cherrypy.HTTPRedirect('/view/'+path)

    @cherrypy.expose
    def run(self,path):
        chk()
        try:
            os.startfile((origin(path)))
        except Exception as e:
            return str(e)
        else:
            uriback=''
            for a in origin(path).split('/')[:-1]:
                    uriback+=(a+'/')
            raise cherrypy.HTTPRedirect('/view/'+urllike(uriback))

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

cherrypy.quickstart(shile(),'','app.conf')