import images
import pyglet
import time
import numpy as np
def rect_intersect(ax1,ay1,ax2,ay2,bx1,by1,bx2,by2):
    return ax1<=bx2 and bx1<=ax2 and ay1<=by2 and by1<=ay2
def take_second(l):
    return l[1]
class clone():
    def __init__(self,mapp,l,batch,**kwargs):
        l+=[self]
        self.hp=kwargs["hp"]
        self.height=kwargs["height"]
        self.width=kwargs["width"]
        self.skin=kwargs["skin"]
        self.batch=batch
        self.spd=kwargs["spd"]
        self.jump=kwargs["jump"]
        self.mapp=mapp
        self.active=True
        self.exists=False
        self.vx=self.vy=0
        self.log=[]
        self.x=0
        self.y=100
        self.log_completed=0
        self.exist_time=0
        self.side=kwargs["side"]
    def start(self):
        self.sprite=pyglet.sprite.Sprite(self.skin,10,100,batch=self.batch)
        self.x=10
        self.y=100
        self.exists=True
        self.log_completed=0
        self.exist_time=0
    def on_ground(self):
        for e in self.mapp.platforms:
            if self.y==e.y+e.h and e.x<self.x<e.x+e.w:
                return True
        return False
    def a_start(self):
        if self.active:
            self.log.append(["a",self.exist_time])
        self.vx=-self.spd
        self.skin.scale_x=-1
    def move_stop(self):
        if self.active:
            self.log.append(["stop",self.exist_time])
        self.vx=0
    def d_start(self):
        if self.active:
            self.log.append(["d",self.exist_time])
        self.vx=self.spd
        self.skin.scale_x=1
    def w(self):
        if self.active:
            self.log.append(["w",self.exist_time])
        if self.on_ground():
            self.vy=10
    def move(self,dt):
        if self.exists:
            self.exist_time+=dt
            if not self.active:
                for e in self.log[self.log_completed::]:
                    if e[1]<self.exist_time:
                        self.log_completed+=1
                        if e[0]=="d":
                            self.d_start()
                        elif e[0]=="stop":
                            self.move_stop()
                        elif e[0]=="a":
                            self.a_start()
                        elif e[0]=="w":
                            self.w()
                        elif e[0]=="shoot":
                            self.shoot(e[2],e[3])
                    else:
                        break
            self.x+=self.vx*dt
            ycap=0
            for e in self.mapp.platforms:
                if self.y>e.y and self.vy<0 and rect_intersect(self.x,
                                                               self.y+self.vy,
                                                               self.x,
                                                               self.y,
                                                               e.x,e.y+e.h,e.x+e.w,e.y+e.h):
                    ycap=max(e.y+e.h,ycap)
            self.y=max(ycap,self.y+self.vy)
            if not ycap==0:
                self.vy=0
            self.sprite.x=self.x
            self.sprite.y=self.y
    def die(self):
        if self.active:
            self.active=False
            self.log.sort(key=take_second)
        self.sprite.delete()
        self.exists=False
class BasicGuyBullet():
    def __init__(self,x,y,vx,vy,side,rang,l,batch):
        self.x,self.y,self.vx,self.vy=x,y,vx,vy
        self.side=side
        self.sprite=pyglet.sprite.Sprite(images.bullet,x,y,batch=batch)
        l.append(self)
        self.travelled,self.rang=0,rang
        self.speed=np.sqrt(self.vx**2+self.vy**2)
    def move(self,dt):
        self.travelled+=self.speed*dt
        self.x+=self.vx*dt
        self.y+=self.vy*dt
        self.sprite.x=self.x
        self.sprite.y=self.y
    def die(self):
        self.l.remove(self)
        self.sprite.delete()
        del self
class BasicGuy(clone):
    def __init__(self,mapp,l,bulletlist,batch,side):
        if side==0:
            sk=images.gunmanG
        else:
            sk=images.gunmanR
        super().__init__(mapp,l,batch,skin=sk,hp=50,height=30,
                         width=70,spd=200,jump=14,side=side)
        self.dmg=20
        self.aspd=0.7
        self.bspd=200
        self.rang=550
        self.bulletlist=bulletlist
    def shoot(self,x,y):
        if x==0:
            vx=self.bspd
            vy=0
        else:
            vx=self.bspd/np.sqrt(y**2/x**2+1)
            if x<0:
                vx*=-1
            vy=vx*y/x
        if self.active:
            self.log.append(["shoot",self.exist_time,x,y])
        BasicGuyBullet(self.x,self.y,vx,vy,self.side,self.rang,self.bulletlist,
                       self.batch)


Mixer={"hp":100,"dmg":5,"aspd":0.05,"bspd":0.5,"rang":1,"height":35,"width":60,
          "Gskin":images.mixerG,
          "spd":5,"jump":16,"Rskin":images.mixerR}

possible_units=[BasicGuy]
