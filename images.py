import pyglet
from constants import *
gunmanR=pyglet.resource.image("imagefolder/BGunman.png")
gunmanG=pyglet.resource.image("imagefolder/GGunman.png")
mixerR=pyglet.resource.image("imagefolder/BMixer.png")
mixerG=pyglet.resource.image("imagefolder/GMixer.png")
teleG=pyglet.resource.image("imagefolder/GTele.png")
teleR=pyglet.resource.image("imagefolder/BTele.png")
ZookaG=pyglet.resource.image("imagefolder/GZooka.png")
ZookaR=pyglet.resource.image("imagefolder/BZooka.png")
gunmanG.width=40*SPRITE_SIZE_MULT
gunmanG.height=70*SPRITE_SIZE_MULT
gunmanR.width=40*SPRITE_SIZE_MULT
gunmanR.height=70*SPRITE_SIZE_MULT
mixerG.width=35*SPRITE_SIZE_MULT
mixerG.height=60*SPRITE_SIZE_MULT
mixerR.width=35*SPRITE_SIZE_MULT
mixerR.height=60*SPRITE_SIZE_MULT
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
for e in [gunmanG,gunmanR,mixerG,mixerR,teleG,teleR]:
    e.anchor_x=e.width//2
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
platform=pyglet.image.load("imagefolder/platform.png")
platform.width=int(platform.width*SPRITE_SIZE_MULT)
platform.height=int(platform.height*SPRITE_SIZE_MULT)
cloneFrame=pyglet.image.load("imagefolder/clone_select.png")
