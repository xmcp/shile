import cherrypy
from cherrypy.lib.static import serve_file
from mako.template import Template
import os
import hashlib

server_path='C:/users/xiao/desktop/shile'

class shile:
    @cherrypy.expose
    def view(self,path):
        try:
            cherrypy.session['login']
        except:
            raise cherrypy.HTTPRedirect('/login')
        def origin(name):
            return name.replace('>','/')
        def urllike(name):
            return name.replace('/','>')
        if not os.path.isdir(origin(path)):
            raise cherrypy.HTTPRedirect('/down/'+path)
        if path[-1]!='>':
            path+='>'
        template = Template(filename=server_path+'/views/list.html',input_encoding='utf-8')
        return template.render(origins=origin(path[:-1]),urllikes=urllike(path[:-1]),files=os.listdir(origin(path)))

    @cherrypy.expose
    def down(self,path):
        try:
            cherrypy.session['login']
        except:
            raise cherrypy.HTTPRedirect('/login')
        return serve_file(path.replace('>','/'),"application/x-download", "attachment")

    @cherrypy.expose
    def login(self,password=None):
        if not password:
            template = Template(filename=server_path+'/views/login.html',input_encoding='utf-8')
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
        try:
            cherrypy.session['login']
        except:
            raise cherrypy.HTTPRedirect('/login')
        else:
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

cherrypy.quickstart(shile(),'','app.conf')