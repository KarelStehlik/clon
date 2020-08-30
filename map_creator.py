from imports import *
from constants import *
import images
class mode():
    def __init__(self,win,batch):
        self.batch=batch
        self.mousex=self.mousey=0
        self.win=win
    def mouse_move(self,x, y, dx, dy):
        self.mousex=x
        self.mousey=y
    def mouse_drag(self,x, y, dx, dy, button, modifiers):
        self.mouse_move(x,y,dx,dy)
    def tick(self,dt):
        self.win.switch_to()
        self.draw_all()
        self.win.flip()
    def draw_all(self):
        self.win.clear()
        self.batch.draw()
    def key_press(self,symbol,modifiers):
        pass
    def key_release(self,symbol,modifiers):
        pass
    def resize(self,width,height):
        pass
    def mouse_press(self,x,y,button,modifiers):
        pass
    def mouse_release(self,x,y,button,modifiers):
        pass
class mode_main(mode):
    def __init__(self,win,batch):
        super().__init__(win,batch)
        self.x=0
        self.y=0
        self.platforms=[]
        self.platform_imgs=[]
        with open("mapdata.txt", "r") as m:
            self.mapdata=[[g.split(",") for g in e.split("\n")] for e in m.read().split("/")]
        print(self.mapdata[0])
    def mouse_press(self,x,y,button,modifiers):
        self.x=x
        self.y=y
        self.active=pyglet.sprite.Sprite(images.platform,self.x,self.y,batch=self.batch)
        self.active.scale_x=self.active.scale_y=0
    def mouse_release(self,x,y,button,modifiers):
        self.platforms.append([self.x,self.y,x,y])
        self.active.scale_x=(x-self.x)/images.platform.width
        self.active.scale_y=(y-self.y)/images.platform.height
        self.platform_imgs.append(self.active)
    def mouse_drag(self,x, y, dx, dy, button, modifiers):
        self.active.scale_x=(x-self.x)/images.platform.width
        self.active.scale_y=(y-self.y)/images.platform.height

class windoo(pyglet.window.Window):
    def start(self):
        self.mainBatch = pyglet.graphics.Batch()
        self.sec=self.frames=0
        self.fpscount=pyglet.text.Label(x=5,y=5,text="aaa",color=(255,255,255,255),
                                        group=pyglet.graphics.OrderedGroup(4),batch=self.mainBatch)
        self.mouseheld=False
        self.main=mode_main(self,self.mainBatch)
        self.keys = key.KeyStateHandler()
        self.push_handlers(self.keys)
        self.current_mode=self.main
    def on_mouse_motion(self,x, y, dx, dy):
        self.current_mode.mouse_move(x,y,dx,dy)
    def on_mouse_drag(self,x,y,dx,dy,button,modifiers):
        self.current_mode.mouse_drag(x,y,dx,dy,button,modifiers)
    def on_close(self):
        self.close()
        os._exit(0)
    def tick(self,dt):
        self.dispatch_events()
        self.check(dt)
        self.current_mode.tick(dt)
    def on_key_press(self,symbol,modifiers):
        self.current_mode.key_press(symbol,modifiers)
    def on_key_release(self,symbol,modifiers):
        self.current_mode.key_release(symbol,modifiers)
    def on_mouse_release(self, x, y, button, modifiers):
        self.mouseheld=False
        self.current_mode.mouse_release(x,y,button,modifiers)
    def on_resize(self,width,height):
        super().on_resize(width,height)
        self.current_mode.resize(width,height)
    def on_mouse_press(self,x,y,button,modifiers):
        self.mouseheld=True
        self.current_mode.mouse_press(x,y,button,modifiers)
    def on_deactivate(self):
        self.minimize()
    def check(self,dt):
        self.sec+=dt
        self.frames+=1
        if self.sec>1:
            self.sec-=1
            self.fpscount.text=str(self.frames)
            self.frames=0
place = windoo(resizable=True,caption='test',fullscreen=True)
place.start()
pyglet.clock.schedule_interval(place.tick,1.0/60)
while True:
    pyglet.clock.tick()
