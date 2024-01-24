import pygame
import pymunk
import pymunk.pygame_util
from threading import Timer
import random
import math
import json
from PIL import Image, ImageFilter
import time
pygame.init()


screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode(flags=pygame.SCALED,vsync=1,size=(screen_width,screen_height))
pygame.display.set_caption("Angry Amogus")
pygame.display.set_icon(pygame.image.load("icon.ico").convert_alpha())
clock = pygame.time.Clock()
space = pymunk.Space()
space.sleep_time_threshold = 1
space.gravity = (0, 981)

allLevels = []
currentLevelIndex = 0

with open("levels.json") as levels:
    allLevels = json.load(levels)["levels"]

with open("save.json") as save:
    saveData = json.load(save)

currentLevelPassed = saveData["currentLevel"]
currentLevelPassed = len(allLevels)-1

drawOptions = pymunk.pygame_util.DrawOptions(screen)

canWin = True
groundOffset = 50

labelFont = "miriamlibre"

#groups and masks
collisionMasks = {
    0: [0b000001,0b011011],          #amogus
    1: [0b000010,0b111111],          #wall
    2: [0b000100,0b000010],          #idleAmogus
    3: [0b001000,0b111011],          #block
    4: [0b010000,0b111011],          #impostor
    5: [0b100000,0b111111]           #amogusObjects

}
maxPullMag = 200

impostorImg = pygame.image.load("./img/impostor.png").convert_alpha()
slingShotImage = pygame.transform.scale(pygame.image.load("./img/slingShot.png").convert_alpha(),(225,275))
mainMenuImage = pygame.image.load("./img/bg.png").convert_alpha()
threeStarsImage = pygame.image.load("./img/stars.png").convert_alpha()

birdTemplates = {
    "red": {
        "size": [40,40],
        "imageSize": [40,40],
        "image": pygame.image.load("./img/amogus.png").convert_alpha(),
        "func": None,
        "activateAfterHit": False
    },
    "cyan": {
        "size": [40,40],
        "imageSize": [40,40],
        "image": pygame.image.load("./img/cyan-amogus.png").convert_alpha(),
        "func": lambda x: cyanBird(x),
        "activateAfterHit": False
    },
    "yellow": {
        "size": [40,40],
        "imageSize": [40,40],
        "image": pygame.image.load("./img/yellow-amogus.png").convert_alpha(),
        "func": lambda x: yellowBird(x),
        "activateAfterHit": True
    },
    "blue": {
        "size": [40,40],
        "imageSize": [40,40],
        "image": pygame.image.load("./img/blue-amogus.png").convert_alpha(),
        "func": lambda x: blueBird(x),
        "activateAfterHit": True
    },
    "green": {
        "size": [40,40],
        "imageSize": [40,40],
        "image": pygame.image.load("./img/green-amogus.png").convert_alpha(),
        "func": lambda x: greenBird(x),
        "activateAfterHit": True
    }
}
blockTemplates = {
    "glass": {
        "bodyType": "dynamic",
        "size": (20,100),
        "image": pygame.image.load("./img/glass.png").convert_alpha(),
        "broken": pygame.image.load("./img/glass-broken.png").convert_alpha(),
        "particle": pygame.image.load("./img/glass-particle.png").convert_alpha(),
        "mass": 5,
        "durability": 5,
        "color": "white",
        "breakVelocity": 100,
        "score": 50,
        "slowingFactor": 0.7,
        "breakSound": pygame.mixer.Sound("./sound/glass-break.wav"),
        "hitSound": pygame.mixer.Sound("./sound/glass-hit.wav"),
        "shape": {
            "type": "box"
        }
    },
    "glass-square": {
        "bodyType": "dynamic",
        "size": (50,50),
        "image": pygame.image.load("./img/glass-square.png").convert_alpha(),
        "broken": pygame.image.load("./img/glass-square-broken.png").convert_alpha(),
        "particle": pygame.image.load("./img/glass-particle.png").convert_alpha(),
        "mass": 5,
        "durability": 5,
        "color": "white",
        "breakVelocity": 100,
        "score": 50,
        "slowingFactor": 0.7,
        "breakSound": pygame.mixer.Sound("./sound/glass-break.wav"),
        "hitSound": pygame.mixer.Sound("./sound/glass-hit.wav"),
        "shape": {
            "type": "box"
        }
    },
    "glass-tri": {
        "bodyType": "dynamic",
        "size": (50,50),
        "image": pygame.image.load("./img/glass-tri.png").convert_alpha(),
        "broken": pygame.image.load("./img/glass-tri-broken.png").convert_alpha(),
        "particle": pygame.image.load("./img/glass-particle.png").convert_alpha(),
        "mass": 5,
        "durability": 5,
        "color": "white",
        "breakVelocity": 100,
        "score": 50,
        "slowingFactor": 0.7,
        "breakSound": pygame.mixer.Sound("./sound/glass-break.wav"),
        "hitSound": pygame.mixer.Sound("./sound/glass-hit.wav"),
        "shape": {
            "type": "poly",
            "points": [(1,0),(0,1),(1,1)]
        }
    },
    "metal": {
        "bodyType": "dynamic",
        "size": (20,100),
        "image": pygame.image.load("./img/metal.png").convert_alpha(),
        "broken": pygame.image.load("./img/metal-broken.png").convert_alpha(),
        "particle": pygame.image.load("./img/metal-particle.png").convert_alpha(),
        "mass": 8,
        "durability": 8,
        "color": "#e19e69",
        "breakVelocity": 150,
        "score": 100,
        "slowingFactor": 0.55,
        "breakSound": pygame.mixer.Sound("./sound/metal-break.wav"),
        "hitSound": pygame.mixer.Sound("./sound/metal-hit.wav"),
        "shape": {
            "type": "box"
        }
    },
    "metal-square": {
        "bodyType": "dynamic",
        "size": (50,50),
        "image": pygame.image.load("./img/metal-square.png").convert_alpha(),
        "broken": pygame.image.load("./img/metal-square-broken.png").convert_alpha(),
        "particle": pygame.image.load("./img/metal-particle.png").convert_alpha(),
        "mass": 8,
        "durability": 8,
        "color": "#e19e69",
        "breakVelocity": 150,
        "score": 100,
        "slowingFactor": 0.55,
        "breakSound": pygame.mixer.Sound("./sound/metal-break.wav"),
        "hitSound": pygame.mixer.Sound("./sound/metal-hit.wav"),
        "shape": {
            "type": "box"
        }
    },
    "metal-tri": {
        "bodyType": "dynamic",
        "size": (50,50),
        "image": pygame.image.load("./img/metal-tri.png").convert_alpha(),
        "broken": pygame.image.load("./img/metal-tri-broken.png").convert_alpha(),
        "particle": pygame.image.load("./img/metal-particle.png").convert_alpha(),
        "mass": 8,
        "durability": 8,
        "color": "#e19e69",
        "breakVelocity": 150,
        "score": 100,
        "slowingFactor": 0.55,
        "breakSound": pygame.mixer.Sound("./sound/metal-break.wav"),
        "hitSound": pygame.mixer.Sound("./sound/metal-hit.wav"),
        "shape": {
            "type": "poly",
            "points": [(1,0),(0,1),(1,1)]
        }
    },
    "platinum": {
        "bodyType": "dynamic",
        "size": (20,100),
        "image": pygame.image.load("./img/platinum.png").convert_alpha(),
        "broken": pygame.image.load("./img/platinum-broken.png").convert_alpha(),
        "particle": pygame.image.load("./img/platinum-particle.png").convert_alpha(),
        "mass": 12,
        "durability": 11,
        "color": "#909090",
        "breakVelocity": 200,
        "score": 200,
        "slowingFactor": 0.5,
        "breakSound": pygame.mixer.Sound("./sound/platinum-break.wav"),
        "hitSound": pygame.mixer.Sound("./sound/platinum-hit.wav"),
        "shape": {
            "type": "box"
        }
    },
    "platinum-square": {
        "bodyType": "dynamic",
        "size": (50,50),
        "image": pygame.image.load("./img/platinum-square.png").convert_alpha(),
        "broken": pygame.image.load("./img/platinum-square-broken.png").convert_alpha(),
        "particle": pygame.image.load("./img/platinum-particle.png").convert_alpha(),
        "mass": 12,
        "durability": 11,
        "color": "#909090",
        "breakVelocity": 200,
        "score": 200,
        "slowingFactor": 0.5,
        "breakSound": pygame.mixer.Sound("./sound/platinum-break.wav"),
        "hitSound": pygame.mixer.Sound("./sound/platinum-hit.wav"),
        "shape": {
            "type": "box"
        }
    },
    "platinum-tri": {
        "bodyType": "dynamic",
        "size": (50,50),
        "image": pygame.image.load("./img/platinum-tri.png").convert_alpha(),
        "broken": pygame.image.load("./img/platinum-tri-broken.png").convert_alpha(),
        "particle": pygame.image.load("./img/platinum-particle.png").convert_alpha(),
        "mass": 12,
        "durability": 11,
        "color": "#909090",
        "breakVelocity": 200,
        "score": 200,
        "slowingFactor": 0.5,
        "breakSound": pygame.mixer.Sound("./sound/platinum-break.wav"),
        "hitSound": pygame.mixer.Sound("./sound/platinum-hit.wav"),
        "shape": {
            "type": "poly",
            "points": [(1,0),(0,1),(1,1)]
        }
    },
    "tnt": {
        "bodyType": "dynamic",
        "size": (48,48),
        "image": pygame.image.load("./img/tnt.png").convert_alpha(),
        "broken": pygame.image.load("./img/tnt.png").convert_alpha(),
        "particle": pygame.image.load("./img/explode-particle.png").convert_alpha(),
        "mass": 12,
        "durability": 1,
        "color": "#909090",
        "breakVelocity": 200,
        "score": 50,
        "breakSound": pygame.mixer.Sound("./sound/platinum-break.wav"),
        "hitSound": pygame.mixer.Sound("./sound/platinum-hit.wav"),
        "shape": {
            "type": "box"
        }
    },
    "wall": {
        "bodyType": "static",
        "size": (50,50),
        "image": pygame.image.load("./img/wall.png").convert_alpha(),
        "broken": pygame.image.load("./img/stone-broken.png").convert_alpha(),
        "mass": 1,
        "durability": 1,
        "color": "#909090",
        "breakVelocity": 1,
        "score": 0,
        "shape": {
            "type": "box"
        }
    },
    "triWall": {
        "bodyType": "static",
        "size": (50,50),
        "image": pygame.image.load("./img/tri-wall.png").convert_alpha(),
        "broken": pygame.image.load("./img/stone-broken.png").convert_alpha(),
        "mass": 1,
        "durability": 1,
        "color": "#909090",
        "breakVelocity": 1,
        "score": 0,
        "shape": {
            "type": "poly",
            "points": [(1,0),(0,1),(1,1)]
        }
    }
}
enemyTemplates = {
    "base": {
        "size": (40,40),
        "image": pygame.image.load("./img/impostor.png").convert_alpha(),
        "health": 5,
        "score": 200
    },
    "armored": {
        "size": (50,50),
        "image": pygame.image.load("./img/armored-impostor.png").convert_alpha(),
        "health": 15,
        "score": 250
    },
    "robot": {
        "size": (60,60),
        "image": pygame.image.load("./img/robot-impostor.png").convert_alpha(),
        "health": 20,
        "score": 300
    },
    "boss": {
        "size": (80,100),
        "image": pygame.image.load("./img/boss-impostor.png").convert_alpha(),
        "health": 30,
        "score": 500
    }
}

