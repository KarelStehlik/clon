from imports import *
import maps
import clones
from constants import *
class mode():
    def __init__(self,win,batch):
        self.batch=batch
        self.mousex=self.mousey=self.sec=self.frames=0
        self.mouseheld=False
        self.win=win
        self.fpscount=pyglet.text.Label(x=5,y=5,text="aaa",color=(255,255,255,255))
    def mouse_move(self,x, y, dx, dy):
        self.mousex=x
        self.mousey=y
    def mouse_drag(self,x, y, dx, dy, button, modifiers):
        self.mouse_move(x,y,dx,dy)
    def tick(self,dt):
        self.win.switch_to()
        self.draw_all()
        self.fpscount.draw()
        self.check(dt)
        self.win.flip()
    def check(self,dt):
        self.sec+=dt
        self.frames+=1
        if self.sec>1:
            self.sec-=1
            self.fpscount.text=str(self.frames)
            self.frames=0
    def draw_all(self):
        self.win.clear()
        self.batch.draw()
    def key_press(self,symbol,modifiers):
        pass
    def key_release(self,symbol,modifiers):
        pass
    def mouse_press(self,x,y,button,modifiers):
        self.mouseheld=True
    def mouse_release(self,x,y,button,modifiers):
        self.mouseheld=False
    def resize(self,width,height):
        pass
def rect_intersect(ax1,ay1,ax2,ay2,bx1,by1,bx2,by2):
    return ax1<=bx2 and bx1<=ax2 and ay1<=by2 and by1<=ay2
class mode_choosing(mode):
    def __init__(self,win,batch,**kwargs):
        super().__init__(win,batch)
        self.ccgroup1=pyglet.graphics.OrderedGroup(3)
        self.ccgroup2=pyglet.graphics.OrderedGroup(4)
        self.win=win
        self.batch=batch
        self.cframes=[]
        self.imgs=[]
    def start(self,side):
        self.win.currentMode=self
        i=0
        w=images.cloneFrame.width
        for e in clones.possible_units:
            a=pyglet.sprite.Sprite(images.cloneFrame,x=(i*w+30)*SPRITE_SIZE_MULT,
                                   y=30*SPRITE_SIZE_MULT,batch=self.batch,group=self.ccgroup1)
            a.scale=SPRITE_SIZE_MULT
            if side==1:
                b=pyglet.sprite.Sprite(e.imageR,x=(i*w+30+w*e.imageR.anchor_x/e.imageG.width)*SPRITE_SIZE_MULT,
                                       y=53*SPRITE_SIZE_MULT,batch=self.batch,group=self.ccgroup2)
            else:
                b=pyglet.sprite.Sprite(e.imageG,x=(i*w+30+w*e.imageG.anchor_x/e.imageG.width)*SPRITE_SIZE_MULT,
                                       y=53*SPRITE_SIZE_MULT,batch=self.batch,group=self.ccgroup2)
            b.scale=SPRITE_SIZE_MULT*(w/e.imageG.width)*0.8
            self.cframes.append(a)
            self.imgs.append(b)
            i+=1
    def mouse_press(self,x,y,button,modifiers):
        super().mouse_press(x,y,button,modifiers)
        i=0
        for e in self.cframes:
            if e.x<x<e.x+e.width and e.y<y<e.y+e.height:
                self.win.currentMode=self.win.main
                self.win.main.summon_clone(i)
                self.end()
                return
            i+=1
    def end(self):
        for e in self.cframes:
            e.delete()
            del e
        for e in self.imgs:
            e.delete()
            del e
        self.cframes=[]
        self.imgs=[]
    def key_press(self,symbol,modifiers):
        if symbol in [key.RIGHT,key.D]:
            w=self.cframes[0].width
            for i in range(len(self.cframes)):
                self.cframes[i].x-=w
                self.imgs[i].x-=w
        elif symbol in [key.LEFT,key.A]:
            w=self.cframes[0].width
            for i in range(len(self.cframes)):
                self.cframes[i].x+=w
                self.imgs[i].x+=w
class mapp():
    def __init__(self,mapp,batch):
        self.platforms=mapp
        for e in self.platforms:
            e.batch(batch)
