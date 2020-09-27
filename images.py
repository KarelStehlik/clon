import pyglet
from constants import *
gunmanR=pyglet.resource.image("imagefolder/BGunman.png")
gunmanG=pyglet.resource.image("imagefolder/GGunman.png")
engiR=pyglet.resource.image("imagefolder/BEngi.png")
engiG=pyglet.resource.image("imagefolder/GEngi.png")
turretR=pyglet.resource.image("imagefolder/BTurret.png")
turretG=pyglet.resource.image("imagefolder/GTurret.png")
mixerR=pyglet.resource.image("imagefolder/BMixer.png")
mixerG=pyglet.resource.image("imagefolder/GMixer.png")
megamixerR=pyglet.resource.image("imagefolder/BMegaMixer.png")
megamixerG=pyglet.resource.image("imagefolder/GMegaMixer.png")
teleG=pyglet.resource.image("imagefolder/GTele.png")
teleR=pyglet.resource.image("imagefolder/BTele.png")
ZookaG=pyglet.resource.image("imagefolder/GZooka.png")
ZookaR=pyglet.resource.image("imagefolder/BZooka.png")
ShieldG=pyglet.resource.image("imagefolder/GShield.png").get_transform(flip_x=True)
ShieldR=pyglet.resource.image("imagefolder/BShield.png").get_transform(flip_x=True)
sprayerR=pyglet.resource.image("imagefolder/BSprayer.png")
sprayerG=pyglet.resource.image("imagefolder/GSprayer.png")

earthquack=pyglet.resource.image("imagefolder/earthquack.png")
earthquack.anchor_x=earthquack.width//2
SmashR=pyglet.resource.image("imagefolder/BSmash.png")
SmashG=pyglet.resource.image("imagefolder/GSmash.png")
SmashRL=pyglet.resource.image("imagefolder/BSmashL.png")
SmashGL=pyglet.resource.image("imagefolder/GSmashL.png")
SmashRR=pyglet.resource.image("imagefolder/BSmashR.png")
SmashGR=pyglet.resource.image("imagefolder/GSmashR.png")
Background=pyglet.resource.image("imagefolder/Background.png")
for e in [SmashR,SmashG]:
    e.width=80*SPRITE_SIZE_MULT
    e.height=120*SPRITE_SIZE_MULT
    e.anchor_x=e.width//2
for e in [SmashRL,SmashGL,SmashRR,SmashGR]:
    e.width=100*SPRITE_SIZE_MULT
    e.height=120*SPRITE_SIZE_MULT
for e in [SmashRR,SmashGR]:
    e.anchor_x=40*SPRITE_SIZE_MULT
for e in [SmashRL,SmashGL]:
    e.anchor_x=60*SPRITE_SIZE_MULT

MSmashR=pyglet.resource.image("imagefolder/BMSmash.png")
MSmashG=pyglet.resource.image("imagefolder/GMSmash.png")
MSmashRL=pyglet.resource.image("imagefolder/BMSmashL.png")
MSmashGL=pyglet.resource.image("imagefolder/GMSmashL.png")
MSmashRR=pyglet.resource.image("imagefolder/BMSmashR.png")
MSmashGR=pyglet.resource.image("imagefolder/GMSmashR.png")
for e in [MSmashR,MSmashG]:
    e.width=235*SPRITE_SIZE_MULT
    e.height=300*SPRITE_SIZE_MULT
    e.anchor_x=e.width//2
for e in [MSmashRL,MSmashGL,MSmashRR,MSmashGR]:
    e.width=250*SPRITE_SIZE_MULT
    e.height=300*SPRITE_SIZE_MULT
for e in [MSmashRR,MSmashGR]:
    e.anchor_x=100*SPRITE_SIZE_MULT
for e in [MSmashRL,MSmashGL]:
    e.anchor_x=150*SPRITE_SIZE_MULT

fire=pyglet.resource.image("imagefolder/fire.png")

tankR=pyglet.resource.image("imagefolder/BTank.png")
tankG=pyglet.resource.image("imagefolder/GTank.png")
for e in [tankR,tankG]:
    e.width=250
    e.height=90
    e.anchor_x=60

sprayerG.width=60*SPRITE_SIZE_MULT
sprayerG.height=80*SPRITE_SIZE_MULT
sprayerR.width=60*SPRITE_SIZE_MULT
sprayerR.height=80*SPRITE_SIZE_MULT

