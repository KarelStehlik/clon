import images
import pyglet
import time
import numpy as np
import math
import random
from constants import *
import serverchannels as channels
dudeg=pyglet.graphics.OrderedGroup(2)
ID=0
class Game():
    def __init__(self,mapp,gravity):
        self.clones=[[],[]]
        self.current_clones=[None,None]
        self.mapp=mapp
        self.gravity=gravity
        self.bullets=[]
        self.deadclones=[]
    def start_round(self):
        for e in self.clones[0]:
            e.start()
        for e in self.clones[1]:
            e.start()
    def summon(self,n,side):
        self.current_clones[side]=possible_units[n](self,
                                                    side)
    def tick(self,dt):
        for i in range(len(self.deadclones)):
            deed=self.deadclones.pop(0)
            deed.die()
        for e in self.clones[0]:
            e.move(dt)
            e.vy-=self.gravity*dt
        for e in self.clones[1]:
            e.move(dt)
            e.vy-=self.gravity*dt
        for e in self.bullets:
            e.move(dt)
        channels.send_both({"action":"update",
                                "hp0":self.current_clones[0].hp,
                                "hp1":self.current_clones[1].hp,
                                "x0":self.current_clones[0].x,
                                "y0":self.current_clones[0].y,
                                "x1":self.current_clones[1].x,
                                "y1":self.current_clones[1].y})
    def end_round(self):
        self.current_clones[0].die()
        self.current_clones[1].die()
        channels.send_both({"action":"endround","log0":self.current_clones[0].log,
                   "log1":self.current_clones[1].log})
    def summon_clones(self,c0,c1):
        self.summon(c0,0)
        self.summon(c1,1)
        channels.send_both({"action":"summon","c":c0,"s":0})
        channels.send_both({"action":"summon","c":c1,"s":1})
        self.start_round()
    def start_round(self):
        channels.send_both({"action":"start_round"})
        for e in self.clones[0]:
            e.start()
        for e in self.clones[1]:
            e.start()
def rect_intersect(ax1,ay1,ax2,ay2,bx1,by1,bx2,by2):
    return ax1<=bx2 and bx1<=ax2 and ay1<=by2 and by1<=ay2
def take_second(l):
    return l[1]