tutorialDict = {
    "4": pygame.image.load("./img/tut-4.png"),
    "8": pygame.image.load("./img/tut-8.png"),
    "12": pygame.image.load("./img/tut-12.png"),
    "16": pygame.image.load("./img/tut-16.png")
}

launchSound = pygame.mixer.Sound("./sound/launch.mp3")
birdDieSound = pygame.mixer.Sound("./sound/poof.wav")
explodeSound = pygame.mixer.Sound("./sound/explode.wav")
hitSound = pygame.mixer.Sound("./sound/hit.wav")
zoomSound = pygame.mixer.Sound("./sound/zoom.wav")
yellowInflateSound = pygame.mixer.Sound("./sound/yellow-inflate.wav")
yellowPopSound = pygame.mixer.Sound("./sound/yellow-pop.wav")
throwSound = pygame.mixer.Sound("./sound/throw.mp3")
remoteSound = pygame.mixer.Sound("./sound/remote.wav")
clickSound = pygame.mixer.Sound("./sound/click.mp3")
scoreSound = pygame.mixer.Sound("./sound/score-up.wav")
stretchSound = pygame.mixer.Sound("./sound/stretch.wav")
starSounds = [pygame.mixer.Sound(f"./sound/star-{i+1}.wav") for i in range(3)]
loseSound = pygame.mixer.Sound("./sound/lose.wav")

class Level():
    def __init__(self,size):
        global mainBall, gameObjects
        self.size = size
        self.extraScore = 0
        self.birds = []
        self.enemies = []
        self.blocks = []

        self.otherObjects = []

        self.state = 0

        


    def calculateTotalScore(self):
        totalScore = sum([enemy.enemy["score"] for enemy in self.enemies]) + sum([block.block["score"] for block in self.blocks]) - self.extraScore
        return totalScore

class Camera():
    def __init__(self,levelSize,speed=10):
        self.position = [0,levelSize[1]-screen_height]
        self.zoom = 1
        self.levelSize = levelSize
        self.velocity = [0,0]
        self.acceleration = [0,0]

    def moveCam(self,dir):
        self.acceleration = dir

    def update(self):
        self.velocity = add(self.velocity,self.acceleration)
        self.position = add(self.position,self.velocity)
        self.position[0] = max(min(self.position[0],self.levelSize[0]-screen_width/self.zoom),0)
        self.position[1] = max(min(self.position[1],self.levelSize[1]-screen_height/self.zoom),0)

        # print(self.position[0],self.levelSize[0]-screen_width/self.zoom)
        if self.position[0] == 0 or self.position[0] == self.levelSize[0]-screen_width/self.zoom:
            self.velocity[0] = 0
            self.acceleration[0] = 0
            # print("well")

        if self.position[1] == 0 or self.position[1] == self.levelSize[1]-screen_height/self.zoom:
            self.velocity[1] = 0
            self.acceleration[1] = 0

        # print(self.acceleration,self.velocity)



    def getPos(self):
        if self.zoom==1:
            return self.position
        center = add(self.position,(screen_width/2,screen_height/2))
        newCenter = mult(center,cam.zoom)

        return mult(subtr(newCenter,(screen_width/2,screen_height/2)),1/cam.zoom)
    
    def setZoom(self,dir):
        step = dir * 0.5
        self.zoom += step
        self.zoom = max(min(self.zoom,4),0.5)

