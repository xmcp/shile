#coding=utf-8
from __future__ import division
import sys
if sys.version[0]=='2':
    reload(sys)
    sys.setdefaultencoding('utf-8')

import cherrypy
from cherrypy.lib.static import serve_file
from mako.template import Template
import os
import time
import shutil
import hasher

SALT='shILE'
server_path=os.getcwd().replace('\\','/')
deadline=10

def origin(name):
    out=''
    for now in name.split('_'):
        if now:
            out+=chr(int(now,16))
    return out
def urllike(name):
    out=''
    for a in name.replace('\\','/'):
        out+=(hex(ord(a))[2:]+'_')
    return out[:-1]
def chk():
    if deadline==0 or 'login' not in cherrypy.session:
        raise cherrypy.HTTPRedirect('/login')
def err(s):
    try:
        if 'username' in cherrypy.session.keys():
            l('[%s]Error: %s'%(cherrypy.session['username'],str(s)))
        else:
            l('Error: %s'%str(s))
        template=Template(filename=server_path+'/views/err.html',input_encoding='utf-8')
        return template.render(err=s)
    except Exception as e:
        cherrypy.response.headers['Content-Type'] = 'text/plain'
        return '在处理您的请求时，出现了一个错误导致无法继续：\n\n'+str(s)+'\n\n在处理该错误时，出现了另一个错误导致无法继续= =\n\n'+str(e)+'\n\n[ Shile ]'
def l(s):
    log.write('%s  %s\n'%(time.strftime('%Y-%m-%d %X',time.localtime()),s))
    global lastupdate
    lastupdate=time.strftime('%Y-%m-%d %X',time.localtime())
    log.flush()
def loadpass():
    global passs
    with open('pass.txt','r') as f:
        passs=[a.strip() for a in f.readlines()]
weakpass=('12345','123456','12345678','1234567890',
          '88888888','8888888888','66666666','6666666666',
          '00000000','0000000000',
          'admin','Admin','ADMIN','administrator','Administrator',
          'webshell','WEBSHELL','Webshell','WebShell','shile','Shile','SHILE',
          'cinba','xinsj','zhenyn','Zhenyn','zhenyn123','dramf','dramforever',
          'ftp','iloveyou','password','anonymous','qweasdzxc','username',
          'aaaaa','qqqqq','zzzzz','xxxxx','sssss',
          'qwert','QWERT','qwertyuiop','QWERTYUIOP')
def isweak(pwd):
    if len(pwd)<5 or pwd in weakpass:
        return True
    return False
def gethome(un):
    if os.path.isdir('/home/%s'%un):
        if os.path.isdir('/home/%s/doc'%un):
            return '/home/%s/doc'%un
        else:
            return '/home/%s'%un
    elif os.path.isdir('c:/users/%s/desktop'%un):
        return 'c:/users/%s/desktop'%un
    return None

