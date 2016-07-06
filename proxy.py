#-*- coding:utf-8 -*-
import socket  
import thread  
import urlparse  
import select  
import sys
  
BUFLEN=8192  
  
class Proxy(object):  
    def __init__(self,conn,addr):  
        self.source=conn  
        self.request=""  
        self.headers={}  
        self.destnation=socket.socket(socket.AF_INET,socket.SOCK_STREAM)  
        self.run()  
  
    def get_headers(self):  
        header=''  
        while True:  
            header+=self.source.recv(BUFLEN)  
            index=header.find('\n')  
            if index > 0:  
                break  
        print header
        firstLine=header[:index]  
        self.request=header[index+1:]  
        self.headers['method'],self.headers['path'],self.headers['protocol']=firstLine.split()  

        if self.headers['method'] == 'CONNECT':
            self.https = 1
            hostname = self.headers['path']
            addr, port=hostname.split(':')  
            self.port=int(port)
        else:
            self.https = 0
            url=urlparse.urlparse(self.headers['path'])  
            hostname=url[1]  
            port="80"  
            if hostname.find(':') >0:  
                addr, self.port=hostname.split(':')  
            else:  
                addr=hostname  
            self.port=int(port)

        self.ip=socket.gethostbyname(addr)  
  
    def conn_destnation(self):  
        if self.https != 1:
            self.destnation.connect((self.ip,self.port))  
            data="%s %s %s\r\n" %(self.headers['method'],self.headers['path'],self.headers['protocol'])  
            self.destnation.send(data+self.request)  
            #print data+self.request  
        else:
            self.destnation.connect((self.ip,self.port))  
            data = "HTTP/1.1 200 Connection Established\r\nconnection: close\r\n\r\n" 
            self.source.send(data)  
            #print data

  
    def render_source(self):  
        readsocket=[self.destnation,self.source]  
        while True:  
            data=''  
            (rlist,wlist,elist)=select.select(readsocket,[],[],3)  
            if rlist:  
                if self.https!=1:
                    data=rlist[0].recv(BUFLEN) 
                    if len(data)>0:  
                        self.source.send(data)  
                    else:  
                        break
                else:
                    data=rlist[0].recv(BUFLEN) 
                    if len(data)>0:  
                        if rlist[0] == self.destnation:
                            self.source.send(data)  
                        elif rlist[0] == self.source:
                            self.destnation.send(data)  
                    else:  
                        #pass
                        break
                    
                    
					
    def run(self):  
        self.get_headers()  
        self.conn_destnation()  
        self.render_source()    
  
  
class Server(object):  
  
    def __init__(self,host,port,handler=Proxy):  
        self.host=host  
        self.port=port  
        self.server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)  
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  
        self.server.bind((host,port))  
        self.server.listen(5)  
        self.handler=handler  
  
    def start(self):  
        while True:  
            try:  
                conn,addr=self.server.accept()  
                thread.start_new_thread(self.handler,(conn,addr))  
            except (KeyboardInterrupt, SystemExit): 
                sys.exit()
            except:  
                pass  
  
  
if __name__=='__main__':  
    print "Proxy begin"
    s=Server('',8193)  
    s.start()