class GameObject():
    def __init__(self,position,size,angle=0,color=None,image=None,imageArea=None,layer=0,opacity=255):
        global gameObjects
        self.position = position
        self.size = size
        self.angle = angle
        self.color = color
        self.image = pygame.transform.scale(image,size) if image else None
        self.imageArea = imageArea
        self.layer = layer
        self.opacity = opacity
        self.alive = True
        self.visible = True

        self.nextUpdateFunction = None

        addGameObject(self)


    def draw(self):
        if not self.visible:
            return
        
        if self.image:
            # scale = pygame.transform.scale(self.image,mult(self.size,cam.zoom)) if cam.zoom != 1 else self.image
            if self.opacity != 255:
                self.image.set_alpha(self.opacity)

            rot = pygame.transform.rotate(self.image,-deg(self.angle))
            pos = mult(subtr(self.position,cam.getPos()),cam.zoom)
            new_rect = rot.get_rect(center = self.image.get_rect(center = pos).center)
            screen.blit(rot,new_rect,area=self.imageArea)

            if self.opacity != 255:
                self.image.set_alpha(255)


        elif self.color:
            pos = mult(subtr(subtr(self.position,mult(self.size,1/2)),cam.getPos()),cam.zoom)
            pygame.draw.rect(screen,self.color,(pos[0],pos[1],self.size[0]*cam.zoom,self.size[1]*cam.zoom))

    def update(self):
        if not self.alive:
            gameObjects.remove(self)

class Text(GameObject):
    def __init__(self, position, text, fontSize=20, color="white",font=labelFont,layer=0, centered=True):
        self.text = text
        self.fontSize = fontSize
        self.font = font
        self.centered = centered
        self.fontObject = pygame.font.SysFont(font,fontSize)
        super().__init__(position, size=[0,0], angle=0, color=color, image=None,layer=layer)

    def draw(self):
        drawText(self.text,self.color,self.fontObject,pos=self.position if not self.centered else None,center=self.position if self.centered else None)

class FloatingScoreLabel(Text):
    def __init__(self, position, text, fontSize=20, color="white", font=labelFont, layer=0):
        self.opacity = 255
        self.delta = 0
        self.fontObject = pygame.font.SysFont(font,fontSize)
        super().__init__(position, text, fontSize, color, font, layer)

    def update(self):
        self.delta += 1
        self.position[1] -= 1
        if self.delta > 10:
            self.opacity *= 0.95
        if self.opacity < 10:
            gameObjects.remove(self)

    def draw(self):
        pos = subtr(self.position,cam.getPos())
        drawText(self.text,"black",self.fontObject,center=add(pos,[2,2]),opacity=self.opacity)
        drawText(self.text,self.color,self.fontObject,center=pos,opacity=self.opacity)

class PhysicsGameObject(GameObject):
    def __init__(self, position, size, angle=0, color=None, image=None):
        super().__init__(position, size, angle, color, image)

    def draw(self):
        self.position = self.body.position
        self.angle = self.body.angle
        super().draw()

    def update(self):
        if not self.alive:
            gameObjects.remove(self)
            space.remove(self.shape,self.body)

class Ball(PhysicsGameObject):
    def __init__(self,position,birdKey):
        

        self.birdKey = birdKey
        self.bird = birdTemplates[birdKey]
        self.image = self.bird["image"]
        self.particle = pygame.image.load(f"img/{birdKey}-particle.png").convert_alpha()
        super().__init__(position,self.bird["imageSize"],angle=0,image=self.bird["image"])

        inertia = pymunk.moment_for_circle(1, 0, self.size[0]/2, (0, 0))
        self.body = pymunk.Body(1,inertia,body_type=pymunk.Body.DYNAMIC)
        self.body.position = position
        self.shape = pymunk.Circle(self.body,self.bird["size"][0]/2)
        self.shape.elasticity = 0
        self.shape.friction = 0.1
        self.shape.filter = pymunk.ShapeFilter(categories=collisionMasks[2][0],mask=collisionMasks[2][1])
        space.add(self.body,self.shape)

        self.shape.id = random.randint(0,9999)

        self.shot = False
        self.hit = False
        self.active = True
        self.clicked = False

    def draw(self):
        if self.active:
            super().draw()

    def update(self):
        if self.nextUpdateFunction:
            self.nextUpdateFunction()
            self.nextUpdateFunction = None
        super().update()

    def destroy(self):
        playSound(birdDieSound)
        self.active = False
        self.alive = False
        Particles(self.body.position,self.size,image=self.particle,angle=self.body.angle,gravity=0,particleSize=[15,15],sizeRandomness=0.2)

class EnemyBall(PhysicsGameObject):
    def __init__(self, position, enemyKey):


        self.enemyKey = enemyKey
        self.enemy = enemyTemplates[enemyKey]
        self.image = self.enemy["image"]
        super().__init__(position,self.enemy["size"],angle=0,image=self.enemy["image"])

        inertia = pymunk.moment_for_circle(1, 0, self.size[0]/2, (0, 0))
        self.body = pymunk.Body(1,inertia,body_type=pymunk.Body.DYNAMIC)
        self.body.position = position
        self.shape = pymunk.Circle(self.body,self.size[0]/2)
        self.shape.elasticity = 0
        self.shape.friction = 0.1
        space.add(self.body,self.shape)

        self.shape.id = random.randint(0,9999)


        self.shape.filter = pymunk.ShapeFilter(categories=collisionMasks[4][0],mask=collisionMasks[4][1])
        self.readyToBreak = False
        self.breakVelocity = 200
        self.health = self.enemy["health"]

    def update(self):
        if not self.alive:
            gameObjects.remove(self)
            level.enemies.remove(self)
            space.remove(self.shape, self.body)

            return

        if mag(self.body.velocity) > self.breakVelocity:
                self.readyToBreak = True
        if self.readyToBreak and (self.body.velocity.y < 10):
            self.destroy()

    def destroy(self):

        addToScore(self.enemy["score"],subtr(self.position,[0,50]))
        playSound(birdDieSound)
        self.alive = False
        Particles(self.body.position,self.size,color="black",angle=self.body.angle)

        aliveEnemies = [e for e in level.enemies if e.alive]
        if not len(aliveEnemies):
            GameTimer(2,endLevel,[True])

    def damage(self,velocity):
        self.health -= velocity/100
        if self.health <= 0:
            self.destroy()

class Wall(PhysicsGameObject):
    def __init__(self,position,size):
        super().__init__(position,size,angle=0,color="dimgrey")
        self.body = pymunk.Body(1,100,body_type=pymunk.Body.STATIC)
        self.body.position = position
        self.shape = pymunk.Poly.create_box(self.body,self.size)
        self.shape.elasticity = 1
        self.shape.friction = 1
        self.shape.filter = pymunk.ShapeFilter(categories=collisionMasks[1][0],mask=collisionMasks[1][1])

        space.add(self.body,self.shape)

    def draw(self):
        pass
    # def draw(self):
    #     pos = mult(subtr(subtr(self.body.position,mult(self.size,1/2)),cam.getPos()),cam.zoom)
    #     pygame.draw.rect(screen,"dimgray",(pos[0],pos[1],self.size[0]*cam.zoom,self.size[1]*cam.zoom))