class Shile:
    @cherrypy.expose
    def view(self,path):
        chk()
        try:
            path=urllike(origin(path))
            origins=origin(path)
        except Exception as e:
            return err(e)
        if os.path.isfile(origins):
            raise cherrypy.HTTPRedirect('/prev/'+path+'/'+os.path.split(origins)[1])
        if not origins.endswith('/'):
            path+='_2f'
            origins+='/'
        template=Template(filename=server_path+'/views/list.html',input_encoding='utf-8')
        try:
            return template.render(origins=origins[:-1],urllikes=path[:-3],files=os.listdir(origins),
                                    user=cherrypy.session['username'],serverpath=server_path)
        except Exception as e:
            return err(e)

    @cherrypy.expose
    def down(self,path,_):
        chk()
        cherrypy.session.release_lock()
        try:
            l('[%s]Download file: %s'%(cherrypy.session['username'],origin(path)))
            return serve_file(origin(path),"application/x-download", "attachment")
        except Exception as e:
            return err(e)

    @cherrypy.expose
    def login(self,username=None,password=None):
        global deadline
        if deadline==0:
            return '<a href="#/unlock" onclick=\'alert("Unlock failed.")\'>Click to Unlock</a>'
        if not password or not username:
            template=Template(filename=server_path+'/views/login.html',input_encoding='utf-8')
            return template.render(last=lastupdate,deadline=deadline)
        if isweak(password):
            return err('杜绝弱密码,从我做起!')
        if hasher.verify_psw(passs,SALT,username,password):
            cherrypy.session['login']=True
            cherrypy.session['username']=username
            l('[%s]Login successful'%username)
            deadline=10
            raise cherrypy.HTTPRedirect('/')
        l('[%s]Login failed(%s attempts left)'%(username,deadline))
        deadline-=1
        raise cherrypy.HTTPRedirect('/login')

    @cherrypy.expose
    def index(self):
        chk()
        home_path=gethome(cherrypy.session['username'])
        if not home_path:
            home_path=server_path+'/public/'
        raise cherrypy.HTTPRedirect('/view/'+urllike(home_path))

    @cherrypy.expose
    def logout(self):
        try:
            cherrypy.session['login']
        except KeyError:
            pass
        else:
            l('[%s]Logout'%cherrypy.session['username'])
            del cherrypy.session['login']
        raise cherrypy.HTTPRedirect('/')

    @cherrypy.expose
    def upload(self,path,upfile,upfilename,xhr=None):
        chk()
        if not path.endswith('_2f'):
            path+='_2f'
        if os.path.exists(origin(path)+upfilename):
            return err('%s 已经存在'%(origin(path)+upfilename))
        try:
            with open(origin(path)+upfilename,'wb') as f:
                l('[%s]Upload file: %s'%(cherrypy.session['username'],origin(path)+upfilename))
                nowprog=-1
                while upfile.file.tell()!=nowprog:
                    nowprog=upfile.file.tell()
                    f.write(upfile.file.read(65536))
        except Exception as e:
            return err(e)
        else:
            if xhr=='yes':
                return 'OK'
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
    def prev(self,path,_):
        chk()
        cherrypy.session.release_lock()
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

    @cherrypy.expose()
    def signup(self,username=None,password=None):
        template=Template(filename=server_path+'/views/signup.html',input_encoding='utf-8')
        if not username or not password:
            return template.render(result=False,username='',password='')
        if not username.isalnum() or not password.isalnum():
            return err('用户名或密码非法')
        if isweak(password):
            return err('杜绝弱密码,从我做起!')
        outhash=hasher.encode_psw(SALT,username,password)
        l('[%s]Creat password hash'%username)
        return template.render(result=True,hash=outhash,
                               username=username,password=password,serverpath=server_path)

    @cherrypy.expose
    def reloadpass(self):
        l('Reload password file')
        loadpass()
        raise cherrypy.HTTPRedirect('/login')

    @cherrypy.expose
    def move(self,oldpath,file,newpath):
        chk()
        try:
            newpath=origin(newpath)
            oldpath=origin(oldpath)
            os.chdir(oldpath)
            if newpath[-1] not in ('/','\\'):
                newpath+='/'
            l('[%s]Move file: %s/%s -> %s'%(cherrypy.session['username'],oldpath,origin(file),newpath))
            shutil.move(oldpath+'/'+origin(file),newpath)
        except Exception as e:
            return err(e)
        else:
            raise cherrypy.HTTPRedirect('/view/'+urllike(oldpath))
        finally:
            os.chdir(server_path)

    @cherrypy.expose
    def compose(self,filename,upload=None):
        chk()
        try:
            if upload:
                l('[%s]Edit file: %s'%(cherrypy.session['username'],origin(filename)))
                with open(origin(filename),'w') as f:
                    f.writelines(upload.split('\n'))
            else:
                l('[%s]Preview file: %s'%(cherrypy.session['username'],origin(filename)))
            with open(origin(filename),'r') as f:
                txt=f.read()
                template=Template(filename=server_path+'/views/compose.html',input_encoding='utf-8')
                return template.render(origins=origin(filename),urllikes=filename,txt=txt)
        except Exception as e:
            return err(e)
            
    @cherrypy.expose
    def unlock(self,username=None,password=None):
        global deadline
        if deadline!=0:
            raise cherrypy.HTTPRedirect('/login')
        if not username or not password:
            return '<form action="/unlock" method="post"><input name="username"><input name="password"><button type="reset">Go</button></form>'
        if hasher.verify_psw(passs,SALT,username,password):
            cherrypy.session['login']=True
            cherrypy.session['username']=username
            l('[%s]Unlock successful'%username)
            deadline=10
            raise cherrypy.HTTPRedirect('/')
        l('[%s]Unlock failed'%username)
        raise SystemExit()

    @cherrypy.expose
    def q(self,username,text=None):
        if not gethome(username):
            return err('%s 的用户目录不存在'%username)
        qfile=os.path.join(gethome(username),'q.txt')
        if not os.path.isfile(qfile):
            return err('%s 的存储文件不存在'%username)
        if not text:
            template=Template(filename=server_path+'/views/q.html',input_encoding='utf-8')
            return template.render(username=username)
        if len(text)>16384:
            return err('上传文件过大')
        with open(qfile,'a') as f:
            f.write('\n%s\n'%text)
        l('[%s]Add quicknote'%username)
        raise cherrypy.HTTPRedirect('/')
        
if 'PORT' in os.environ:
    shileport=int(os.environ['PORT'])
    print('Port detected as %d'%shileport)
else:
    shileport=3389

loadpass()
log=open('log.txt','a')
cherrypy.config.update({'tools.staticdir.root':server_path+'/'})
cherrypy.config.update({'server.socket_port':shileport})
l('Server start')
cherrypy.quickstart(Shile(),'',{
    'global': {
        'engine.autoreload.on':False,
        'request.show_tracebacks': False,
        'server.socket_host':'0.0.0.0',
        'tools.response_headers.on':True,
    },
    '/': {
        'tools.sessions.on':True,
        'tools.gzip.on': True,
    },
    '/public': {
        'tools.staticdir.on':True,
        'tools.staticdir.dir':'public',
    },
    '/q': {
         'tools.response_headers.headers':[('Access-Control-Allow-Origin','*')],
    },
    '/down': {
        'tools.gzip.on': False,
    }
})

