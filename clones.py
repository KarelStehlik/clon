import images
import pyglet
class clone():
    def __init__(self,s,mapp):
        self.hp=s["hp"]
        self.height=s["height"]
        self.width=s["width"]
        self.Gskin=pyglet.sprite.Sprite(s["Gskin"])
        self.Rskin=pyglet.sprite.Sprite(s["Rskin"])
        self.spd=s["spd"]
        self.jump=s["jump"]
        self.vx,self.vy=0
        self.log=[]
    def a_start(self):
        self.log.append(["a",time.time()])

        #hp dmg  aspd bspd range   hbxX hbxY
BasicGuy={"hp":50,"dmg":20,"aspd":0.7,"bspd":5.2,"rang":550,"height":30,"width":70,
          "Gskin":images.gunmanG,
          "spd":3.5,"jump":14,"Rskin":images.gunmanR}
        #spd  jump
Mixer={"hp":100,"dmg":5,"aspd":0.05,"bspd":0.5,"rang":1,"height":35,"width":60,
          "Gskin":images.mixerG,
          "spd":5,"jump":16,"Rskin":images.mixerR}

possible_units=[BasicGuy, Mixer]