class Block(PhysicsGameObject):
    def __init__(self,position,blockKey,angle=0,elast=0):
        self.blockKey = blockKey
        self.block = blockTemplates[blockKey]
        super().__init__(position,add(self.block["size"],[2,2]),angle,image=self.block["image"])
        self.body = pymunk.Body(1,1,body_type=(pymunk.Body.DYNAMIC if self.block["bodyType"]=="dynamic" else pymunk.Body.STATIC))
        self.body.position = position
        self.body.angle = rad(angle)
        
        if self.block["shape"]["type"]=="box":
            self.shape = pymunk.Poly.create_box(self.body,self.block["size"])
        elif self.block["shape"]["type"]=="poly":
            self.shape = pymunk.Poly(self.body,[(v[0]*self.block["size"][0]-self.block["size"][0]/2,v[1]*self.block["size"][1]-self.block["size"][1]/2) for v in self.block["shape"]["points"]])


        self.shape.mass = self.block["mass"]
        self.shape.elasticity = 0.3
        self.shape.friction = 1
        category = 3 if self.block["bodyType"]=="dynamic" else 1
        self.shape.filter = pymunk.ShapeFilter(categories=collisionMasks[category][0],mask=collisionMasks[category][1])
        space.add(self.body,self.shape)

        self.readyToBreak = False
        self.breakVelocity = self.block["breakVelocity"]
        self.durability = self.block["durability"]
        self.broken = False

        self.shape.id = random.randint(0,9999)
        level.blocks.append(self)


    def draw(self):
        self.position = self.body.position
        self.angle = self.body.angle
        super().draw()
    

    def update(self):
        if self.nextUpdateFunction:
            self.nextUpdateFunction()
            self.nextUpdateFunction = None

        if not self.alive:
            gameObjects.remove(self)
            level.blocks.remove(self)
            space.remove(self.shape, self.body)
            return

        if self.block["bodyType"]=="dynamic":
            if mag(self.body.velocity) > self.breakVelocity:
                self.readyToBreak = True
            if self.blockKey=="tnt":
                if self.readyToBreak and mag(self.body.velocity) < self.breakVelocity/2:
                    self.destroy()
            else:
                if self.readyToBreak and mag(self.body.velocity) < 10:
                    playSound(self.block["hitSound"])
                    self.damage(mag(self.body.velocity)*self.breakVelocity/2)
                    self.readyToBreak = False

    def destroy(self):

        addToScore(self.block["score"],subtr(self.position,[0,50]))

        if self.block.get("breakSound",None):
            playSound(self.block["breakSound"])   

        if self.blockKey=="tnt":

            # def setExplodeFunc(self):
            #     self.nextUpdateFunction = self.explode
            # GameTimer(0.05,setExplodeFunc,[self])
            self.alive = False
            self.nextUpdateFunction = self.explode
            Particles(self.body.position,mult(self.size,1.2),color=self.color,image=self.block["particle"],angle=self.body.angle,amount=100,particleSize=[30,30],sizeRandomness=0.5,gravity=0,velocity=10,decay=0.1)

        else:
            Particles(self.body.position,self.size,color=self.color,image=self.block["particle"],angle=self.body.angle)
            self.alive = False

    def explode(self):

        playSound(explodeSound)

        for enemy in level.enemies:
            if enemy.alive:
                if mag(subtr(self.body.position,enemy.body.position)) <= 150:
                    enemy.destroy()

        for block in level.blocks:
            if block.alive:
                if block != self and mag(subtr(self.body.position,block.body.position)) <= 200:
                    impulse = subtr(self.body.position,block.body.position)
                    distance = mag(impulse)
                    u = unit(impulse)
                    m = 8500
                    f = m + (-m/(250-50))*(distance-50 if distance >= 50 else 0)

                    if block.block["bodyType"]=="dynamic":
                        block.damage(f/8)

                    block.body.apply_impulse_at_world_point(mult(u,-f),block.body.position)

        for ball in level.balls:
             if ball.active and ball.shot:
                if mag(subtr(self.body.position,ball.body.position)) <= 200:
                    impulse = subtr(self.body.position,ball.body.position)
                    # impulse[1] *= -1
                    distance = mag(impulse)
                    u = unit(impulse)
                    m = 500
                    # f = m + (-m/(250-50))*(distance-50 if distance >= 50 else 0)
                    ball.body.apply_impulse_at_world_point(mult(u,-m),ball.body.position)

        self.alive = False

    def damage(self,velocity):
        self.durability -= velocity/(self.breakVelocity/2)
        if not self.broken:
            if self.durability < self.block["mass"]/2:
                self.image = pygame.transform.scale(self.block["broken"],add(self.size,[2,2]))
                self.broken = True

        if self.durability <= 0:
            self.destroy()

class GameTimer():
    def __init__(self,seconds,function,args=[]):
        global gameTimers

        def timerFunction():
            function(*args)
            gameTimers.remove(self.timer)

        self.timer = Timer(seconds,timerFunction)
        self.timer.daemon = True
        self.timer.start()
        gameTimers.append(self.timer)

    def cancel(self):
        self.timer.cancel()

class Particles(GameObject):
    def __init__(self,position,size,color="white",image=None,angle=0,particleSize=[10,10],sizeRandomness=0,gravity=0.3,
                 amount=20, velocity=3, decay = 0.05,layer=0):
        self.amount = amount
        self.position = position
        self.color = color
        self.image = image
        self.angle = angle
        self.acceleration = gravity
        self.decay = decay
        self.layer = layer
        self.alive = True
        self.particles = [
            {
            "pos":[random.random()*size[0],random.random()*size[1]],
            "size": mult(particleSize,(1-sizeRandomness)+random.random()*2*sizeRandomness),
            "vel": mult([-1 + random.random()*2,-1 + random.random()*2],velocity)
            } for i in range(self.amount)
        ]

        mm = rotationMatrix(angle)
        self.size = multMtrx(mm,size)

        for p in self.particles:
            p["pos"] = multMtrx(mm,p["pos"])

        addGameObject(self)

    def draw(self):
        for p in self.particles:
            
            pos = subtr(subtr(add(self.position,p["pos"]),mult(self.size,1/2)),cam.getPos())
            pos = subtr(pos,mult(p["size"],1/2))

            if self.image:
                screen.blit(pygame.transform.scale(self.image,p["size"]),pos)
            else:
                pygame.draw.rect(screen,self.color,(pos[0],pos[1],p["size"][0],p["size"][1]))

            p["pos"] = add(p["pos"],p["vel"])
            if self.acceleration:
                p["vel"][1] += self.acceleration

            if p["size"][0] > 0.5:
                p["size"] = mult(p["size"],(1-self.decay))
            else:
                self.alive = False

class TrailLine(GameObject):
    def __init__(self, position=[0,0], size=[0,0], angle=0, color=None, image=None):
        super().__init__(position, size, angle, color, image)
        self.points = []
        self.pointSize = [8,8]

    def addPoint(self,point):
        self.points.append(point)

    def draw(self):
        for p in self.points:
            pos = mult(subtr(subtr(p,mult(self.pointSize,1/2)),cam.getPos()),cam.zoom)
            pygame.draw.rect(screen,"white",(pos[0],pos[1],self.pointSize[0]*cam.zoom,self.pointSize[0]*cam.zoom),border_radius=int(self.pointSize[0]/2))

class Marker(GameObject):
    def __init__(self,position):
        self.mainImage = pygame.image.load("./img/marker.png").convert_alpha()
        super().__init__(position, size=[100,100], angle=0, image=self.mainImage, layer=2, opacity=255)

    def update(self):
        super().update()
        self.opacity -= 10
        self.angle += 0.05
        self.image = pygame.transform.scale(self.mainImage,subtr(self.size,[self.angle*10,self.angle*10]))
        if self.opacity <= 0:
            self.alive = False
        
class FloatingMenuSprite(GameObject):
    def __init__(self, position, size, angle=0, color=None, image=None, imageArea=None, velocity=[0,0], angularVelocity=0, layer=0):
        super().__init__(position, size, angle, color, image, imageArea, layer)
        self.velocity = velocity
        self.angularVelocity = rad(angularVelocity)

    def update(self):
        global dt
        self.position = add(self.position,mult(self.velocity,dt*3/4))
        self.angle += self.angularVelocity*dt*3/4
        if self.position[0] >= screen_width+self.size[0]/2 or self.position[1] >= screen_height+self.size[1]/2:
            gameObjects.remove(self)

class MovingBackground(GameObject):
    def __init__(self, position, size, angle=0, color=None, image=None, imageArea=None, layer=0):
        super().__init__(position, size, angle, color, image, imageArea, layer)

    def update(self):
        if self.position[0] >= self.size[0]/2:
            self.position = [0,self.position[1]]
        self.position = add(self.position,[2,0])