class clone():
    def __init__(self,game,**kwargs):
        global ID
        self.ID=ID
        ID+=1
        self.side=kwargs["side"]
        self.maxhp=kwargs["hp"]
        self.hp=self.maxhp
        self.height=kwargs["height"]
        self.width=kwargs["width"]
        self.spd=kwargs["spd"]
        self.jump=kwargs["jump"]
        self.mapp=game.mapp
        self.active=True
        self.exists=False
        self.vx=self.vy=0
        self.log=[]
        self.log_completed=0
        self.exist_time=0
        game.clones[self.side].append(self)
        self.l=game.clones
        self.facing=1
        if self.side==0:
            self.x=10
        else:
            self.x=1270
        self.y=100
        self.moving=0
        self.move_locked=False
        self.shoot_queue=[]
        self.game=game
    def add_shoot(self,a):
        self.shoot_queue.append(a)
    def schedule_die(self):
        if self.exists:
            self.game.deadclones.append(self)
    def start(self):
        if self.side==0:
            self.x=10
        else:
            self.x=1270
        self.y=100
        self.hp=self.maxhp
        self.exists=True
        self.log_completed=0
        self.exist_time=0
    def take_damage(self,amount,source):
        if self.exists:
            self.hp-=amount
            if self.hp<=0:
                self.schedule_die()
                channels.cn[1-self.side].get_money(self.cost//2+25)
    def on_ground(self):
        for e in self.mapp.platforms:
            if self.y==e.y+e.h and e.x<self.x<e.x+e.w:
                return True
        return False
    def a_start(self):
        if self.exists:
            if self.active:
                self.log.append(["a",self.exist_time])
            self.facing=self.moving=-1
            if not self.move_locked:
                self.vx=-self.spd
    def move_stop(self):
        if self.exists:
            if self.active:
                self.log.append(["stop",self.exist_time])
            self.moving=0
            if not self.move_locked:
                self.vx=0
    def d_start(self):
        if self.exists:
            if self.active:
                self.log.append(["d",self.exist_time])
            self.facing=self.moving=1
            if not self.move_locked:
                self.vx=self.spd
    def w(self):
        if self.exists:
            if self.active:
                self.log.append(["w",self.exist_time])
            if self.on_ground():
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
            if self.active:
                if len(self.shoot_queue)>0 and self.can_shoot():
                    self.shoot(self.shoot_queue.pop(0),0)
            else:
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
                            self.schedule_die()
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
                self.schedule_die()
                channels.cn[1-self.side].get_money(self.cost//2+25)
    def die(self):
        if self.exists:
            if self.active:
                self.log.append(["die",self.exist_time+0.1])
                self.active=False
                self.log.sort(key=take_second)
            self.moving=self.vy=self.vx=0
            self.exists=False
class Projectile():
    def __init__(self,x,y,vx,vy,enemies,rang,damage,game):
        self.x,self.y,self.vx,self.vy=x,y,vx,vy
        self.enemies=enemies
        self.l=game.bullets
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
        del self
def AOE_square(source,x,y,radius,targets,damage,knockback_x=0,knockback_y=0):
    for e in targets:
        if rect_intersect(x-radius,y-radius,x+radius,y+radius,e.x-e.width/2,
                          e.y,e.x+e.width/2,e.y+e.height):
            if (not knockback_x==0) or (not knockback_y==0):
                e.knockback(knockback_x,knockback_y)
            e.take_damage(damage,source)
###################################################################################################
class BasicGuyBullet(Projectile):
    def __init__(self,x,y,vx,vy,enemies,rang,damage,game):
        super().__init__(x,y,vx,vy,enemies,rang,damage,game)
    def on_collision(self,e):
        e.take_damage(self.damage,self)
        pyglet.clock.unschedule(self.die)
        self.die(0)
class BasicGuy(clone):
    cost=0
    def __init__(self,game,side):
        super().__init__(game,hp=50,height=70,
                         width=30,spd=200,jump=600,side=side)
        self.dmg=20
        self.aspd=0.7
        self.bspd=400
        self.rang=400
        self.lastshot=0
    def shoot(self,a,dt):
        if self.active:
            channels.send_both({"action":"shoot","a":a,"side":self.side})
            self.log.append(["shoot",self.exist_time,a])
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
                         self.rang,self.dmg,self.game)
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False
###########################################################################################################
class Mixer(clone):
    cost=0
    def __init__(self,game,side):
        super().__init__(game,hp=100,height=60,
                         width=30,spd=300,jump=700,side=side)
        self.dmg=200
        self.lastshot=0
        self.enemies=game.clones[1-self.side]
    def shoot(self,a,dt):
        AOE_square(self,self.x,self.y+self.height*2/3,self.width/2,self.enemies,self.dmg*dt)
    def can_shoot(self):
        return False
    def move(self,dt):
        super().move(dt)
        if self.exists:
            self.shoot([],dt)
#########################################################################################################
class Bazooka(clone):
    cost=500
    def __init__(self,game,side):
        super().__init__(game,hp=150,height=65,
                         width=65,spd=200,jump=600,side=side)
        self.dmg=70
        self.aspd=3
        self.bspd=500
        self.rang=800
        self.lastshot=0
        self.eradius=150
    def shoot(self,a,dt):
        if self.active:
            channels.send_both({"action":"shoot","a":a,"side":self.side})
            self.log.append(["shoot",self.exist_time,a])
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
                         self.rang,self.dmg,self.game,self.eradius)
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False
class BazookaBullet(Projectile):
    def __init__(self,x,y,vx,vy,enemies,rang,damage,game,radius):
        super().__init__(x,y,vx,vy,enemies,rang,damage,game)
        self.radius=radius
    def on_collision(self,e):
        AOE_square(self,self.x,self.y,self.radius,self.enemies,self.damage)
        pyglet.clock.unschedule(self.die)
        self.die(0)
##################################################################################################################
class Tele(clone):
    cost=250
    def __init__(self,game,side):
        super().__init__(game,hp=50,height=80,
                         width=44,spd=200,jump=600,side=side)
        self.dmg=60
        self.aspd=1.5
        self.lastshot=0
        self.radius=200
        self.enemies=game.clones[1-side]
        self.phase=255
    def shoot(self,a,dt):
        if self.active:
            channels.send_both({"action":"shoot","a":a,"side":self.side})
            self.log.append(["shoot",self.exist_time,a])
        self.x+=a[0]
        self.y+=a[1]
        self.phase=0
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False
    def move(self,dt):
        if (not self.phase==255) and self.exists:
            self.exist_time+=dt
            self.phase=min(self.phase+200*dt,255)
            if self.phase==255:
                AOE_square(self,self.x,self.y,self.radius,self.enemies,self.dmg)
        else:
            super().move(dt)
    def die(self):
        self.phase=255
        super().die()
