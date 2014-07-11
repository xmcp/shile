import cherrypy
from cherrypy.lib.static import serve_file
from mako.template import Template
import os

server_path='C:/users/xiao/desktop/shile'

class shile:
    @cherrypy.expose
    def view(self,path):
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
        return serve_file(path.replace('>','/'),"application/x-download", "attachment")

cherrypy.quickstart(shile(),'','app.conf')
