#!flask/bin/python
from imports import *
scheduler = BackgroundScheduler()
scheduler.start()
app = Flask(__name__)
s=0     #s0 s1
players=[]
bullets=[]
gravity=0.65
turn=0
from server_class import *

def ScanDown(x,y,map1):
    r=100000000
    for e in map1:
        if e.x<x and e.x+e.width>x and e.y+e.height<=y:
            r=min(r,y-e.y-e.height)
    return(r)

def tick():
    global clock
    clock.tick()
    for e in bullets:
        e.fly()
    global players, map1, gravity
    for e in players:
        e.fall(map1)
        if e.active and e.shooting:
            e.attempt_to_shoot(mousex-e.graphicx, mousey-e.y-e.hitboxh//2)
        

scheduler.add_job(tick,'interval',seconds=0.02)

        
    
def NewGame():
    global players, current_map, bullets,gravity,turn,s
    players=[]
    current_map=random.choice(maps)
    bullets=[]
    gravity=0.65
    turn=0
    s=0

NewGame()

@app.route('/GetSide')
def side():
    global s
    if s==0:
        s+=1
        return Response('0', mimetype='text/plain')
    if s==1:
        s+=1
        return Response('1', mimetype='text/plain')
    NewGame()
    return Response('0', mimetype='text/plain')

@app.route("/Test",methods=["GET","POST"])
def blah():
    a=str(request.data)[2:-1]
    print(a)
    return "-".join(a.split(" "))

@app.route("/a_press",methods=["GET","POST"])
def a_press():
    side=str(request.data)[2:-1]
    global players
    for e in players:
        if e.active==1 and e.side=side:
            e.walkingA=True
            return 'done'

@app.route("/d_press",methods=["GET","POST"])
def d_press():
    side=str(request.data)[2:-1]
    global players
    for e in players:
        if e.active==1 and e.side=side:
            e.walkingD=True
            return 'done'

@app.route("/w_press",methods=["GET","POST"])
def w_press():
    side=str(request.data)[2:-1]
    global players
    for e in players:
        if e.active==1 and e.side=side:
            e.w()

@app.route("/a_release",methods=["GET","POST"])
def a_release():
    side=str(request.data)[2:-1]
    global players
    for e in players:
        if e.active==1 and e.side=side:
            e.walkingA=False
            return 'done'

@app.route("/b_release",methods=["GET","POST"])
def a_release():
    side=str(request.data)[2:-1]
    global players
    for e in players:
        if e.active==1 and e.side=side:
            e.walkingA=True
            return 'done'

@app.route("/shoot",methods=["GET","POST"])
def a_press():
    dat=str(request.data)[2:-1].split(" ")
    side=dat[0]
    global players
    for e in players:
        if e.active==1 and e.side=side:
            e.attempt_to_shoot(dat[1],dat[2])
            return 'done'

atexit.register(lambda: scheduler.shutdown())


if __name__ == '__main__':
    app.run(host= '0.0.0.0', debug=True)


    