class mode_testing(mode):
    def __init__(self,win,batch,**kw):
        super().__init__(win,batch)
        self.player_side=0
        bg=pyglet.graphics.OrderedGroup(0)
        self.background=batch.add(4,pyglet.gl.GL_QUADS,bg,
                                           ("v2i",[0,0,SCREEN_WIDTH,0,SCREEN_WIDTH,
                                                   SCREEN_HEIGHT,0,SCREEN_HEIGHT]),
                                           ("c3B",[100,100,255, 255,0,0, 255,50,50, 0,200,255]))
        if "map" in kw:
            self.mapp=kw["map"]
        else:
            self.mapp=random.choice(maps.maps)
        self.mapp=mapp(self.mapp,self.batch)
        self.gravity=1000
        self.clones=[[],[]]
        self.bullets=[]
        self.current_clones=[None,None]
        self.summon_clone(0)
        self.total_time=0
    def choose_clone(self):
        self.player_side=1-self.player_side
        self.win.cc.start(self.player_side)
    def summon_clone(self,n):
        self.current_clones[self.player_side]=(clones.possible_units)[n](self.mapp,
                                                                self.clones,
                                                                self.bullets,
                                                                self.batch,
                                                                self.player_side)
        for e in self.clones[0]:
            e.start()
        for e in self.clones[1]:
            e.start()
    def mouse_drag(self,x, y, dx, dy, button, modifiers):
        self.mouse_move(x,y,dx,dy)
    def tick(self,dt):
        self.total_time+=dt
        if self.mouseheld:
            a=self.current_clones[self.player_side]
            a.attempt_shoot([self.mousex-a.x*SPRITE_SIZE_MULT,self.mousey-(a.y+a.height/2)*SPRITE_SIZE_MULT],
                            self.total_time,dt)
        for e in self.clones[0]:
            e.move(dt)
            e.vy-=self.gravity*dt
        for e in self.clones[1]:
            e.move(dt)
            e.vy-=self.gravity*dt
        for e in self.bullets:
            e.move(dt)
        super().tick(dt)
    def key_press(self,symbol,modifiers):
        if symbol==key.A:
            self.current_clones[self.player_side].a_start()
        if symbol==key.D:
            self.current_clones[self.player_side].d_start()
        if symbol==key.W:
            self.current_clones[self.player_side].w()
        if symbol==key.V:
            for e in self.clones[0]+self.clones[1]:
                e.die()
            self.choose_clone()
       # if symbol==key.M and modifiers==6:
       #     self.current_clones[self.player_side].aspd=0
       #     self.current_clones[self.player_side].bspd=1000
       #     self.current_clones[self.player_side].rang=1500
    def key_release(self,symbol,modifiers):
        if symbol==key.A or symbol==key.D:
            self.current_clones[self.player_side].move_stop()

class windoo(pyglet.window.Window):
    def start(self):
        self.mainBatch = pyglet.graphics.Batch()
        self.cc=mode_choosing(self,self.mainBatch)
        self.main=mode_testing(self,self.mainBatch)
        self.currentMode=self.main
    def on_mouse_motion(self,x, y, dx, dy):
        self.currentMode.mouse_move(x,y,dx,dy)
    def on_mouse_drag(self,x,y,dx,dy,button,modifiers):
        self.currentMode.mouse_drag(x,y,dx,dy,button,modifiers)
    def on_close(self):
        self.close()
        os._exit(0)
    def tick(self,dt):
        self.dispatch_events()
        self.currentMode.tick(dt)
    def on_key_press(self,symbol,modifiers):
        self.currentMode.key_press(symbol,modifiers)
    def on_key_release(self,symbol,modifiers):
        self.currentMode.key_release(symbol,modifiers)
    def on_mouse_release(self, x, y, button, modifiers):
        self.currentMode.mouse_release(x,y,button,modifiers)
    def on_resize(self,width,height):
        super().on_resize(width,height)
        self.currentMode.resize(width,height)
    def on_mouse_press(self,x,y,button,modifiers):
        self.currentMode.mouse_press(x,y,button,modifiers)
place = windoo(resizable=True,caption='test')
place.set_size(int(SCREEN_WIDTH*0.45),int(SCREEN_HEIGHT*2/3))
place.set_location(SCREEN_WIDTH//2,int(SCREEN_HEIGHT*1/6))
place.start()
pyglet.clock.schedule_interval(place.tick,1.0/60)
while True:
    pyglet.clock.tick()