#####################################################################
class Shield(clone):
    cost=400
    def __init__(self,game,side):
        super().__init__(game,hp=800,height=110,
                         width=70,spd=100,jump=400,side=side)
        self.dmg=20
        self.aspd=1
        self.bspd=300
        self.rang=300
        self.lastshot=0
    def shoot(self,a,dt):
        if self.active:
            channels.send_both({"action":"shoot","a":a,"side":self.side})
            self.log.append(["shoot",self.exist_time,a])
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
                         self.rang,self.dmg,self.game)
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False
    def take_damage(self,amount,source):
        if (source.x>self.x and self.facing==1) or (source.x<self.x and self.facing==-1):
            super().take_damage(amount/4,source)
        else:
            super().take_damage(amount,source)
##########################################################################################################################################
class Sprayer(clone):
    cost=500
    def __init__(self,game,side):
        super().__init__(game,hp=50,height=70,
                         width=30,spd=200,jump=600,side=side)
        self.dmg=20
        self.aspd=10
        self.bspd=400
        self.rang=400
        self.lastshot=0
    def shoot(self,a,dt):
        if self.active:
            bullet_data=[]
            for i in range(500):
                x=random.random()*random.choice([-1,1])
                y=random.random()*random.choice([-1,1])
                v=random.randint(int(self.bspd/1.1),self.bspd)
                if x==0:
                    vx=v
                    vy=0
                else:
                    vx=v/math.sqrt(y**2/x**2+1)
                    if x<0:
                        vx*=-1
                    vy=vx*y/x
                bul=BasicGuyBullet(self.x,self.y+self.height/2,vx,vy,self.l[1-self.side],
                                     self.rang,self.dmg,self.game)
                bullet_data.append([vx,vy])
            channels.send_both({"action":"shoot","a":bullet_data,"side":self.side})
            self.log.append(["shoot",self.exist_time,bullet_data])
        else:
            for e in a:
                bul=BasicGuyBullet(self.x,self.y+self.height/2,e[0],e[1],self.l[1-self.side],
                                     self.rang,self.dmg,self.game)
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False
###########################################################
class MegaMixer(clone):
    cost=100000
    def __init__(self,game,side):
        super().__init__(game,hp=50000,height=300,
                         width=200,spd=300,jump=700,side=side)
        self.dmg=10000
        self.enemies=game.clones[1-self.side]
        self.succ=100
    def shoot(self,a,dt):
        for e in self.enemies:
            if e.exists:
                if e.x<self.x:
                    e.x+=self.succ*dt
                else:
                    e.x-=self.succ*dt
                if e.y>self.y+self.height:
                    e.y-=1
        AOE_square(self,self.x,self.y+self.height*2/3,self.width/2,self.enemies,self.dmg*dt)
    def can_shoot(self):
        return False
    def move(self,dt):
        super().move(dt)
        if self.exists:
            self.shoot([],dt)