class WinStars():
    def __init__(self,position,size,maxStars):
        self.position = position
        self.size = size
        a = [-1,0,1]
        self.images = [pygame.image.load(f"./img/star-{i+1}.png").convert_alpha() for i in range(3)]
        self.stars = [GameObject(add(position,[(175)*a[i],size[1]/2]),self.size,image=self.images[i],layer=2,opacity=0) for i in range(3)]
        self.count = 0
        self.currentStar = 0
        # playSound(starSounds[0])
        def updateEmpty():
            pass


        def updateStar(stars,self):
            if stars.currentStar < maxStars:
                if self == stars.stars[stars.currentStar] and not stars.count:
                    if self.opacity < 255:
                        self.opacity += 255/25
                        m = (1-1.5)/255
                        f = (m*self.opacity+1.5)
                        newSize = mult(stars.size,f)
                        self.image = pygame.transform.scale(stars.images[stars.currentStar],newSize)
                    else:
                        # star.opacity = 255
                        playSound(starSounds[stars.currentStar])
                        stars.currentStar += 1
                        stars.count = 400
                        # self.update = updateEmpty

            if stars.count:
                stars.count -= 5
                
        for star in self.stars:
            star.update = lambda x=star: updateStar(self,x)

class Button():
    def __init__(self, position, size, color=None, text=None, image=None, function=None):
        self.position = position
        self.size = size
        self.color = color
        self.image = pygame.transform.scale(image,size)
        self.function = function
        self.text = text
        self.rect = pygame.Rect(position,size)
        if text:
            self.fontObject = pygame.font.SysFont(text.get("font","calibri"),text["fontSize"])

    def draw(self):
        if self.image:
            screen.blit(self.image,self.position)
        elif self.color:
            pygame.draw.rect(screen,self.color,(self.position[0],self.position[1],self.size[0],self.size[1]))
        
        if self.text:
            drawText(self.text["text"],self.text["color"],self.fontObject,(self.position[0]+self.size[0]/2,self.position[1]+self.size[1]/2))

    def checkEvent(self):
        global mouse
        if self.function:
            if self.rect.collidepoint(mouse):
                self.function()

class Arrow(GameObject):
    def __init__(self):
        super().__init__((screen_width-100,screen_height/2), (100,100), image=pygame.image.load("./img/arrow.png").convert_alpha(),layer=2)

    def draw(self):
        enemyOutside = False
        for enemy in level.enemies:
            if enemy.alive:
                if enemy.position[0] - enemy.size[0]/2 > cam.getPos()[0]+screen_width:
                    enemyOutside = True
                    break
        
        if enemyOutside:
            super().draw()

def rotationMatrix(angle):
    return [[math.cos(angle),-math.sin(angle)],[math.sin(angle),math.cos(angle)]]
def deg(rad):
    return rad / math.pi * 180
def rad(deg):
    return deg * math.pi / 180
def add(a,b):
    return [a[0]+b[0],a[1]+b[1]]
def subtr(a,b):
    return [a[0]-b[0],a[1]-b[1]]
def mag(a):
    return math.sqrt(a[0]**2+a[1]**2)
def mult(a,x):
    return [a[0]*x,a[1]*x]
def unit(a):
    m = mag(a)
    if not m:
        return [0,0]
    return [a[0]/m,a[1]/m]
def dot(a,b):
    return a[0]*b[0] + a[1]*b[1]
def multMtrx(a,b):
    result = [0,0]
    result[0] = a[0][0]*b[0] + a[0][1]*b[1]
    result[1] = a[1][0]*b[0] + a[1][1]*b[1]
    return result
def normal(a):
    return unit([-a[1],a[0]])

def addGameObject(gameObject):
    global gameObjects
    layer = gameObject.layer
    if not len(gameObjects):
        gameObjects.insert(0,gameObject)
        return
    elif layer <= gameObjects[0].layer:
        gameObjects.insert(0,gameObject)
        return
    elif layer >= gameObjects[-1].layer:
        gameObjects.insert(len(gameObjects),gameObject)
        return
    
    i = math.ceil(len(gameObjects)/2)
    l = i

    while True:
        if i+1<len(gameObjects):
            if gameObjects[i+1].layer >= layer and gameObjects[i].layer <= layer:
                break
        
        if gameObjects[i].layer >= layer:
            i -= math.ceil(l/2)
        else:
            i += math.ceil(l/2)
        l = math.floor(l/2)

    gameObjects.insert(i+1,gameObject)

def playSound(sound,volume=1,looped=False):
        sound.set_volume(volume)
        sound.play(-1 if looped else 0)
        # sound.set_volume(1)

def stopSound(sound,fadeout=0):
    if fadeout:
        sound.fadeout(fadeout)
    else:
        sound.stop()

def drawText(text,color,fontObject,center=(),pos=(),opacity=255):
    # font = pygame.font.SysFont(font,size)
    text = fontObject.render(text,True,color)
    textRect = text.get_rect()
    if center:
        textRect.center = center
    if pos:
        textRect.topleft = pos
    if opacity != 255:
        text.set_alpha(opacity)
    screen.blit(text,textRect)
    if opacity != 255:
        text.set_alpha(255)

def ballReady():
    global mainBall, currentBallIndex, readyToAim, nextAnimation, animationStartPos, ballTimer
    ballTimer = None
    if currentBallIndex < len(level.balls):
        mainBall = level.balls[-1-currentBallIndex]
        if currentBallIndex > 0:
            nextAnimation = True
            animationStartPos = mainBall.body.position
        else:
            mainBall.body.position = slingShotPos
            mainBall.body.sleep()
        currentBallIndex += 1
    else:
        mainBall = None
        GameTimer(5,endLevel,[not len(level.enemies)])

def getCollisionData(arbiter,space,data):
    
    global ballTimer
    pair = sorted([shape for shape in arbiter.shapes],key=lambda s: s.filter.categories)
    pairGroups = [pair[0].filter.categories,pair[1].filter.categories]
    # if first shape is bird
    if pairGroups[0]==collisionMasks[0][0]:
        bird = list(filter(lambda s: s.shape.id==pair[0].id,level.balls))[0]

        playSound(hitSound,mag(bird.body.velocity)/500)
        if bird == mainBall:
            if mainBall.shot and ballTimer == None:
                mainBall.hit = True
                ballTimer = GameTimer(1.5,ballReady)
                GameTimer(5,mainBall.destroy)
                

        if pairGroups[1] == collisionMasks[4][0]:
            enemy = list(filter(lambda s: s.shape.id==pair[1].id,level.enemies))[0]
            velocity = mag(bird.body.velocity)
            enemy.damage(velocity)
        
        elif pairGroups[1] == collisionMasks[3][0]:
            block = list(filter(lambda s: s.shape.id==pair[1].id,level.blocks))[0]
            velocity = mag(bird.body.velocity)
            if velocity > 600:
                if block.block["bodyType"]=="dynamic":
                    block.damage(velocity)
            
            if block.blockKey != "tnt" and velocity > 200:
                n = arbiter.contact_point_set.normal
                v = bird.body.velocity
                angle = math.acos(dot(n,v)/(mag(n)*mag(v)))
                
                if angle < 35:
                    def setVelocity(vel):
                        bird.body.velocity = vel
                    
                    GameTimer(0.01,setVelocity,[mult(bird.body.velocity,blockTemplates[block.blockKey].get("slowingFactor",0.5))])

    elif pairGroups[1]==collisionMasks[5][0]:
        object = list(filter(lambda s: s.shape.id==pair[1].id,level.otherObjects))[0]

        playSound(hitSound,mag(object.body.velocity)/500)

        if pairGroups[0] == collisionMasks[3][0]:
            block = list(filter(lambda s: s.shape.id==pair[0].id,level.blocks))[0]
            velocity = mag(object.body.velocity)
            if velocity > 600:
                if block.block["bodyType"]=="dynamic":
                    block.damage(velocity)
            

    return True

handler = space.add_default_collision_handler()
handler.begin = getCollisionData


