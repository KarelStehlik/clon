from imports import *
import maps
import clones
from constants import *
def rect_intersect(ax1,ay1,ax2,ay2,bx1,by1,bx2,by2):
    return ax1<=bx2 and bx1<=ax2 and ay1<=by2 and by1<=ay2
class mode_choosing():
    def __init__(self,**kwargs):
        self.frames=[]
        self.Gclones=[]
        self.Rclones=[]
    def mouse_move(self,x,y,dx,dy):
        return
    def mouse_press(self,x,y,button,modifiers):
        return
class mapp():
    def __init__(self,mapp,batch):
        self.platforms=mapp
        for e in self.platforms:
            e.batch(batch)
class mode_testing():
    global screen
    def __init__(self,**kw):
        self.player_side=0
        self.win=kw["win"]
        self.mainBatch = pyglet.graphics.Batch()
        self.background=pyglet.graphics.vertex_list(4,
                                           ("v2i",[0,0,SCREEN_WIDTH,0,SCREEN_WIDTH,
                                                   SCREEN_HEIGHT,0,SCREEN_HEIGHT]),
                                           ("c3B",[100,100,255, 255,0,0, 255,50,50, 0,200,255]))
        if "map" in kw:
            self.mapp=kw["map"]
        else:
            self.mapp=random.choice(maps.maps)
        self.mapp=mapp(self.mapp,self.mainBatch)
        self.fpscount=pyglet.text.Label(x=5,y=5,text="aaa",color=(255,255,255,255))
        self.mousex,self.mousey,self.frames,self.sec,self.mouseheld=0,0,0,0,False
        self.gravity=1000
        self.clones=[[],[]]
        self.bullets=[]
        self.current_clones=[None,None]
        self.summon_clone()
    def summon_clone(self):
        self.current_clones[self.player_side]=random.choice(clones.possible_units)(self.mapp,
                                                                self.clones,
                                                                self.bullets,
                                                                self.mainBatch,
                                                                self.player_side)
        for e in self.clones[0]:
            e.start()
        for e in self.clones[1]:
            e.start()
    def mouse_move(self,x, y, dx, dy):
        self.mousex=x
        self.mousey=y
    def mouse_drag(self,x, y, dx, dy, button, modifiers):
        self.mouse_move(x,y,dx,dy)
    def tick(self,dt):
        if self.mouseheld:
            a=self.current_clones[self.player_side]
            a.attempt_shoot(self.mousex-a.x*SPRITE_SIZE_MULT,self.mousey-(a.y+a.height/2)*SPRITE_SIZE_MULT)
        for e in self.clones[0]:
            e.move(dt)
            e.vy-=self.gravity*dt
        for e in self.clones[1]:
            e.move(dt)
            e.vy-=self.gravity*dt
        for e in self.bullets:
            e.move(dt)
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
        self.background.draw(pyglet.gl.GL_QUADS)
        self.mainBatch.draw()
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
            self.summon_clone()
    def key_release(self,symbol,modifiers):
        if symbol==key.A or symbol==key.D:
            self.current_clones[self.player_side].move_stop()
    def mouse_press(self,x,y,button,modifiers):
        self.mouseheld=True
    def mouse_release(self,x,y,button,modifiers):
        self.mouseheld=False
    def resize(self,width,height):
        pass

class windoo(pyglet.window.Window):
    def start(self):
        self.currentMode=mode_testing(win=self)
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