################################################################
class Smash(clone):
    cost=2000
    def __init__(self,game,side):
        super().__init__(game,hp=2000,height=120,
                         width=80,spd=150,jump=600,side=side)
        self.dmg=300
        self.aspd=1
        self.lastshot=0
        self.enemies=self.l[1-side]
        self.radius=20
    def shoot(self,a,dt):
        if self.active:
            channels.send_both({"action":"shoot","a":a,"side":self.side})
            self.log.append(["shoot",self.exist_time,a])
        if a[0]<=0:
            AOE_square(self,self.x-50,self.y+self.height/2,self.radius,self.enemies,self.dmg,
                       knockback_x=-500,knockback_y=1000)
        else:
            AOE_square(self,self.x+50,self.y+self.height/2,self.radius,self.enemies,self.dmg,
                       knockback_x=500,knockback_y=1000)
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False
############################################################################3
class MachineGun(clone):
    cost=1000
    def __init__(self,game,side):
        super().__init__(game,hp=200,height=70,
                         width=30,spd=140,jump=500,side=side)
        self.dmg=2
        self.aspd=0.0
        self.bspd=800
        self.rang=550
        self.lastshot=0
    def shoot(self,a,dt):
        if self.active:
            channels.send_both({"action":"shoot","a":a,"side":self.side})
            self.log.append(["shoot",self.exist_time,a])
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
                         self.rang,self.dmg,self.game)
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False
#################################################################################
class Tank(clone):
    cost=5000
    def __init__(self,game,side):
        super().__init__(game,hp=5000,height=80,
                         width=150,spd=100,jump=0,side=side)
        self.dmg=500
        self.aspd=3
        self.bspd=1000
        self.rang=1000
        self.lastshot=0
        self.eradius=80
        self.dmg2=100
        self.enemies=self.l[1-side]
    def shoot(self,a,dt):
        if self.active:
            channels.send_both({"action":"shoot","a":a,"side":self.side})
            self.log.append(["shoot",self.exist_time,a])
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
                         self.rang,self.dmg,self.game,self.eradius)
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False
    def shoot2(self,dt):
        for e in self.enemies:
            if e.exists and e.x-e.width/2<self.x<e.x+e.width/2 and e.y<self.y+self.height/2<e.y+e.height:
                e.take_damage(self.dmg2*dt,self)
    def w(self):
        pass
    def move(self,dt):
        super().move(dt)
        if self.exists:
            self.shoot2(dt)
    def knockback(self,a,b):
        super().knockback(a/4,b/3)
################################################################################
class Engi(clone):
    cost=5000
    def __init__(self,game,side):
        super().__init__(game,hp=50,height=70,
                         width=30,spd=200,jump=600,side=side)
        self.lastshot=0
        self.turrets=[]
        self.aspd=1
    def shoot(self,a,dt):
        Turret(self.game,self.side,self.turrets,self.x,self.y)
        if self.active:
            channels.send_both({"action":"shoot","a":a,"side":self.side})
            self.log.append(["shoot",self.exist_time,a])
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd and len(self.turrets)<=5:
            self.lastshot=t
            return True
        return False
class Turret(clone):
    def __init__(self,game,side,l2,x,y):
        super().__init__(game,hp=50,height=70,
                         width=30,spd=200,jump=600,side=side)
        self.l2=l2
        l2.append(self)
        self.lastshot=0
        self.aspd=0.1
        self.bspd=500
        self.rang=500
        self.dmg=10
        self.x,self.y=x,y
        self.exists=True
        self.enemies=self.l[1-self.side]
    def start(self):
        self.schedule_die()
    def die(self):
        self.l[self.side].remove(self)
        self.l2.remove(self)
        self.exists=False
        del self
    def take_damage(self,amount,source):
        if self.exists:
            self.hp-=amount
            if self.hp<=0:
                self.schedule_die()
    def move(self,dt):
        if self.exists:
            if self.can_shoot():
                self.aim_shoot()
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
                self.schedule_die()
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False
    def aim_shoot(self):
        d=self.rang**2
        for e in self.enemies:
            if e.exists:
                de=(self.x-e.x)**2+(self.y+self.height/2-e.y-e.height/2)**2
                if de<=d:
                    d=de
                    target=e
        if d<self.rang**2:
            self.shoot([target.x-self.x,target.y+target.height/2-self.y-self.height/2])                
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
                         self.rang,self.dmg,self.game)
############################################################################
class MegaSmash(clone):
    cost=20000
    def __init__(self,game,side):
        super().__init__(game,hp=10000,height=300,
                         width=200,spd=150,jump=1100,side=side)
        self.dmg=1500
        self.aspd=1
        self.lastshot=0
        self.enemies=self.l[1-side]
        self.radius=100
    def shoot(self,a,dt):
        if self.active:
            channels.send_both({"action":"shoot","a":a,"side":self.side})
            self.log.append(["shoot",self.exist_time,a])
        if a[0]<=0:
            AOE_square(self,self.x-80,self.y+self.height/3,self.radius,self.enemies,self.dmg,
                       knockback_x=-2500,knockback_y=1000)
        else:
            AOE_square(self,self.x+80,self.y+self.height/3,self.radius,self.enemies,self.dmg,
                       knockback_x=2500,knockback_y=1000)
    def can_shoot(self):
        if not self.exists:
            return False
        t=self.exist_time
        if t-self.lastshot>self.aspd:
            self.lastshot=t
            return True
        return False
#################################################################################3
possible_units=[BasicGuy,Mixer,Bazooka,Tele,Shield,Sprayer,MachineGun,Smash,Engi,
                Tank,MegaSmash,MegaMixer]