def cyanBird(self):
    newVelocity = mult(unit(subtr(add(mouse,cam.getPos()),self.body.position)),1500)
    if newVelocity[0] < 0:
        self.image = pygame.transform.flip(self.image,1,0)
    self.body.velocity = newVelocity
    playSound(zoomSound)


def yellowBird(self):
    oldShape = self.shape
    oldSize = self.size
    oldImage = self.image

    self.size = [250,200]
    self.image = pygame.transform.scale(pygame.image.load("./img/inflated-yellow-amogus.png").convert_alpha(),self.size)
    space.remove(self.shape,self.body)
    

    self.shape = pymunk.Circle(self.body,self.size[1]/2)
    self.shape.elasticity = oldShape.elasticity
    self.shape.friction = oldShape.friction
    self.shape.filter = oldShape.filter
    space.add(self.body,self.shape)
    self.shape.id = oldShape.id


    self.body.mass = 10
    self.body.inertia = pymunk.moment_for_circle(1, 0, self.size[0]/2, (0, 0))

    for block in level.blocks:
        if block.alive:
            if mag(subtr(self.body.position,block.body.position)) <= 180:
                impulse = subtr(self.body.position,block.body.position)
                # impulse[1] *= -1
                distance = mag(impulse)
                u = unit(impulse)
                m = 8500
                f = m + (-m/(200-50))*(distance-50 if distance >= 50 else 0)

                if block.block["bodyType"]=="dynamic":
                    block.damage(f/10)

                block.body.apply_impulse_at_world_point(mult(u,-f),block.body.position)

    def revertYellow():
        space.remove(self.shape,self.body)
        self.shape = oldShape
        self.size = oldSize
        self.image = oldImage
        space.add(self.body,self.shape)
        playSound(yellowPopSound)

    playSound(yellowInflateSound)

    def setFunction():
        self.nextUpdateFunction = revertYellow    

    GameTimer(2,setFunction)


def blueBird(self):
    p = PhysicsGameObject(self.body.position,[20,20],0,image=pygame.image.load("./img/throw-ball.png").convert_alpha())

    inertia = pymunk.moment_for_circle(1, 0, p.size[0]/2, (0, 0))
    p.body = pymunk.Body(1,inertia,body_type=pymunk.Body.DYNAMIC)
    p.body.position = p.position
    m = add(mouse,cam.getPos())
    p.body.velocity = mult(unit(subtr(m,self.body.position)),1200)
    p.body.mass = 5
    p.shape = pymunk.Circle(p.body,p.size[0]/2)
    p.shape.elasticity = 0
    p.shape.friction = 0.1
    p.shape.filter = pymunk.ShapeFilter(categories=collisionMasks[5][0],mask=collisionMasks[5][1])
    space.add(p.body,p.shape)
    p.shape.id = random.randint(0,9999)

    level.otherObjects.append(p)

    playSound(throwSound)

def greenBird(self):
    tnt = Block([self.body.position.x,blockTemplates["tnt"]["size"][1]/2],"tnt")
    oldSize = self.size
    oldImage = self.image
    self.size = [60,52]
    self.image = pygame.transform.scale(pygame.image.load("./img/green-amogus-activate.png").convert_alpha(),self.size)

    def revertGreen():
        self.size = oldSize
        self.image = oldImage
    GameTimer(1,revertGreen)
    playSound(remoteSound)


def endLevel(win):
    global winScreenScoreLabel

    def addFloatingLabel(pos,birdKey):
        # print("here it is")
        FloatingScoreLabel(pos,f"{300}+",40,color=birdKey)
        addToScore(300)

    def winLevel():
        global winScreenScoreLabel, currentLevelPassed, levelMenuButtons, levelMenuButtonSurface, saveData
        if currentLevelPassed == currentLevelIndex:
            currentLevelPassed += 1
        addLevelMenuButtons()

        GameObject(add(pos,cam.getPos()),(500,580),image=pygame.image.load("./img/panel.png").convert_alpha(),layer=2)
        winScreenScoreLabel = Text(add(pos,[0,30]),"0",fontSize=50,layer=2)
        scorePercent = score/level.totalScore
        starCount = 3 if scorePercent >= 0.75 else 2 if scorePercent >= 0.5 else 1
        starObject = WinStars(add(subtr(pos,(0,240)),cam.getPos()),(180,180),starCount)
        playSound(scoreSound,looped=True)

        with open("save.json") as save:
            saveData = json.load(save)
            if starCount > saveData["levelStars"].get(f"{currentLevelIndex}",0):
                saveData["levelStars"][f"{currentLevelIndex}"] = starCount
            if saveData["currentLevel"] == currentLevelIndex:
                saveData["currentLevel"] = currentLevelIndex+1
        with open("save.json","w") as save:
            json.dump(saveData, save)



    if not level.state:
        if canWin:
            pos = (screen_width/2,screen_height/2)
            if win:
                level.state = 1
                remainingBalls = list(reversed([ball for ball in level.balls if ball.active and not ball.shot]))
                for i,ball in enumerate(remainingBalls):
                    GameTimer(i+1,addFloatingLabel,[subtr(ball.body.position,[0,50]),ball.birdKey])
                GameTimer(len(remainingBalls)+1,winLevel)


            else:
                GameObject(add(pos,cam.getPos()),(500,650),image=pygame.image.load("./img/panel.png").convert_alpha(),layer=2)
                GameObject(add(subtr(pos,[0,50]),cam.getPos()),(500,500),image=pygame.image.load("./img/lose.png").convert_alpha(),layer=2)
                level.state = 2
                playSound(loseSound)


def startNextLevel():
    global currentLevelIndex
    currentLevelIndex += 1
    startLevel(currentLevelIndex)


def addToScore(x,position=None):
    if position:
        scorePopup = FloatingScoreLabel(position,f"{x}+",40)
    global score
    score += x

def updateScore():
    scoreLabel.text = f"Score: {score}"


def drawButtons(buttons):
    for button in buttons:
        button.draw()

def handleButtonEvents(buttons,event):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
            for button in buttons:
                button.checkEvent()



endLevelButtons = [
    Button(size=(100,100),position=(screen_width/2-100/2,screen_height-180-100/2),image=pygame.image.load("./img/restart-button.png").convert_alpha(),function=lambda: startLevel(currentLevelIndex)),
    Button(size=(100,100),position=(screen_width/2-150-100/2,screen_height-180-100/2),image=pygame.image.load("./img/menu-button.png").convert_alpha(),function=lambda: backToMenu()),
    Button(size=(100,100),position=(screen_width/2+150-100/2,screen_height-180-100/2),image=pygame.image.load("./img/next-button.png").convert_alpha(),function=lambda: startNextLevel())
    ]


mainMenuButtons = [Button(size=(200,200),position=(screen_width/2-200/2,screen_height/2),image=pygame.image.load("./img/start-button.png").convert_alpha(),function=lambda: chooseMenu("levels"))]

