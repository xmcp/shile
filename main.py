import cherrypy
from mako.template import Template
import os

server_path='C:/users/xiao/desktop/shile'

class shile:
    @cherrypy.expose
    def view(self,path):
        template = Template(filename=server_path+'/views/list.html',input_encoding='utf-8')
        def origin(name):
            return name.replace('>','\\')
        def urllike(name):
            return name.replace('\\','>')
        os.chdir(origin(path))
        return template.render(origins=origin(path),urllikes=urllike(path),files=os.listdir('.'))

cherrypy.quickstart(shile(),'','app.conf')
