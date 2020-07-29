from imports import *
class mode_choosing():
    def __init__(self,**kwargs):
        return
    def mouse_move(self,x,y,dx,dy):
        return
    def mouse_press(self,x,y,button,modifiers):
        return
class mode_testing():
    def __init__(self,**kw):
        global testBlocks
        self.mainBatch = pyglet.graphics.Batch()
        self.fpscount=pyglet.text.Label(x=5,y=5,text="aaa",color=(255,255,255,255))
        self.win=kw["win"]
        self.mousex,self.mousey,self.frames,self.sec,self.mouseheld=0,0,0,0,False
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
        self.mainBatch.draw()
    def key_press(self,symbol,modifiers):
        return
    def mouse_press(self,x,y,button,modifiers):
        self.mouseheld=True
    def mouse_release(self,x,y,button,modifiers):
        self.mouseheld=False

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
    def on_mouse_release(self, x, y, button, modifiers):
        self.currentMode.mouse_release(x,y,button,modifiers)
place = windoo(resizable=True,caption='test')
display = pyglet.canvas.Display()
screen = display.get_default_screen()
place.set_size(int(screen.width*0.45),int(screen.height*2/3))
place.set_location(screen.width//2,int(screen.height*1/6))
place.start()
pyglet.clock.schedule_interval(place.tick,1.0/60)
while True:
    pyglet.clock.tick()
