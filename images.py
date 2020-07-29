import pyglet
gunmanR=pyglet.image.load("imagefolder/BGunman.png")
gunmanG=pyglet.image.load("imagefolder/GGunman.png")
mixerR=pyglet.image.load("imagefolder/BMixer.png")
mixerG=pyglet.image.load("imagefolder/GMixer.png")
gunmanG.width=40
gunmanG.height=70
gunmanR.width=40
gunmanR.height=70
mixerG.width=35
mixerG.height=60
mixerR.width=35
mixerR.height=60
mixerG.anchor_x-=11
mixerR.anchor_x-=11

bullet=pyglet.image.load("imagefolder/Bullet.png")
buttonG=pyglet.image.load("imagefolder/GreenButton.png")
buttonR=pyglet.image.load("imagefolder/RedButton.png")
platform=pyglet.image.load("imagefolder/platform.png")
cloneFrame=pyglet.image.load("imagefolder/clone_select.png")