def addLevelMenuButtons():
    global levelMenuButtons, levelMenuButtonSurface
    size = 100
    margin = [50,25]
    levelMenuButtons = []
    startPos = [screen_width/2-(5*(size+margin[0])-margin[0])/2,80]
    for i in range(25):
       levelMenuButtons.append(Button(text={"text":str(i+1),"color":"black","fontSize":30,"font":labelFont},size=(size,size),position=(startPos[0]+(i%5)*(size+margin[0]),startPos[1]+(i//5)*(size+margin[1])),image=pygame.image.load(f"./img/{'' if i < currentLevelPassed+1 else 'disabled-' }button.png").convert_alpha(),function=(lambda x=i: startLevel(x)) if i < currentLevelPassed+1 else None))

    levelMenuButtons.append(Button(text={"text":"","color":"black","fontSize":30,"font":labelFont},size=(size,size),position=(50,screen_height-150),image=pygame.transform.flip(pygame.image.load("./img/start-button.png").convert_alpha(),1,0),function=lambda: chooseMenu("main")))

    levelMenuButtonSurface = pygame.Surface((screen_width,screen_height),pygame.SRCALPHA, 32)

    starRects = [pygame.Rect(0,0,(i)*30,30) for i in range(4)]

    for i,button in enumerate(levelMenuButtons):
        levelMenuButtonSurface.blit(button.image,button.position)
        font = pygame.font.SysFont(button.text["font"],button.text["fontSize"])
        text = font.render(button.text["text"],True,button.text["color"])
        textRect = text.get_rect()
        textRect.center = add(button.position,mult(button.size,1/2))
        levelMenuButtonSurface.blit(text,textRect)

        levelMenuButtonSurface.blit(pygame.transform.scale(threeStarsImage,(90,90/3)),[button.position[0]+5,button.position[1]+70],area=starRects[saveData["levelStars"].get(f"{i}",0)])

def startLevel(levelIndex):
    global level, cam, space, backgroundImage, spaceImage, slingShotPos, spaceImagePos, currentLevelIndex
    global gameObjects, gameTimers, currentBallIndex, mainBall, ballTimer, score, scoreLabel, trailLine, arrow, winScreenScoreLabel, particles
    global readyToAim, nextAnimation, aiming, stretched, animationStartPos, delta, running, tutorialImage
    
    playSound(clickSound)
    stopSound(scoreSound,200)
    for timer in gameTimers:
        timer.cancel() 
    
    space = pymunk.Space()
    space.sleep_time_threshold = 1
    space.gravity = (0, 981)

    handler = space.add_default_collision_handler()
    handler.begin = getCollisionData

    gameObjects = []
    

    level = Level((1440,720))
    cam = Camera(level.size)

    slingShotPos = (400,level.size[1]-220-groundOffset)
    slingShotSize = (225,275)

    blurred = Image.open("./img/background.png").filter(ImageFilter.GaussianBlur(radius=1))
    backgroundSize = [int(blurred.width*(level.size[1]-groundOffset)/blurred.height),int(level.size[1]-groundOffset)]
    backgroundImage = pygame.image.frombytes(blurred.tobytes(), blurred.size, "RGBA")
    backgroundImage = pygame.transform.scale(backgroundImage,backgroundSize).convert_alpha()

    blurred = Image.open("./img/space.png").filter(ImageFilter.GaussianBlur(radius=0))
    spaceImage = pygame.image.frombytes(blurred.tobytes(), blurred.size, "RGBA")
    spaceImage = pygame.transform.scale(spaceImage,(level.size[0]*2,360)).convert_alpha()
    spaceImagePos = 0

    currentBallIndex = 0
    ballTimer = None
    score = 0

    level.walls = [
    Wall((level.size[0]/2,-5),(level.size[0],5)),
    Wall((level.size[0]/2,level.size[1]+5-groundOffset),(level.size[0],5)),
    Wall((-5,level.size[1]/2),(5,level.size[1])),
    Wall((level.size[0]+5,level.size[1]/2),(5,level.size[1])),
    ]

    currentLevelIndex = levelIndex
    currentLevel = allLevels[currentLevelIndex]
    level.blocks = [Block(block["pos"],block["block"],360-block["angle"]) for block in list(filter(lambda x: x["type"]=="block",currentLevel["objects"]))]
    level.enemies = [EnemyBall(enemy["pos"],enemy["enemy"]) for enemy in list(filter(lambda x: x["type"]=="enemy",currentLevel["objects"]))]

    birdMargin = 60 if len(currentLevel["birds"]) < 7 else 380/len(currentLevel["birds"])
    level.balls = list(reversed([Ball((slingShotPos[0]-(i+1)*birdMargin,level.size[1]-groundOffset-20),bird) for i,bird in enumerate(currentLevel["birds"])]))
    level.extraScore = currentLevel["extraScore"]
    mainBall = level.balls[-1]
    ballReady()

    level.totalScore = level.calculateTotalScore()

    GameObject(mult(subtr((280+112.5,screen_height-137.5-groundOffset),cam.getPos()),cam.zoom),mult(slingShotSize,cam.zoom),image=slingShotImage,layer=1)
    GameObject((level.size[0]/2,level.size[1]-groundOffset/2),(level.size[0],groundOffset),image=pygame.image.load("./img/ground.png").convert_alpha())
    scoreLabel = Text((30,25),"Score:",40,"black",labelFont,centered=False,layer=2)
    Text((30,75),f"Level {levelIndex+1}",20,"black",labelFont,centered=False,layer=2)
    trailLine = TrailLine()
    arrow = Arrow()
    winScreenScoreLabel = None

    if tutorialDict.get(f"{levelIndex+1}",None):
        tutorialImage = GameObject((screen_width/2,screen_height/2),(500,500),image=tutorialDict[f"{levelIndex+1}"],layer=3)
    else:
        tutorialImage = None
        

    particles = []

    aiming = False
    stretched = False
    readyToAim = True
    nextAnimation = False
    animationStartPos = [0,0]

    running = True
    delta = 0

def backToMenu():
    global level, gameTimers, gameObjects, space, cam, titleImage
    for timer in gameTimers:
        timer.cancel()
    gameTimers = []
    gameObjects = []
    # space = pymunk.Space()
    cam = Camera((screen_width,screen_height))
    titleImage = GameObject((screen_width/2,screen_height/2-200),(680,200),image=pygame.image.load("./img/title.png"))
    MovingBackground((screen_width/2,screen_height/2-2),(4315,725),0,image=mainMenuImage)
    addMainMenuSprites(10)
    chooseMenu("main")
    addLevelMenuButtons()
    level = None
    space = pymunk.Space()
    space.sleep_time_threshold = 1
    space.gravity = (0, 981)


def chooseMenu(menuName):
    playSound(clickSound)

    global menu, titleImage
    menu = menuName
    if menuName=="levels":
        titleImage.visible = False
    else:
        titleImage.visible = True
    

def addMainMenuSprites(n):
                    
    for i in range(n):
        objectList = random.choice([blockTemplates,enemyTemplates,birdTemplates])
        object = objectList[random.choice(list(objectList.keys()))]
        if object != enemyTemplates["boss"]:
            velocityRange = 2
            scaleFactor = 1 + random.random()*1
            angle = random.randint(0,360)
            pos = [random.randint(0,screen_width),random.randint(0,screen_height)]
            f = FloatingMenuSprite(pos,mult(object["size"],scaleFactor),0,image=object["image"],velocity=[2 + random.random()*velocityRange/2,-velocityRange + random.random()*velocityRange*2],angularVelocity=-1+random.random()+2,layer=1)
            f.angle = angle


if __name__=="__main__":
    

    # Running loop


    level = None
    cam = Camera((screen_width,screen_height))

    menu = "main"
   
    gameTimers = []
    gameObjects = []

    titleImage = GameObject((screen_width/2,screen_height/2-200),(680,200),image=pygame.image.load("./img/title.png"))
    MovingBackground((screen_width/2,screen_height/2-2),(4315,725),0,image=mainMenuImage)
    addMainMenuSprites(10)
    addLevelMenuButtons()
    
    tutorialImage = None

    running = True
    delta = 0
    lastTime = time.time()
    dt = 0
    while running:
        delta += 1

        if level:

            mouse = mult(pygame.mouse.get_pos(),cam.zoom)

            pos = subtr(slingShotPos,cam.getPos())
            ballToMouse = subtr(pos,mouse)
            ballToMouseMag = mag(ballToMouse)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if level.state == 1:
                        if currentLevelIndex == 24:
                            handleButtonEvents(endLevelButtons[0:2],event)
                        else:
                            handleButtonEvents(endLevelButtons,event)

                        
                    elif level.state == 2:
                        if currentLevelPassed>currentLevelIndex:
                            handleButtonEvents(endLevelButtons,event)
                        else:
                            handleButtonEvents(endLevelButtons[0:2],event)
                    else:
                        if tutorialImage:
                            gameObjects.remove(tutorialImage)
                            tutorialImage = None
                            playSound(clickSound)
                        else:
                            if mainBall and readyToAim and mag(ballToMouse) <= maxPullMag:
                                aiming = True
                            if mainBall:
                                if mainBall.shot and not mainBall.clicked and (not mainBall.hit or mainBall.bird["activateAfterHit"]):
                                    if mainBall.bird["func"]:
                                        mainBall.nextUpdateFunction = lambda: mainBall.bird["func"](mainBall)
                                        mainBall.clicked = True

                                        if mainBall.birdKey != "yellow" and mainBall.birdKey != "green":
                                            Marker(add(mouse,cam.getPos()))

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if aiming:
                        aiming = False
                        if ballToMouseMag > 50:
                            playSound(launchSound)
                            trailLine.points = []
                            readyToAim = False
                            stretched = False
                            mainBall.shape.filter = pymunk.ShapeFilter(categories=collisionMasks[0][0],mask=collisionMasks[0][1])
                            mainBall.body.activate()
                            impulse = mult(unit(ballToMouse),maxPullMag) if mag(ballToMouse) > maxPullMag else ballToMouse
                            mainBall.body.apply_impulse_at_local_point(mult(impulse,5))
                            mainBall.shot = True
                        else:
                            mainBall.body.position = slingShotPos
                            mainBall.body.sleep()



                elif event.type == pygame.MOUSEWHEEL:
                    if level.state == 0 and not tutorialImage:
                        cam.moveCam([event.y*2,0])

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        startLevel(currentLevelIndex)
                    elif event.key == pygame.K_ESCAPE:
                        backToMenu()
                    elif event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()


            if not level:
                continue

            screen.fill("white")
            screen.blit(spaceImage,subtr([-spaceImagePos,0],cam.getPos()))
            screen.blit(backgroundImage,mult(cam.getPos(),-1))
         
            spaceImagePos = spaceImagePos + 1 if spaceImagePos < level.size[0] else 0                      
            
            ballToMouse = mult(unit(ballToMouse),maxPullMag) if mag(ballToMouse) > maxPullMag else ballToMouse

            pygame.draw.line(screen,"#AF3C3F",mult(add(pos,[65,0]),cam.zoom),mult(subtr(pos,ballToMouse if aiming else [0,0]),cam.zoom),5)
            pygame.draw.line(screen,"#AF3C3F",mult(add(pos,[-65,-8]),cam.zoom),mult(subtr(pos,ballToMouse if aiming else [0,0]),cam.zoom),5)
            pygame.draw.rect(screen,"black",(0-cam.getPos()[0],level.size[1]-groundOffset-cam.getPos()[1],level.size[0],groundOffset))

            if aiming:
                mainBall.body.position = add(subtr(pos,ballToMouse),cam.getPos())
                mainBall.body.sleep()

                
                if ballToMouseMag >= 150:
                    if not stretched:
                        playSound(stretchSound)
                        stretched = True
                else:
                    stretchSound
                    if stretched:
                        stretched = False


            

            for gameObject in gameObjects:
                gameObject.draw()
            
            for gameObject in gameObjects:
                if gameObject.update:
                    gameObject.update()
            
            birdMargin = 60 if len(level.balls) < 7 else 380/len(level.balls)
            if nextAnimation:
                for i,ball in enumerate(level.balls):
                    if ball.active and not ball.shot:
                        step = 5
                        startPosition = [slingShotPos[0]-120,level.size[1]-groundOffset-ball.size[1]/2] if ball == mainBall else [slingShotPos[0]-(len(level.balls)-currentBallIndex-i+2)*birdMargin,level.size[1]-groundOffset-ball.size[1]/2]
                        endPosition = slingShotPos if ball == mainBall else [slingShotPos[0]-(len(level.balls)-currentBallIndex-i+1)*birdMargin,level.size[1]-groundOffset-ball.size[1]/2]
                        # print(i,startPosition[0],e[0])

                        if ball.body.position.x < endPosition[0]:
                            highPoint =  endPosition[1]-50
                            slope = (highPoint-startPosition[1])/(endPosition[0]-startPosition[0])
                            y = slope * (ball.body.position.x+step - startPosition[0]) + startPosition[1]



                            yp = (y-startPosition[1])/(highPoint-startPosition[1])
                            if yp < 0.7:
                                y = (1 - (1 - yp)**3)*(highPoint-startPosition[1])+(startPosition[1])
                            else:
                                yp = 1-yp
                                y = -yp*3*(endPosition[1]-highPoint)+(endPosition[1])
                            ball.body.position = [ball.body.position.x+step,y]
                            ball.body.sleep()

                        else:
                            ball.body.position = endPosition
                            ball.body.sleep()
                            if ball == mainBall:
                                nextAnimation = False
                                readyToAim = True
                        # else:
                        #     ball.body.position = [ball.body.position.x+5,ball.body.position.y]
                        #     ball.body.sleep()

            if mainBall:
                if mainBall.shot and ballTimer == None:
                    if mainBall.body.position.x > slingShotPos[0] and not delta % 3:
                        trailLine.addPoint(mainBall.body.position)

            if level.state == 0:
                cam.update()
            elif level.state == 1 and winScreenScoreLabel:
                if int(winScreenScoreLabel.text) < score:
                    winScreenScoreLabel.text = str(min(int(winScreenScoreLabel.text)+int(score/20),score))
                else:
                    stopSound(scoreSound,200)
                if currentLevelIndex == 24:
                    drawButtons(endLevelButtons[0:2])
                else:
                    drawButtons(endLevelButtons)

            elif level.state == 2:
                if currentLevelPassed>currentLevelIndex:
                    drawButtons(endLevelButtons)
                else:
                    drawButtons(endLevelButtons[0:2])
                

            updateScore()
        else:
            mouse = mult(pygame.mouse.get_pos(),cam.zoom)

            for event in pygame.event.get():
                if event.type == pygame.QUIT: running = False

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if menu == "main":
                        handleButtonEvents(mainMenuButtons,event)
                    elif menu == "levels":
                        handleButtonEvents(levelMenuButtons,event)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_F11:
                        pygame.display.toggle_fullscreen()

                    elif event.key == pygame.K_ESCAPE:
                        if menu == "main":
                            running = False
                        elif menu == "levels":
                            chooseMenu("main")

            if level:
                continue

            for gameObject in gameObjects:
                gameObject.draw()
            for gameObject in gameObjects:
                gameObject.update()

            if menu == "main":
                drawButtons(mainMenuButtons)
            elif menu == "levels":
                # drawButtons(levelMenuButtons)
                screen.blit(levelMenuButtonSurface,(0,0))

            if not delta % 50:
                objectList = random.choice([blockTemplates,enemyTemplates,birdTemplates])
                object = objectList[random.choice(list(objectList.keys()))]
                if object != enemyTemplates["boss"]:
                    velocityRange = 2
                    scaleFactor = 1 + random.random()*1
                    FloatingMenuSprite((-object["size"][0]/2*scaleFactor,random.randint(0,screen_height)),mult(object["size"],scaleFactor),0,image=object["image"],velocity=[2 + random.random()*velocityRange/2,-velocityRange + random.random()*velocityRange*2],angularVelocity=-1+random.random()+2,layer=1)

            
        if delta > 2000:
            delta = 0
        
        pygame.display.update()
        dt = time.time() - lastTime
        for i in range(2):
            space.step(1/100)
        # space.step(1/50)
        clock.tick(120)
        # print(dt)
        pygame.display.set_caption(f"Angry Amogus   FPS: {int(1/dt)}")
        dt *= 60
        lastTime = time.time()
