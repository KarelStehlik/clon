import images
import pyglet
import time
import numpy as np
import math
import random
from constants import *
dudeg=pyglet.graphics.OrderedGroup(2)
camx=0
def rect_intersect(ax1,ay1,ax2,ay2,bx1,by1,bx2,by2):
    return ax1<=bx2 and bx1<=ax2 and ay1<=by2 and by1<=ay2
def take_second(l):
    return l[1]
class clone():
    def __init__(self,mapp,l,batch,**kwargs):
        self.side=kwargs["side"]
        if self.side==0:
            self.skin=self.imageG
        else:
            self.skin=self.imageR
        self.maxhp=kwargs["hp"]
        self.hp=self.maxhp
        self.height=kwargs["height"]
        self.width=kwargs["width"]
        self.batch=batch
        self.spd=kwargs["spd"]
        self.jump=kwargs["jump"]
        self.mapp=mapp
        self.active=True
        self.exists=False
        self.vx=self.vy=0
        self.log=[]
        self.log_completed=0
        self.exist_time=0
        l[self.side]+=[self]
        self.l=l
        self.facing=1
        self.moving=0
        self.move_locked=False
        self.hpbar_scale=SPRITE_SIZE_MULT*self.width/images.buttonG.width
        if self.side==0:
            self.x=10
        else:
            self.x=1270
        self.y=100
        self.vpoint=self.x-1280/2
        self.sprite=pyglet.sprite.Sprite(self.skin,10,100,batch=self.batch,group=dudeg)
        self.hpbar=pyglet.sprite.Sprite(images.buttonG,self.x,self.y+self.height,batch=self.batch,group=dudeg)
        self.hpbar.scale=self.hpbar_scale
        self.hpbar.scale_y=5/self.hpbar.height
        arro=[images.blue_arrow,images.red_arrow][self.side]
        self.additional_images=[]
        self.additional_images.append([pyglet.sprite.Sprite(arro,
                                                           x=self.x*SPRITE_SIZE_MULT,
                                                           y=(self.y+self.height+10)*SPRITE_SIZE_MULT,
                                                            group=pyglet.graphics.OrderedGroup(3),batch=self.batch),
                                       0,self.height+10])
    def start(self):
        if self.side==0:
            self.x=10
        else:
            self.x=1270
        self.y=100
        self.sprite.batch=self.batch
        self.hpbar.batch=self.batch
        self.hpbar.scale_x=1
        self.hp=self.maxhp
        self.exists=True
        self.log_completed=0
        self.exist_time=0
    def update_health(self,health):
        self.hp=health
        if self.hp<=0:
            self.die()
            return
        self.hpbar.scale_x=self.hp/self.maxhp
    def take_damage(self,amount,source):
        if not self.active:
            self.update_health(self.hp-amount)
    def update_pos(self,x,y):
        self.sprite.update(x=(x-camx)*SPRITE_SIZE_MULT,y=y*SPRITE_SIZE_MULT)
        self.hpbar.update(x=(x-self.width//2-camx)*SPRITE_SIZE_MULT,y=(y+self.height)*SPRITE_SIZE_MULT)
        self.x,self.y=x,y
        self.vpoint=self.x-1280/2
        for e in self.additional_images:
            e[0].update(x=(self.x+e[1]-camx)*SPRITE_SIZE_MULT,y=(self.y+e[2])*SPRITE_SIZE_MULT)
    def on_ground(self):
        for e in self.mapp.platforms:
            if self.y==e.y+e.h and e.x<self.x<e.x+e.w:
                return True
        return False
    def a_start(self):
        if self.exists:
            self.sprite.scale_x=-1
            self.facing=-1
            self.moving=-1
            if not self.move_locked:
                self.vx=-self.spd
    def move_stop(self):
        if self.exists:
            self.vx=0
            self.moving=0
            if not self.move_locked:
                self.vx=0
    def d_start(self):
        if self.exists:
            self.sprite.scale_x=1
            self.facing=1
            self.moving=1
            if not self.move_locked:
                self.vx=self.spd
    def w(self):
        if self.on_ground() and self.exists:
            self.vy=self.jump
    def knockback(self,x,y):
        if self.exists:
            self.y+=1
            self.vx+=x
            self.vy+=y
            self.move_locked=True
    def move(self,dt):
        if self.exists:
            if self.move_locked and self.on_ground():
                self.move_locked=False
                self.vx=self.moving*self.spd
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
                            self.shoot(e[2],dt)
                        elif e[0]=="die":
                            self.die()
                            return
                    else:
                        break
                self.x=self.x+self.vx*dt
                ycap=-500
                for e in self.mapp.platforms:
                    if self.y>e.y and self.vy<0 and rect_intersect(self.x,
                                                                   self.y+self.vy*dt,
                                                                   self.x,
                                                                   self.y,
                                                                   e.x,e.y+e.h,e.x+e.w,e.y+e.h):
                        ycap=max(e.y+e.h,ycap)
                self.y=max(ycap,self.y+self.vy*dt)
                if not ycap==-500:
                    self.vy=0
                if self.y<=-500:
                    self.die()
            self.update_pos(self.x,self.y)
    def die(self):
        if self.exists:
            if self.active:
                self.active=False
                self.log.sort(key=take_second)
                self.additional_images=[]
            self.vx=0
            self.vy=0
            self.sprite.batch=None
            self.hpbar.batch=None
            self.exists=False
class Projectile():
    def __init__(self,x,y,vx,vy,enemies,rang,damage,l,batch,model):
        self.x,self.y,self.vx,self.vy=x,y,vx,vy
        self.enemies=enemies
        self.sprite=pyglet.sprite.Sprite(model,x,y,batch=batch,group=dudeg)
        self.l=l
        self.l.append(self)
        self.rang=rang
        self.speed=math.sqrt(self.vx**2+self.vy**2)
        pyglet.clock.schedule_once(self.die,self.rang/self.speed)
        self.damage=damage
    def move(self,dt):
        self.x+=self.vx*dt
        self.y+=self.vy*dt
        if self.collide():
            return
        self.sprite.update(x=SPRITE_SIZE_MULT*(self.x-camx),y=SPRITE_SIZE_MULT*self.y)
    def collide(self):
        for e in self.enemies:
            if e.exists and e.x-e.width/2<self.x<e.x+e.width/2 and e.y<self.y<e.y+e.height:
                self.on_collision(e)
                return True
        return False
    def on_collision(self,e):
        pass
    def die(self,dt):
        self.l.remove(self)
        self.sprite.delete()
        del self
###################################################################################################
class BasicGuyBullet(Projectile):
    def __init__(self,x,y,vx,vy,enemies,rang,damage,l,batch):
        super().__init__(x,y,vx,vy,enemies,rang,damage,l,batch,images.bullet)
    def on_collision(self,e):
        e.take_damage(self.damage,self)
        pyglet.clock.unschedule(self.die)
        self.die(0)
class BasicGuy(clone):
    cost=0
    imageG=images.gunmanG
    imageR=images.gunmanR
    def __init__(self,mapp,l,bulletlist,batch,side):
        super().__init__(mapp,l,batch,hp=50,height=70,
                         width=30,spd=200,jump=600,side=side)
        self.dmg=20
        self.aspd=0.7
        self.bspd=400
        self.rang=400
        self.bulletlist=bulletlist
        self.lastshot=0
    def shoot(self,a,dt):
        x=a[0]
        y=a[1]
        if x==0:
            vx=self.bspd
            vy=0
        else:
            vx=self.bspd/math.sqrt(y**2/x**2+1)
            if x<0:
                vx*=-1
            vy=vx*y/x
        a=BasicGuyBullet(self.x,self.y+self.height/2,vx,vy,self.l[1-self.side],
                         self.rang,self.dmg,self.bulletlist,self.batch)
    def can_shoot(self):
        t=self.exist_time
        if t-self.lastshot>self.aspd and self.exists:
            self.lastshot=t
            return True
        return False
###########################################################################################################
class Mixer(clone):
    cost=0
    imageG=images.mixerG
    imageR=images.mixerR
    def __init__(self,mapp,l,bulletlist,batch,side):
        super().__init__(mapp,l,batch,hp=100,height=60,
                         width=30,spd=300,jump=700,side=side)
        self.dmg=200
        self.lastshot=0
        self.enemies=l[1-self.side]
    def shoot(self,a,dt):
        for e in self.enemies:
            if e.exists and e.x-e.width/2<self.x<e.x+e.width/2 and e.y<self.y+self.height/2<e.y+e.height:
                e.take_damage(self.dmg*dt,self)
    def can_shoot(self):
        return False
    def move(self,dt):
        super().move(dt)
        if self.exists:
            self.shoot([],dt)
#########################################################################################################
class Bazooka(clone):
    cost=500
    imageG=images.ZookaG
    imageR=images.ZookaR
    def __init__(self,mapp,l,bulletlist,batch,side):
        super().__init__(mapp,l,batch,hp=150,height=65,
                         width=65,spd=200,jump=600,side=side)
        self.dmg=70
        self.aspd=3
        self.bspd=500
        self.rang=800
        self.bulletlist=bulletlist
        self.lastshot=0
        self.eradius=150
    def shoot(self,a,dt):
        x=a[0]
        y=a[1]
        if x==0:
            vx=self.bspd
            vy=0
        else:
            vx=self.bspd/math.sqrt(y**2/x**2+1)
            if x<0:
                vx*=-1
            vy=vx*y/x
        a=BazookaBullet(self.x,self.y+self.height/2,vx,vy,self.l[1-self.side],
                         self.rang,self.dmg,self.bulletlist,self.batch,self.eradius)
    def can_shoot(self):
        t=self.exist_time
        if t-self.lastshot>self.aspd and self.exists:
            self.lastshot=t
            return True
        return False
class BazookaBullet(Projectile):
    def __init__(self,x,y,vx,vy,enemies,rang,damage,l,batch,radius):
        super().__init__(x,y,vx,vy,enemies,rang,damage,l,batch,images.BazookaBullet)
        self.radius=radius
        if vx==0:
            if vy<0:
                self.sprite.rotation=-90
            else:
                self.sprite.rotation==90
        elif vx>0:
            self.sprite.rotation=-math.atan(vy/vx)*180/math.pi
        else:
            self.sprite.rotation=180-math.atan(vy/vx)*180/math.pi
    def on_collision(self,e):
        for i in self.enemies:
            if i.exists and (i.x-self.x)**2+(i.y+i.height//2-self.y)**2<=self.radius**2:
                i.take_damage(self.damage,self)
        pyglet.clock.unschedule(self.die)
        self.die(0)
##################################################################################################################
class Tele(clone):
    cost=250
    imageG=images.teleG
    imageR=images.teleR
    def __init__(self,mapp,l,bulletlist,batch,side):
        super().__init__(mapp,l,batch,hp=50,height=80,
                         width=44,spd=200,jump=600,side=side)
        self.dmg=60
        self.aspd=3
        self.lastshot=0
        self.radius=200
        self.enemies=l[1-side]
        self.phase=255
    def shoot(self,a,dt):
        self.x+=a[0]
        self.y+=a[1]
        self.phase=0
        self.update_pos(self.x,self.y)
    def can_shoot(self):
        t=self.exist_time
        if t-self.lastshot>self.aspd and self.exists:
            self.lastshot=t
            return True
        return False
    def move(self,dt):
        if self.phase != 255:
            self.exist_time+=dt
            self.update_pos(self.x,self.y)
            self.phase=min(self.phase+150*dt,255)
            self.sprite.opacity=self.phase
            if self.phase==255:
                for i in self.enemies:
                    if i.exists and (i.x-self.x)**2+(i.y+i.height//2-self.y)**2<=self.radius**2:
                        i.take_damage(self.dmg,self)
        else:
            super().move(dt)
    def die(self):
        self.phase=255
        self.sprite.opacity=self.phase
        super().die()
##########################################################################
class Shield(clone):
    cost=400
    imageG=images.ShieldG
    imageR=images.ShieldR
    def __init__(self,mapp,l,bulletlist,batch,side):
        super().__init__(mapp,l,batch,hp=500,height=110,
                         width=70,spd=100,jump=400,side=side)
        self.dmg=20
        self.aspd=1
        self.bspd=300
        self.rang=300
        self.bulletlist=bulletlist
        self.lastshot=0
    def shoot(self,a,dt):
        x=a[0]
        y=a[1]
        if x==0:
            vx=self.bspd
            vy=0
        else:
            vx=self.bspd/math.sqrt(y**2/x**2+1)
            if x<0:
                vx*=-1
            vy=vx*y/x
        a=BasicGuyBullet(self.x,self.y+self.height/2,vx,vy,self.l[1-self.side],
                         self.rang,self.dmg,self.bulletlist,self.batch)
    def can_shoot(self):
        t=self.exist_time
        if t-self.lastshot>self.aspd and self.exists:
            self.lastshot=t
            return True
        return False
    def take_damage(self,amount,source):
        if (source.x>self.x and self.facing==1) or (source.x<self.x and self.facing==-1):
            super().take_damage(amount/4,source)
        else:
            super().take_damage(amount,source)
##############################################################################
class Sprayer(clone):
    cost=500
    imageG=images.sprayerG
    imageR=images.sprayerR
    def __init__(self,mapp,l,bulletlist,batch,side):
        super().__init__(mapp,l,batch,hp=50,height=70,
                         width=30,spd=200,jump=600,side=side)
        self.dmg=20
        self.aspd=10
        self.rang=400
        self.bulletlist=bulletlist
        self.lastshot=0
    def shoot(self,a,dt):
        for e in a:
            bul=BasicGuyBullet(self.x,self.y+self.height/2,e[0],e[1],self.l[1-self.side],
                             self.rang,self.dmg,self.bulletlist,self.batch)
    def can_shoot(self):
        t=self.exist_time
        if t-self.lastshot>self.aspd and self.exists:
            self.lastshot=t
            return True
        return False
#########################################################################################
class MegaMixer(clone):
    cost=100000
    imageG=images.megamixerG
    imageR=images.megamixerR
    def __init__(self,mapp,l,bulletlist,batch,side):
        super().__init__(mapp,l,batch,hp=50000,height=300,
                         width=200,spd=300,jump=700,side=side)
        self.dmg=10000
        self.enemies=l[1-self.side]
        self.succ=100
    def shoot(self,a,dt):
        for e in self.enemies:
            if e.exists:
                if e.x<self.x:
                    e.x+=self.succ*dt
                else:
                    e.x-=self.succ*dt
                if e.y>self.y+self.height:
                    e.y-=self.succ*dt
                if rect_intersect(self.x-self.width/2,self.y,self.x+self.width/2,self.y+self.height,
                                  e.x-e.width/2,e.y,e.x+e.width/2,e.y+e.height):
                    e.take_damage(self.dmg*dt,self)
    def can_shoot(self):
        return False
    def move(self,dt):
        super().move(dt)
        if self.exists:
            self.shoot([],dt)
####################################################################
class Smash(clone):
    cost=2000
    imageG=images.SmashG
    imageR=images.SmashR
    def __init__(self,mapp,l,bulletlist,batch,side):
        super().__init__(mapp,l,batch,hp=2000,height=120,
                         width=80,spd=150,jump=600,side=side)
        self.dmg=300
        self.aspd=1
        self.lastshot=0
        self.enemies=l[1-side]
        self.smashing="none"
        self.smashing_time=0
        self.radius=20
        if side==0:
            self.spryte=pyglet.sprite.Sprite(self.imageG,10,100,batch=None,group=dudeg)
            self.left=pyglet.sprite.Sprite(images.SmashGL,self.sprite.x,self.sprite.y,batch=None,group=dudeg)
            self.right=pyglet.sprite.Sprite(images.SmashGR,self.sprite.x,self.sprite.y,batch=None,group=dudeg)
        else:
            self.spryte=pyglet.sprite.Sprite(self.imageR,10,100,batch=None,group=dudeg)
            self.left=pyglet.sprite.Sprite(images.SmashRL,self.sprite.x,self.sprite.y,batch=None,group=dudeg)
            self.right=pyglet.sprite.Sprite(images.SmashRR,self.sprite.x,self.sprite.y,batch=None,group=dudeg)
    def shoot(self,a,dt):
        if a[0]<=0:
            for e in self.enemies:
                if rect_intersect(self.x-50-self.radius,self.y+self.height/2-self.radius,
                                  self.x-50+self.radius,self.y+self.height/2+self.radius,
                                  e.x-e.width/2,e.y,e.x+e.width/2,e.y+e.height):
                    e.knockback(-500,1000)
                    e.take_damage(self.dmg,self)
            self.smashing="left"
            self.sprite.batch=None
            if self.facing==1:
                self.sprite=self.left
                self.sprite.batch=self.batch
            else:
                self.sprite=self.right
                self.sprite.batch=self.batch
            self.sprite.scale_x=self.facing
        else:
            for e in self.enemies:
                if rect_intersect(self.x+50-self.radius,self.y+self.height/2-self.radius,
                                  self.x+50+self.radius,self.y+self.height/2+self.radius,
                                  e.x-e.width/2,e.y,e.x+e.width/2,e.y+e.height):
                    e.knockback(500,1000)
                    e.take_damage(self.dmg,self)
            self.smashing="right"
            self.sprite.batch=None
            if self.facing==1:
                self.sprite=self.right
                self.sprite.batch=self.batch
            else:
                self.sprite=self.left
                self.sprite.batch=self.batch
            self.sprite.scale_x=self.facing
        self.smashing_time=0.3
    def can_shoot(self):
        t=self.exist_time
        if t-self.lastshot>self.aspd and self.exists:
            self.lastshot=t
            return True
        return False
    def move(self,dt):
        if self.smashing_time>0:
            self.smashing_time-=min(dt,self.smashing_time)
            if self.smashing_time==0:
                self.sprite.batch=None
                self.spryte.scale_x=self.sprite.scale_x
                self.sprite=self.spryte
                self.sprite.batch=self.batch
                self.smashing="none"
        super().move(dt)
    def die(self):
        self.sprite.batch=None
        self.sprite=self.spryte
        self.sprite.batch=None
        self.smashing="none"
        self.smashing_time=0
        super().die()
###########################################################################
class MachineGun(clone):
    cost=1000
    imageG=images.gunmanG
    imageR=images.gunmanR
    def __init__(self,mapp,l,bulletlist,batch,side):
        super().__init__(mapp,l,batch,hp=200,height=70,
                         width=30,spd=140,jump=500,side=side)
        self.dmg=1.0
        self.aspd=0.0
        self.bspd=800
        self.rang=550
        self.bulletlist=bulletlist
        self.lastshot=0
    def shoot(self,a,dt):
        x=a[0]
        y=a[1]
        if x==0:
            vx=self.bspd
            vy=0
        else:
            vx=self.bspd/math.sqrt(y**2/x**2+1)
            if x<0:
                vx*=-1
            vy=vx*y/x
        a=BasicGuyBullet(self.x,self.y+self.height/2,vx,vy,self.l[1-self.side],
                         self.rang,self.dmg,self.bulletlist,self.batch)
    def can_shoot(self):
        t=self.exist_time
        if t-self.lastshot>self.aspd and self.exists:
            self.lastshot=t
            return True
        return False
###########################################################################
class Tank(clone):
    cost=5000
    imageG=images.tankG
    imageR=images.tankR
    def __init__(self,mapp,l,bulletlist,batch,side):
        super().__init__(mapp,l,batch,hp=5000,height=80,
                         width=150,spd=100,jump=0,side=side)
        self.dmg=500
        self.aspd=3
        self.bspd=1000
        self.rang=1000
        self.bulletlist=bulletlist
        self.lastshot=0
        self.eradius=80
        self.dmg2=100
        self.enemies=l[1-side]
    def shoot(self,a,dt):
        x=a[0]
        y=a[1]
        if x==0:
            vx=self.bspd
            vy=0
        else:
            vx=self.bspd/math.sqrt(y**2/x**2+1)
            if x<0:
                vx*=-1
            vy=vx*y/x
        a=BazookaBullet(self.x,self.y+self.height/2,vx,vy,self.l[1-self.side],
                         self.rang,self.dmg,self.bulletlist,self.batch,self.eradius)
    def can_shoot(self):
        t=self.exist_time
        if t-self.lastshot>self.aspd and self.exists:
            self.lastshot=t
            return True
        return False
    def w(self):
        pass
    def knockback(self,a,b):
        super().knockback(a/5,b/4)
    def shoot2(self,dt):
        for e in self.enemies:
            if e.exists and e.x-e.width/2<self.x<e.x+e.width/2 and e.y<self.y+self.height/2<e.y+e.height:
                e.take_damage(self.dmg2*dt,self)
    def move(self,dt):
        super().move(dt)
        if self.exists:
            self.shoot2(dt)
###########################################################################
class Squad():
    cost=0
    imageG=images.tankG
    imageR=images.tankR
    def __init__(self,mapp,l,bulletlist,batch,side):
        self.clones=[]
        self.clones.append(BasicGuy(mapp,l,bulletlist,batch,side))
        self.clones.append(Tank(mapp,l,bulletlist,batch,side))
        self.active=True
        self.exists=True
        self.hp=[e.hp for e in self.clones]
        self.x=[e.x for e in self.clones]
        self.y=[e.y for e in self.clones]
        self.vpoint=0
    def update_health(self,hp):
        for i in range(len(self.clones)):
            self.clones[i].update_health(hp[i])
    def update_pos(self,x,y):
        for i in range(len(self.clones)):
            self.clones[i].update_pos(x[i],y[i])
    def a_start(self):
        for e in self.clones:
            e.a_start()
    def move_stop(self):
        for e in self.clones:
            e.move_stop()
    def d_start(self):
        for e in self.clones:
            e.d_start()
    def w(self):
        for e in self.clones:
            e.w()
    def move(self,dt):
        self.vpoint=self.clones[0].vpoint
        for e in self.clones:
            e.move(dt)
    def die(self):
        if self.exists:
            if self.active:
                self.active=False
            self.exists=False
        for e in self.clones:
            e.die()
    def can_shoot(self):
        c=self.clones
        return c[0].can_shoot() or c[1].can_shoot()
    def shoot(self,a,dt):
        for e in self.clones:
            if e.can_shoot():
                e.shoot(a,dt)
######################################################################################
class Engi(clone):
    cost=0
    imageG=images.gunmanG
    imageR=images.gunmanR
    def __init__(self,mapp,l,bulletlist,batch,side):
        super().__init__(mapp,l,batch,hp=50,height=70,
                         width=30,spd=200,jump=600,side=side)
        self.bulletlist=bulletlist
        self.lastshot=0
        self.turrets=[]
        self.aspd=1
    def shoot(self,a,dt):
        Turret(self.mapp,self.l,self.batch,self.bulletlist,self.side,self.turrets,self.x,self.y)
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False
class Turret(clone):
    imageG=images.gunmanG
    imageR=images.gunmanR
    def __init__(self,mapp,l,batch,bulletlist,side,l2,x,y):
        super().__init__(mapp,l,batch,hp=50,height=70,
                         width=30,spd=200,jump=600,side=side)
        self.l2=l2
        l2.append(self)
        self.bulletlist=bulletlist
        self.lastshot=0
        self.aspd=0.1
        self.bspd=500
        self.rang=500
        self.dmg=20
        self.update_pos(x,y)
        self.exists=True
        self.active=False
        self.additional_images=[]
    def die(self):
        self.l[self.side].remove(self)
        self.l2.remove(self)
        self.exists=False
        del self
    def move(self,dt):
        if self.exists:
            if self.move_locked and self.on_ground():
                self.move_locked=False
                self.vx=self.moving*self.spd
            self.exist_time+=dt
            self.x=self.x+self.vx*dt
            ycap=-500
            for e in self.mapp.platforms:
                if self.y>e.y and self.vy<0 and rect_intersect(self.x,
                                                                   self.y+self.vy*dt,
                                                                   self.x,
                                                                   self.y,
                                                                   e.x,e.y+e.h,e.x+e.w,e.y+e.h):
                    ycap=max(e.y+e.h,ycap)
            self.y=max(ycap,self.y+self.vy*dt)
            if not ycap==-500:
                self.vy=0
            if self.y<=-500:
                self.die()
            self.update_pos(self.x,self.y)
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False
    def shoot(self,a):
        x=a[0]
        y=a[1]
        if x==0:
            vx=self.bspd
            vy=0
        else:
            vx=self.bspd/math.sqrt(y**2/x**2+1)
            if x<0:
                vx*=-1
            vy=vx*y/x
        a=BasicGuyBullet(self.x,self.y+self.height/2,vx,vy,self.l[1-self.side],
                         self.rang,self.dmg,self.bulletlist,self.batch)
############################################################################
possible_units=[BasicGuy,Mixer,Bazooka,Tele,Shield,Sprayer,MachineGun,Smash,
                Tank,MegaMixer,Engi]#,Squad]
