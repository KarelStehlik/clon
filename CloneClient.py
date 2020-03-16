from imports import *
from client_class import *
place = pyglet.window.Window(resizable=True,caption='CLOWN WARS!')
keys = key.KeyStateHandler()
place.set_minimum_size(100,100)
pyglet.gl.glClearColor(0.2,0.3,1,1)
map1=[]
players=[]
bullets=[]
CCpics=[]
gravity=0.65
side=int(requests.get("http://localhost:5000/GetSide").text)


def tick():
    for e in bullets:
        e.fly()
    global players, map1, camx, gravity
    if mouseheld:
        if time.time()-players[-1].lastshot>=players[-1].cd:
            players[-1].shoot(0,turn, mousex-players[-1].graphicx, mousey-players[-1].y-players[-1].hitboxh//2)
    for e in map1:
        e.graphicx=e.x-camx
    for e in players:
        e.graphicx=e.x-camx
        if ScanDown(e.x,e.y,map1):
            e.v-=gravity
        else:
            e.v=max(e.v,0)
        e.y+=max(e.v,-ScanDown(e.x,e.y,map1))
        if e.y<0:
            e.die(0,turn)
    place.push_handlers(keys)
    if keys[key.D]:
        players[-1].d(0,turn)
    if keys[key.A]:
        players[-1].a(0,turn)
        

@place.event
def on_draw():
    place.clear()
    glEnable(GL_BLEND)
    for e in map1+bullets:
        e.draw()
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    for e in players:
        e.draw()
    for e in CCpics:
        e[0].blit(e[1],e[2])
    

pyglet.app.run()