gunmanG.width=40*SPRITE_SIZE_MULT
gunmanG.height=70*SPRITE_SIZE_MULT
gunmanR.width=40*SPRITE_SIZE_MULT
gunmanR.height=70*SPRITE_SIZE_MULT

engiG.width=40*SPRITE_SIZE_MULT
engiG.height=70*SPRITE_SIZE_MULT
engiR.width=40*SPRITE_SIZE_MULT
engiR.height=70*SPRITE_SIZE_MULT

turretG.width=60*SPRITE_SIZE_MULT
turretG.height=54*SPRITE_SIZE_MULT
turretR.width=60*SPRITE_SIZE_MULT
turretR.height=54*SPRITE_SIZE_MULT
turretG.anchor_x=15
turretR.anchor_x=15

mixerG.width=35*SPRITE_SIZE_MULT
mixerG.height=60*SPRITE_SIZE_MULT
mixerR.width=35*SPRITE_SIZE_MULT
mixerR.height=60*SPRITE_SIZE_MULT

megamixerG.width=200*SPRITE_SIZE_MULT
megamixerG.height=300*SPRITE_SIZE_MULT
megamixerR.width=200*SPRITE_SIZE_MULT
megamixerR.height=300*SPRITE_SIZE_MULT

teleG.width=50*SPRITE_SIZE_MULT
teleG.height=80*SPRITE_SIZE_MULT
teleR.width=50*SPRITE_SIZE_MULT
teleR.height=80*SPRITE_SIZE_MULT

ZookaG.anchor_x=55*SPRITE_SIZE_MULT
ZookaG.width=200*SPRITE_SIZE_MULT
ZookaG.height=68*SPRITE_SIZE_MULT

ZookaR.anchor_x=55*SPRITE_SIZE_MULT
ZookaR.width=200*SPRITE_SIZE_MULT
ZookaR.height=68*SPRITE_SIZE_MULT

ShieldG.width=70*SPRITE_SIZE_MULT
ShieldR.width=70*SPRITE_SIZE_MULT
ShieldG.height=110*SPRITE_SIZE_MULT
ShieldR.height=110*SPRITE_SIZE_MULT
ShieldG.anchor_x=20*SPRITE_SIZE_MULT
ShieldR.anchor_x=20*SPRITE_SIZE_MULT

for e in [gunmanG,gunmanR,mixerG,mixerR,teleG,teleR,sprayerG,sprayerR,megamixerG,
          megamixerR,fire,engiG,engiR]:
    e.anchor_x=e.width//2
fire.anchor_y=fire.height//2
gunmanG.anchor_x-=5*SPRITE_SIZE_MULT
gunmanR.anchor_x-=5*SPRITE_SIZE_MULT

bullet=pyglet.resource.image("imagefolder/Bullet.png")
bullet.width=bullet.height=6*SPRITE_SIZE_MULT
bullet.anchor_x=bullet.anchor_y=3*SPRITE_SIZE_MULT

BazookaBullet=pyglet.resource.image("imagefolder/BazookaBullet.png")
BazookaBullet.width=int(BazookaBullet.width*SPRITE_SIZE_MULT/15)
BazookaBullet.height=int(BazookaBullet.height*SPRITE_SIZE_MULT/15)
BazookaBullet.anchor_x=BazookaBullet.width
BazookaBullet.anchor_y=BazookaBullet.height//2

buttonG=pyglet.image.load("imagefolder/GreenButton.png")
buttonR=pyglet.image.load("imagefolder/RedButton.png")
platform=pyglet.resource.image("imagefolder/platform.png")
platform.width=int(platform.width*SPRITE_SIZE_MULT)
platform.height=int(platform.height*SPRITE_SIZE_MULT)
platform.anchor_x=platform.anchor_y=0
cloneFrame=pyglet.resource.image("imagefolder/clone_select.png")
cloneFrame.height*=SPRITE_SIZE_MULT
cloneFrame.width*=SPRITE_SIZE_MULT
blue_arrow=pyglet.resource.image("imagefolder/blue_arrow.png")
red_arrow=pyglet.resource.image("imagefolder/red_arrow.png")
blue_arrow.width=red_arrow.width=int(blue_arrow.width*SPRITE_SIZE_MULT/15)
blue_arrow.height=red_arrow.height=int(blue_arrow.height*SPRITE_SIZE_MULT/15)
blue_arrow.anchor_x=int(blue_arrow.width/2)
red_arrow.anchor_x=int(red_arrow.width/2)

