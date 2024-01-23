import pygame
from threading import Timer
import random
import math
import main
import json
import copy

pygame.init()


screen_width = 1280
screen_height = 720
screen = pygame.display.set_mode(flags=pygame.SCALED,vsync=1,size=(screen_width,screen_height))
pygame.display.set_caption("Amogus Bird")
clock = pygame.time.Clock()

snapPixels = 5
snapEnabled = False
blockIndexes = list(main.blockTemplates.keys())
enemyIndexes = list(main.enemyTemplates.keys())
birdIndexes = list(main.birdTemplates.keys())
categoryLists = [main.blockTemplates,main.enemyTemplates, main.birdTemplates]
categoryIndexes = [blockIndexes, enemyIndexes, birdIndexes]
categoryTypes = ["block","enemy"]

categoryIndex = 0
index = 0
angle = 0

objects = []
birdButtons = []
birds = []
extraScore = 0

offsetPos = (0,screen_height)
groundOffset = main.groundOffset

levelSize = [1440,720]
allLevels = []
currentLevel = 0
level = {}

with open("levels.json") as levels:
    data = json.load(levels)
    allLevels = data["levels"]
    currentLevel = data["currentLevel"]

if len(allLevels):
    level = allLevels[0]

camPos = [0,levelSize[1]-screen_height]

selectMenu = False
selectMenuButtons = []

def moveCam():
    speed = 10
    keys = pygame.key.get_pressed()
    if keys[pygame.K_RIGHT]:
        camPos[0] += speed
    elif keys[pygame.K_LEFT]:
        camPos[0] -= speed
    elif keys[pygame.K_DOWN]:
        camPos[1] += speed
    elif keys[pygame.K_UP]:
        camPos[1] -= speed

allButtons = []

def addBird(x):
    birds.append(x)

def popBird():
    if len(birds):
        birds.pop()


def changeExtra(dir):
    global extraScore
    extraScore += dir*50
    extraScore = max(0,extraScore)

def addButton(text="",size=(0,0),pos=(0,0),backgroundColor=None,image=None,color="black",fontSize=20,border_radius=0,function=None,hidden=False,buttonGroup=None):
    b = {"text":text,"rect":pygame.Rect(pos,(abs(size[0]),abs(size[1]))),"backgroundColor":backgroundColor,"image":pygame.transform.flip(image,flip_x=1,flip_y=0) if size[0] < 0 else image,"color":color,"fontSize":fontSize,"border_radius":border_radius,"hidden":hidden,"func":function}
    
    if buttonGroup != None:
        buttonGroup.append(b)

def drawText(text,color,size,center=(),pos=(),font="calibri"):
    font = pygame.font.SysFont(font,size)
    text = font.render(text,True,color)
    textRect = text.get_rect()
    if center:
        textRect.center = center
    if pos:
        textRect.topleft = pos
    screen.blit(text,textRect)

def drawButton(button):
    global cursor

    rect = (button["rect"][0],button["rect"][1],button["rect"][2],button["rect"][3])

    if button["backgroundColor"]:
        pygame.draw.rect(screen,
                        "black" if button["backgroundColor"]==None else button["backgroundColor"],
                        rect,border_radius=button["border_radius"])
    if button["image"]:
        image = pygame.transform.scale(button["image"],(button["rect"][2],button["rect"][3]))
        # if flip:
        #     image = pygame.transform.flip(image,flip_x=1,flip_y=0)
        screen.blit(image,rect)
    if button["text"]:
        drawText(button["text"],button["color"],button["fontSize"],(button["rect"][0]+button["rect"][2]/2,button["rect"][1]+button["rect"][3]/2))

def drawButtons(buttons):
    global cursor          
    for button in buttons:
        drawButton(button)

def handleButtonEvents(buttons):
    for button in buttons:
        if abs(mouse[0]-button["rect"][0]-button["rect"][2]/2) <= button["rect"][2]/2 and abs(mouse[1]-button["rect"][1]-button["rect"][3]/2) <= button["rect"][3]/2:
            if button["func"]:
                button["func"]()
                return True


def addBirdButtons():
    size = 50
    for i,bird in enumerate(categoryLists[2].items()):
        addButton("",[size,size],[i*(size+1),size+1],"lightblue",image=bird[1]["image"],buttonGroup=birdButtons, function=lambda x=i: addBird(birdIndexes[x]))
    addButton("Pop",[size,size],[len(categoryIndexes[2])*(size+1),size+1],"lightblue",buttonGroup=birdButtons, function=popBird)
    addButton("+",[size,size],[(len(categoryIndexes[2])+1)*(size+1),size+1],"lightblue",buttonGroup=birdButtons, function=lambda: changeExtra(1))
    addButton("-",[size,size],[(len(categoryIndexes[2])+2)*(size+1),size+1],"lightblue",buttonGroup=birdButtons, function=lambda: changeExtra(-1))

def selectLevel(i):
    global currentLevel, objects, birds, extraScore
    currentLevel = i
    if currentLevel < len(allLevels):
        level = allLevels[i]
        objects = []
        for object in level["objects"]:
            addObject(object)
        birds = level["birds"]
        extraScore = level["extraScore"]


    else:
        objects = []
        birds = []
        extraScore = 0

def addSelectButtons():
    global selectMenuButtons
    selectMenuButtons = []
    startPos = (screen_width/2-250,screen_height/2-250)
    margin = [10,10]
    for i, l in enumerate(allLevels):
        addButton(f"Level {i+1}",(80,20),(margin[0]+startPos[0]+(i%5)*(80+margin[0]),margin[1]+startPos[1]+(i//5)*(20+margin[1])),backgroundColor="white",buttonGroup=selectMenuButtons, function=lambda x=i: selectLevel(x))
    i = len(allLevels)
    addButton("New",(80,20),(margin[0]+startPos[0]+(i%5)*(80+margin[0]),margin[1]+startPos[1]+(i//5)*(20+margin[1])),backgroundColor="white",buttonGroup=selectMenuButtons, function=lambda x=i: selectLevel(x))

def changeCategory(i):
    global objectToPlace, categoryIndex, index
    categoryIndex = i

    if i < 2:
        index = min(index,len(categoryIndexes[categoryIndex])-1)
        objectToPlace = categoryLists[categoryIndex][categoryIndexes[categoryIndex][index]]
        objectToPlace["image"] = pygame.transform.scale(objectToPlace["image"],objectToPlace["size"])
    else:
        objectToPlace = None


def changeObject(dir=[0,0]):
    global objectToPlace, index
    if categoryIndex == 2:
        return
    index = (index//3)*3 + (index%3) + dir[0] + dir[1]*3
    if index >= len(categoryIndexes[categoryIndex]):
        index = 0
    elif index < 0:
        index = len(categoryIndexes[categoryIndex])-1

    objectToPlace = categoryLists[categoryIndex][categoryIndexes[categoryIndex][index]]
    objectToPlace["image"] = pygame.transform.scale(objectToPlace["image"],objectToPlace["size"])


def drawBounds():
    w = 5
    pygame.draw.line(screen,"black",main.subtr((0,0),camPos),main.subtr((levelSize[0],0),camPos),w)
    pygame.draw.line(screen,"black",main.subtr((0,levelSize[1]),camPos),main.subtr((levelSize[0],levelSize[1]),camPos),w)
    pygame.draw.line(screen,"black",main.subtr((levelSize[0],0),camPos),main.subtr((levelSize[0],levelSize[1]),camPos),w)
    pygame.draw.line(screen,"black",main.subtr((0,0),camPos),main.subtr((0,levelSize[1]),camPos),w)

def drawMenu():
    size = 50
    for i,catList in enumerate(categoryLists):
        pygame.draw.rect(screen,"blue" if categoryIndex == i else "lightblue",(i*(size+1),0,size,size))
        firstItem = catList[categoryIndexes[i][0]]
        screen.blit(pygame.transform.scale(firstItem["image"],firstItem["size"]),(i*(size+1)+(size/2)-firstItem["size"][0]/2,(size/2)-firstItem["size"][1]/2))

    if categoryIndex != 2:
        for i,(key,object) in enumerate(categoryLists[categoryIndex].items()):
            color = "lightblue"
            if index < len(categoryIndexes[categoryIndex]):
                if categoryIndexes[categoryIndex][index]==key and categoryIndexes[categoryIndex]==categoryIndexes[categoryIndex]:
                    color = "blue"

            pygame.draw.rect(screen,color,(i%3*(size+1),size+(size+1)*((i//3)),size,size))
            r = (size*0.75)/object["size"][1]
            objectSize = main.mult(object["size"],r)
            screen.blit(pygame.transform.scale(object["image"],objectSize),(i%3*(size+1)+(size/2)-objectSize[0]/2,size+(size+1)*((i//3))+(size/2)-objectSize[1]/2))
    
    else:
        drawButtons(birdButtons)
        drawText(f"Extra Score: {extraScore}","black",size=20,pos=[(len(categoryIndexes[2])+1)*(50+1)+125,65])
        
        # for i,(key,bird) in enumerate(categoryLists[2].items()):
        #     color = "lightblue"
        #     if index < len(categoryIndexes[categoryIndex]):
        #         if categoryIndexes[categoryIndex][index]==key and categoryIndexes[categoryIndex]==categoryIndexes[categoryIndex]:
        #             color = "blue"

        #     pygame.draw.rect(screen,color,(i%3*(size+1),size+(size+1)*((i//3)),size,size))
        #     r = (size*0.75)/object["size"][1]
        #     objectSize = main.mult(object["size"],r)
        #     screen.blit(pygame.transform.scale(object["image"],objectSize),(i%3*(size+1)+(size/2)-objectSize[0]/2,size+(size+1)*((i//3))+(size/2)-objectSize[1]/2))



def addObject(object):
    size = []
    if object["type"]=="block":
        size = main.blockTemplates[object["block"]]["size"]
    elif object["type"]=="enemy":
        size = main.enemyTemplates[object["enemy"]]["size"]

    object["rect"] = pygame.Rect(main.subtr(object["pos"],main.mult(size,1/2)),size)
    objects.append(object)

def drawObject(object):
    if object["type"]=="block":
        image = pygame.transform.scale(main.blockTemplates[object["block"]]["image"],main.add(main.blockTemplates[object["block"]]["size"],[2,2]))
    elif object["type"]=="enemy":
        image = pygame.transform.scale(main.enemyTemplates[object["enemy"]]["image"],main.add(main.enemyTemplates[object["enemy"]]["size"],[2,2]))

    rot = pygame.transform.rotate(image,object["angle"])
    new_rect = rot.get_rect(center = image.get_rect(center = main.subtr(object["pos"],camPos) ).center)
    screen.blit(rot,new_rect)

def drawHoverObject():
    objectToPlace["image"].set_alpha(128)
    rot = pygame.transform.rotate(objectToPlace["image"],angle)
    new_rect = rot.get_rect(center = objectToPlace["image"].get_rect(center = mouseSnap).center)
    screen.blit(rot,new_rect)

    # screen.blit(,main.subtr(mouseSnap,main.mult(objectToPlace["size"],1/2)))
    objectToPlace["image"].set_alpha(255)

def writeObjects():
    newObjects = copy.deepcopy(objects)
    startPos = [screen_height,0]
    tempOffset = [0,0]
    for level in allLevels:
        for object in level["objects"]:
            if object.get("rect",None):
                del object["rect"]

    for object in newObjects:
        if object.get("rect",None):
            del object["rect"]
        # rot = main.rotationMatrix(object["angle"])
        # if object["pos"][0] < startPos[0]:
        #     startPos[0] = object["pos"][0]
        #     tempOffset[0] = main.multMtrx(rot,categoryLists[categoryTypes.index(object["type"])][object[object["type"]]]["size"])[0]/2

        # if object["pos"][1] > startPos[1]:
        #     startPos[1] = object["pos"][1]
            
        #     tempOffset[1] = -main.multMtrx(rot,categoryLists[categoryTypes.index(object["type"])][object[object["type"]]]["size"])[1]/2
        # object["angle"] *= -1
        # if object["angle"] < 0:
        #     object["angle"] += 360
    # for object in newObjects:
    #     object["pos"] = main.add(main.subtr(object["pos"],startPos),offsetPos)

    # print(newObjects)
    print("Level Saved")
    newLevel = {"objects":newObjects,"birds":birds,"extraScore":extraScore}
    if currentLevel >= len(allLevels):
        allLevels.append(newLevel)
    else:
        allLevels[currentLevel] = newLevel
    with open('levels.json', 'w') as levels:
        json.dump({"levels":allLevels,"currentLevel":currentLevel}, levels)
    addSelectButtons()

def openMenu():
    global selectMenu
    selectMenu = True


def shift(dir):
    for object in allLevels[currentLevel]["objects"]:
        object["pos"] = main.add(object["pos"],dir)

# shift([0,100])
# allLevels[15],allLevels[17] = allLevels[17],allLevels[15]
        
if __name__=="__main__":
    

    # objects = level.get("block",None) or []
    selectLevel(currentLevel)
    objectToPlace = main.blockTemplates[blockIndexes[index]]
    changeObject()
    addBirdButtons()
    addSelectButtons()
    addButton("Select",(100,50),(screen_width-108,10),"lightblue",buttonGroup=allButtons,function=openMenu)

    running = True
    delta = 0
    while running:
        delta += 1

        mouse = pygame.mouse.get_pos()
        mouseSnap = (mouse[0]-mouse[0]%(snapPixels if snapEnabled else 1),mouse[1]-mouse[1]%(snapPixels if snapEnabled else 1))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if selectMenu:
                        handleButtonEvents(selectMenuButtons)
                    elif not handleButtonEvents(allButtons) and not handleButtonEvents(birdButtons) and objectToPlace:
                        addObject({"type":categoryTypes[categoryIndex],"pos":main.add(mouseSnap,camPos),categoryTypes[categoryIndex]:categoryIndexes[categoryIndex][index],"angle":angle})
                elif event.button == 3:
                    for object in objects:
                        if object["rect"].collidepoint(main.add(mouse,camPos)):
                            objects.remove(object)
                            break


            elif event.type == pygame.MOUSEWHEEL:
                angle = (angle+(event.y)*45)%360

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    changeObject([0,-1])

                elif event.key == pygame.K_a:
                    changeObject([-1,0])

                elif event.key == pygame.K_s:
                    changeObject([0,1])

                elif event.key == pygame.K_d:
                    changeObject([1,0])




                elif event.key == pygame.K_1:
                    changeCategory(0)

                elif event.key == pygame.K_2:
                    changeCategory(1)

                elif event.key == pygame.K_3:
                    changeCategory(2)

                elif event.key == pygame.K_RETURN:
                    writeObjects()

                elif event.key == pygame.K_LCTRL:
                    snapEnabled = not snapEnabled
                
                elif event.key == pygame.K_ESCAPE:
                    selectMenu = False

                    
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LCTRL:
                    snapEnabled = not snapEnabled

        screen.fill("white")
        pygame.draw.rect(screen,"gray",(-camPos[0],screen_height-groundOffset-camPos[1],levelSize[0],groundOffset))
        drawBounds()
        screen.blit(main.slingShotImage,main.subtr((280,levelSize[1]-275-groundOffset),camPos))
        drawMenu()
        # drawText(f"Angle: {angle}","black",50,(screen_width-150,50))

        if objectToPlace and not selectMenu:
            drawHoverObject()
        for object in objects:
            drawObject(object)

        birdMargin = 60 if len(birds) < 7 else 400/len(birds)
        for i,bird in enumerate(birds):
            birdObject = categoryLists[2][bird]
            pos = (400-(i+1)*birdMargin,levelSize[1]-birdObject["size"][1]-groundOffset) if i else main.subtr((400,levelSize[1]-220-groundOffset),main.mult(birdObject["size"],1/2))
            screen.blit(pygame.transform.scale(birdObject["image"],birdObject["size"]),main.subtr(pos,camPos))

        if selectMenu:
            pygame.draw.rect(screen,"lightblue",(screen_width/2-250,screen_height/2-250,500,500))
            drawButtons(selectMenuButtons)

        drawButtons(allButtons)

        moveCam()
        
        if delta > 1000:
            delta = 0

        clock.tick(120)
        pygame.display.update()