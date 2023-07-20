import pygame
from math import floor, ceil
from random import randint
import os, time, sys

#Initialization
pygame.init()
WIDTH = 1400
HEIGHT = 900
display = pygame.display.set_mode((WIDTH, HEIGHT))
cwd = os.getcwd()   

#Colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (238, 232, 170)
WATER_BLUE = (0, 0, 130)
BEIGE = (207, 185, 151)
DARK_RED = (124, 10, 2)
FOREST_GREEN = (11, 102, 35)
OLIVE_GREEN = (96, 168, 48)
GREY = (169, 169, 169)
DARK_BEIGE = (169, 149, 123)

#Fonts
textFont = pygame.font.SysFont("Comic Sans MS", 20)
signFont = pygame.font.SysFont("ComicSans MS", 17)
storeFont = pygame.font.SysFont("Comic Sans MS", 15)
titleFont = pygame.font.SysFont("Comic Sans MS", 40)

#Grid movement in directions(Clockwise starting from 1 is upwards direction)
movement = [[], [0, -1], [1, 0], [0, 1], [-1, 0]]

#Map Information
GRID_DIST_TOP = 25
GRID_WIDTH = 40
GRID_HEIGHT = 30
SQUARE_SIZE = 25
moveableSpaces = ["/", ".", ",", "-", "I"]
areaMap = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
spawnChances = [
    [],
    [20, 30, 50],
    [50, 50, 0],
    [10, 10, 80],
    [50, 40, 10],
    [30, 30, 40],
    [40, 50, 10],
    [100, 0, 0],
    [60, 30, 10],
    [40, 40, 20]
]
spawnRates = [0, 3, 3, 3, 3, 3, 3, 1, 3, 3]

#Folder and file information
groundAreas = ["", "mapAreaGround1.txt", "mapAreaGround2.txt", "mapAreaGround3.txt", "mapAreaGround4.txt", "mapAreaGround5.txt", "mapAreaGround6.txt", "mapAreaGround7.txt", "mapAreaGround8.txt", "mapAreaGround9.txt"]
obstacleAreas = ["", "mapArea1.txt", "mapArea2.txt", "mapArea3.txt", "mapArea4.txt", "mapArea5.txt", "mapArea6.txt", "mapArea7.txt", "mapArea8.txt", "mapArea9.txt"]
weaponFiles = ["weaponTypes.txt", "shieldTypes.txt"]

def loadTile(fileName, width, height):
    return pygame.transform.scale(pygame.image.load(os.path.join(cwd, "art", "tileArt", fileName)).convert_alpha(), (width, height))

def checkIfExitGame(events):
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

#Loads all the tile images
groundDict = {
    "." : loadTile("grassArt.png", 25, 25),
    "," : loadTile("snowArt.png", 25, 25),
    "/" : loadTile("pathArt.png", 25, 25),
    "!" : loadTile("charredGroundArt.png", 25, 25)
}

obstacleDict = {
    "#" : loadTile("treeArt.png", 50, 50),
    "%" : loadTile("waterArt.png", 25, 25),
    "^" : loadTile("snowyTreeLarge.png", 50, 50),
    "S" : loadTile("signArt.png", 25, 25),
    "C" : loadTile("chestArt.png", 25, 25),
    "T" : loadTile("smallTreeArt.png", 25, 25),
    "O" : loadTile("moveableRockArt.png", 25, 25),
    "I" : loadTile("iceArt.png", 25, 25),
    "L" : loadTile("staticRockArtLarge.png", 50, 50),
    "B" : loadTile("bushArt.png", 25, 25),
    "K" : loadTile("staticRockArtSmall.png", 25, 25),
    "P" : loadTile("snowyTreeSmall.png", 25, 25),
    "A" : loadTile("houseA.png", 300, 175)
}

#Game information
bossDefeated = False
def loadDirectionalSprites(folder, fileName): #Image rotation results in loss of quality
    sprites = [""]
    for i in range(1, 5):
        sprites.append(pygame.transform.scale(pygame.image.load(os.path.join(cwd, "art", folder, fileName + str(i) + ".png")).convert_alpha(), (25, 25)))
    return sprites

def isInConstraint(x, lower, upper):
    if x >= lower and x <= upper:
        return True
    else:
        return False

def drawTextBoxes(text, delay, backgroundColour, name):
    #Displays text from list of strings with 2 lines in every text box
    for i in range(0, len(text), 2):
        pygame.draw.rect(display, DARK_BEIGE, (150, 780, 1100, 40), 0)
        pygame.draw.rect(display, backgroundColour, (150, 820, 1100, 65), 0)
        displayName = textFont.render(name, 1, WHITE)
        display.blit(displayName, (175, 784))
        for k in range(2):
            if i+k <= len(text) - 1:
                displayText = signFont.render(text[i+k].strip(), 1, BLACK)
                display.blit(displayText, (175, 825 + k*25))
        pygame.display.update()
        pygame.time.wait(delay)

def getScreenPos(gridX, gridY):
    #Gets the position on the window from the position on the grid
    screenX = gridX * SQUARE_SIZE - GRID_WIDTH*SQUARE_SIZE/2 + WIDTH/2 - SQUARE_SIZE
    screenY = gridY * SQUARE_SIZE + GRID_DIST_TOP - SQUARE_SIZE
    return (screenX, screenY)

def textToBool(text):
    if text.strip() == "True":
        return True
    else:
        return False

#Information container classes  
class Node():
    def __init__(self, f, g, h, parent, position):
        self.f = f
        self.g = g
        self.h = h
        self.parent = parent
        self.position = position

class StoreItem():
    def __init__(self, item, stock, cost):
        self.item = item
        self.stock = stock
        self.cost = cost

class Button:
    alreadyClicked = False
    useable = True
    def __init__(self, x, y, width, height, colour, text, textColour, hoverColour):
        self.x = x
        self.y = y
        self.height = height
        self.width = width
        self.colour = colour
        self.text = text
        self.textColour = textColour
        self.hoverColour = hoverColour
        self.buttonFont = pygame.font.SysFont("Comic Sans MS", self.height - 14)
        self.displayText = self.buttonFont.render(self.text, 1, self.textColour)
        self.buttonRect = self.displayText.get_rect(center = (self.x + self.width/2, self.y + self.height/2))
 
    def draw(self):
        mouseX, mouseY = pygame.mouse.get_pos()
        if (self.x <= mouseX <= self.x + self.width) and (self.y <= mouseY <= self.y + self.height) and self.useable:
            pygame.draw.rect(display, self.hoverColour, (self.x, self.y, self.width, self.height), 0)
        else:
            pygame.draw.rect(display, self.colour, (self.x, self.y, self.width, self.height), 0)
        display.blit(self.displayText, self.buttonRect)
                
    def isHovered(self):
        mouseX, mouseY = pygame.mouse.get_pos()
        if (self.x <= mouseX <= self.x + self.width) and (self.y <= mouseY <= self.y + self.height):
            return True
        return False
    
    def isLeftClicked(self, events): 
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.isHovered():
                        return True
                    return False

    def isRightClicked(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3:
                    if self.isHovered():
                        return True
                    return False



#Item classes
class Item():
    def __init__(self, name, effect, sprite, throwable):
        self.name = name
        self.effect = effect
        self.sprite = sprite
        self.throwable = throwable

class StrengthPotion(Item):
    def __init__(self, name, effect, sprite, throwable):
        Item.__init__(self, name, effect, sprite, throwable)
    
    def usePot(self, player):
        player.addDamage += self.effect

class HealthPotion(Item):
    def __init__(self, name, effect, sprite, throwable):
        Item.__init__(self, name, effect, sprite, throwable)

    def usePot(self, player):
        player.remainingHealth += self.effect
        if player.remainingHealth > player.maxHealth:
            player.remainingHealth = player.maxHealth
                                
class Shield(Item):
    def __init__(self, name, effect, sprite, throwable):
        Item.__init__(self, name, effect, sprite, throwable)
    
class Weapon(Item):
    def __init__(self, name, effect, sprite, throwable):
        Item.__init__(self, name, effect, sprite, throwable)

class GameObject():
    def __init__(self, areaNumber):
        self.areaNumber = areaNumber

class FreeMovingObject():
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Projectile(FreeMovingObject):
    def __init__(self, x, y, sizeX, sizeY, speed):
        FreeMovingObject.__init__(self, x, y)
        self.sizeX = sizeX
        self.sizeY = sizeY
        self.speed = speed

    def isContact(self, player):
        playerCornerLocations = []
        playerCornerLocations.append((player.x, player.y))
        playerCornerLocations.append((player.x + 50, player.y))
        playerCornerLocations.append((player.x, player.y + 50))
        playerCornerLocations.append((player.x + 50, player.y + 50))

        for i in playerCornerLocations:
            if self.x <= i[0] <= self.x + self.sizeX and self.y <= i[1] <= self.y + self.sizeY:
                return True
        return False

    def draw(self):
        display.blit(self.sprite, (self.x, self.y))     

class ZombieProjectile(Projectile):
    def __init__(self, x, y, sizeX, sizeY, speed):
        Projectile.__init__(self, x, y, sizeX, sizeY, speed)
        self.destX = 0 - self.sizeX
        self.sprite = loadTile("zombieProj.png", self.sizeX, self.sizeY)

    def move(self):
        self.x -= self.speed

    def finished(self):
        if self.x < self.destX:
            return True
        return False

class BookProjectile(Projectile):
    def __init__(self, x, y, sizeX, sizeY, speed):
        Projectile.__init__(self, x, y, sizeX, sizeY, speed)
        self.destX = 0 - self.sizeX
        self.sprite = loadTile("bookProj.png", self.sizeX, self.sizeY)

    def finished(self):
        if self.x < self.destX:
            return True
    
    def move(self):
        self.x -= self.speed

class SlimeProjectile(Projectile):
    def __init__(self, x, y, sizeX, sizeY, speed):
        Projectile.__init__(self, x, y, sizeX, sizeY, speed)
        self.destY = 600
        self.sprite = loadTile("slimeProj.png", self.sizeX, self.sizeY)

    def finished(self):
        if self.y == self.destY:
            return True
        return False

    def move(self):
        for i in range(self.speed):
            if self.finished():
                return
            self.y += 1

class GridRestrictedObject():
    def __init__(self, gridX, gridY):
        self.gridX = gridX
        self.gridY = gridY

class Character(GameObject):
    def __init__(self, areaNumber, name, remainingHealth, maxHealth, speed, attack, direction):
        GameObject.__init__(self, areaNumber)
        self.name = name
        self.remainingHealth = remainingHealth
        self.maxHealth = maxHealth
        self.speed = speed
        self.attack = attack
        self.direction = direction

    def displayHealthBar(self, surface, topLeftX, topLeftY, length, unfilledColour, textColour):
        percentageFilled = round(self.remainingHealth/self.maxHealth * length)
        healthData = textFont.render(str(self.remainingHealth) + "/" + str(self.maxHealth), 1, textColour)
        pygame.draw.rect(surface, unfilledColour, (topLeftX, topLeftY, length, 20), 0)
        pygame.draw.rect(surface, RED, (topLeftX, topLeftY, percentageFilled, 20), 0)
        pygame.draw.rect(surface, BLACK, (topLeftX, topLeftY, length, 20), 2)
        surface.blit(healthData, (topLeftX + length + 10, topLeftY - 5))

class MovingCharacter(FreeMovingObject, Character):
    def __init__(self, areaNumber, x, y, name, remainingHealth, maxHealth, speed, attack, direction):
        FreeMovingObject.__init__(self, x, y)
        Character.__init__(self, areaNumber, name, remainingHealth, maxHealth, speed, attack, direction)
    
    def getGridPos(self, pointX, pointY, floored): 
        #Gets grid position from a position on the screen
        gridPosX = (pointX - WIDTH/2 + GRID_WIDTH*SQUARE_SIZE/2)/SQUARE_SIZE
        gridPosY = (pointY - GRID_DIST_TOP)/SQUARE_SIZE
        if(floored):
            return (floor(gridPosX + 1), floor(gridPosY + 1))
        else:
            return (gridPosX + 1, gridPosY + 1)

    def slide(self, obstacleMap, mobs):
        middle = self.getGridPos(self.x + SQUARE_SIZE/2, self.y + SQUARE_SIZE/2, True)
        #Runs 3 times resulting in speed of 3
        for i in range(3):
            #Checks if character is still on ice
            if obstacleMap[middle[1]][middle[0]] == "I":
                newX = self.x + movement[self.direction][0]
                newY = self.y + movement[self.direction][1]
                
                #If no collision with mob or no collision with obstacles allows it to slide
                for mob in mobs:
                    if mob != self:
                        if self.isContactEntity(mob, newX, newY):
                            return False
                if self.isCollide(obstacleMap, newX, newY):
                    return False
                else:
                    self.x = newX
                    self.y = newY 
            else:
                return False
        return True

    def isCollide(self, obstacleMap, movedX, movedY):
        cornerLocations = []
        cornerLocations.append(self.getGridPos(movedX, movedY, False)) #Top left
        cornerLocations.append(self.getGridPos(movedX + SQUARE_SIZE - 1, movedY, False)) #Top Right
        cornerLocations.append(self.getGridPos(movedX, movedY + SQUARE_SIZE - 1, False)) #Bottom Left
        cornerLocations.append(self.getGridPos(movedX + SQUARE_SIZE - 1, movedY + SQUARE_SIZE - 1, False)) #Bottom Right

        #For all corner locations of a character, it checks if it is colliding with something
        for corner in cornerLocations:
            if not isInConstraint(corner[0], 0, GRID_WIDTH + 2) or not isInConstraint(corner[1], 0, GRID_HEIGHT + 2):
                return True
            elif obstacleMap[floor(corner[1])][floor(corner[0])] not in moveableSpaces:
                return True
        return False

    def isContactEntity(self, entity, movedX, movedY):
        newPos = self.getGridPos(movedX + SQUARE_SIZE/2, movedY + SQUARE_SIZE/2, False)
        entityLocation = self.getGridPos(entity.x + SQUARE_SIZE/2, entity.y + SQUARE_SIZE/2, False)

        if isInConstraint(newPos[0], entityLocation[0] - 1, entityLocation[0] + 1) and isInConstraint(newPos[1], entityLocation[1] - 1, entityLocation[1] + 1):
            return True
        else:
            return False

class StaticCharacter(GridRestrictedObject, Character):
    def __init__(self, areaNumber, gridX, gridY, name, remainingHealth, maxHealth, speed, attack, direction):
        GridRestrictedObject.__init__(self, gridX, gridY)
        Character.__init__(self, areaNumber, name, remainingHealth, maxHealth, speed, attack, direction)
    
class Aggressive(MovingCharacter):
    path = []
    sprites = []
    index = 1
    pathAvailable = True
    timeSinceLastSearch = 1


    def __init__(self, areaNumber, x, y, name, remainingHealth, maxHealth, speed, attack, direction, level):
        MovingCharacter.__init__(self, areaNumber, x, y, name, remainingHealth, maxHealth, speed, attack, direction)
        self.level = level
        self.percentRun = self.level * 30
    
    def draw(self):
        display.blit(self.sprites[self.direction], (self.x, self.y))

    def getPlayerPath(self, player, obstacleMap, mobs): #aStar algorithm
        #If there was no path on last iteration it doesnt run for 50 calls to reduce lag
        if(self.pathAvailable or self.timeSinceLastSearch % 50 == 0):
            self.timeSinceLastSearch = 1
            self.index = 1
            
            #Initializes algorith
            end = player.getGridPos(player.x, player.y, True)
            start = player.getGridPos(self.x, self.y, True)
            openSet = set()
            openList = []
            closedSet = set()
            openList.append(Node(0, 0, 0, None, start))
            openSet.add(start)

            minf = 100000
            toCheckIndex = 0

            while len(openSet) > 0:
                #Finds node with smallest f value
                for i, node in enumerate(openList):
                    if node.f < minf:
                        minf = node.f
                        toCheckIndex = i
                
                #Gets the current node
                currentNode = openList.pop(toCheckIndex)
                openSet.remove(currentNode.position)
                closedSet.add(currentNode.position)

                #Check if the node is the end and returns path if it is
                if currentNode.position == end:
                    currentCheckNode = currentNode
                    path = []
                    while(currentCheckNode.parent != None):
                        path.insert(0, currentCheckNode.position)
                        currentCheckNode = currentCheckNode.parent
                    path.insert(0, start)
                    self.pathAvailable = True
                    self.path = path
                    return
                
                #Gets squares from all four directions
                for i in movement[1:]:
                    newPos = (currentNode.position[0] + i[0], currentNode.position[1] + i[1])
                    #Makes sure it is in the map and that it is not colliding with obstacle
                    if isInConstraint(newPos[0], 1, GRID_WIDTH) and isInConstraint(newPos[1], 1, GRID_HEIGHT):
                        if obstacleMap[newPos[1]][newPos[0]] in moveableSpaces:
                            #Makes sure node was not visited already
                            if newPos in closedSet or newPos in openSet:
                                continue
                            else:
                                #Generates nodes with heuristics and adds to open list
                                g = currentNode.g + 1
                                h = (currentNode.position[0] - newPos[0]) ** 2 + (currentNode.position[1] - newPos[1]) **2
                                f = g+h
                                openSet.add(newPos)
                                openList.append(Node(f, g, h, currentNode, newPos))
            self.path = []
            self.pathAvailable = False
        else:
            self.timeSinceLastSearch += 1

    def moveToGridCoord(self, obstacleMap, gridX, gridY, mobs):
        screenPos = getScreenPos(gridX, gridY)
        #Finds which way mob needs to move
        for i in range(self.speed):
            if self.y < screenPos[1] and not self.isCollide(obstacleMap, self.x, self.y + 1):
                self.direction = 3
            elif self.x > screenPos[0] and not self.isCollide(obstacleMap, self.x - 1, self.y):
                self.direction = 4
            elif self.y > screenPos[1] and not self.isCollide(obstacleMap, self.x, self.y - 1):
                self.direction = 1
            elif self.x < screenPos[0] and not self.isCollide(obstacleMap, self.x + 1, self.y):
                self.direction = 2
            else:
                return True

            newX = self.x + movement[self.direction][0]
            newY = self.y + movement[self.direction][1]

            #Moves if no collision
            if not self.isCollide(obstacleMap, newX, newY):
                noEntityBlock = True
                #Makes sure it is not colliding with another mob
                for mob in mobs:
                    if mob != self:
                        if self.isContactEntity(mob, newX, newY):
                            noEntityBlock = False
                if noEntityBlock:
                    self.x = newX
                    self.y = newY
        return False

    def moveToPlayer(self, player, obstacleMap, mobs):
        playerPos = self.getGridPos(self.x, self.y, True)
        if self.index < len(self.path):
            if playerPos not in self.path:
                return
            if self.moveToGridCoord(obstacleMap, self.path[self.index][0], self.path[self.index][1], mobs):
                if self.index < len(self.path) - 1:
                    self.index += 1
        else:
            self.getPlayerPath(player, obstacleMap, mobs)
    
class Zombie(Aggressive):
    sprites = loadDirectionalSprites("zombie", "Zombie")
    def __init__(self, areaNumber, x, y, name, remainingHealth, maxHealth, speed, attack, direction, level):
        Aggressive.__init__(self, areaNumber, x, y, name, remainingHealth, maxHealth, speed, attack, direction, level)
    
    def loadProjectiles(self):
        projectiles = []
        projectiles.append(ZombieProjectile(randint(1400, 1500), 500, 250, 100, self.level + 2))
        return projectiles
    
class Book(Aggressive):
    sprites = loadDirectionalSprites("Book", "Book")
    def __init__(self, areaNumber, x, y, name, remainingHealth, maxHealth, speed, attack, direction, level):
        Aggressive.__init__(self, areaNumber, x, y, name, remainingHealth, maxHealth, speed, attack, direction, level)

    def loadProjectiles(self):
        projectiles = []
        for i in range(2 * self.level):
            size = randint(45, 55)
            projectiles.append(BookProjectile(randint(1400, 1600), randint(100, 550), size, size, self.level + randint(1, 5)))
        return projectiles
            
class Slime(Aggressive):
    sprites = loadDirectionalSprites("slime", "Slime")
    def __init__(self, areaNumber, x, y, name, remainingHealth, maxHealth, speed, attack, direction, level):
        Aggressive.__init__(self, areaNumber, x, y, name, remainingHealth, maxHealth, speed, attack, direction, level)

    def loadProjectiles(self):
        projectiles = []
        for i in range(2 * self.level):
            size = randint(45, 55)
            projectiles.append(SlimeProjectile(randint(300, 1050), randint(50, 100), size, size, self.level + randint(1, 3)))
        return projectiles

class Necromancer(Aggressive):
    sprites = loadDirectionalSprites("necromancer", "Necromancer")
    def __init__(self, areaNumber, x, y, name, remainingHealth, maxHealth, speed, attack, direction, level):
        Aggressive.__init__(self, areaNumber, x, y, name, remainingHealth, maxHealth, speed, attack, direction, level)
    def loadProjectiles(self):
        projectiles = []
        attack = randint(1, 3)

        #Loads one of the three attacks
        if attack == 1:
            for i in range(self.level):
                size = randint(45, 65)
                projectiles.append(SlimeProjectile(randint(300, 1050), randint(50, 100), size, size, self.level))
        elif attack == 2:
            for i in range(self.level):
                size = randint(45, 65)
                projectiles.append(BookProjectile(randint(1400, 1600), randint(100, 550), size, size, self.level))
        else:
            projectiles.append(ZombieProjectile(randint(1400, 1500), 500, 300, 125, self.level))
        return projectiles

class Villager(StaticCharacter):
    def __init__(self, areaNumber, gridX, gridY, name, remainingHealth, maxHealth, speed, attack, direction, dialogue):
        StaticCharacter.__init__(self, areaNumber, gridX, gridY, name, remainingHealth, maxHealth, speed, attack, direction)
        self.dialogue = dialogue
    
    def speak(self):
        drawTextBoxes(self.dialogue, 1000, BEIGE, self.name)

class SellingVillager(Villager):
    def __init__(self, areaNumber, gridX, gridY, name, remainingHealth, maxHealth, speed, attack, direction, dialogue, store):
        Villager.__init__(self, areaNumber, gridX, gridY, name, remainingHealth, maxHealth, speed, attack, direction, dialogue)
        self.store = store
    
    #Store interface
    def sell(self, player):
        selling = True
        storeSurface = pygame.Surface((WIDTH, HEIGHT))
        #Drawing the labels and store background
        pygame.draw.rect(storeSurface, BEIGE, (400, 100, 600, 600), 0)
        pygame.draw.rect(storeSurface, DARK_BEIGE, (400, 30, 600, 70), 0)
        titleLabel = titleFont.render(self.name + "'s Store", 1, BLACK)
        nameLabel = storeFont.render("NAME", 1, BLACK)
        stockLabel = storeFont.render("STOCK", 1, BLACK)
        costLabel = storeFont.render("PRICE", 1, BLACK)
        storeSurface.blit(titleLabel, (450, 35))
        storeSurface.blit(nameLabel, (450, 125))
        storeSurface.blit(stockLabel, (650, 125))
        storeSurface.blit(costLabel, (750, 125))
        
        buttons = []
        #Drawing the items
        for i, storeItem in enumerate(self.store):
            buttons.append(Button(850, 170 + i*50, 100, 25, FOREST_GREEN, "BUY", BLACK, OLIVE_GREEN))
            itemName = storeFont.render(storeItem.item.name, 1, BLACK)
            itemCost = storeFont.render(str(storeItem.cost), 1, BLACK)
            storeSurface.blit(itemName, (450, 170 + i*50))
            storeSurface.blit(itemCost, (750, 170 + i*50))
         
        exitButton = Button(950, 30, 50, 50, RED, "X", BLACK, DARK_RED)

        while(selling):
            events = pygame.event.get()
            checkIfExitGame(events)

            display.blit(storeSurface, (0, 0))

            #Displays amount of gold
            amountOfGold = titleFont.render(str(player.goldAmount), 1, BLACK)
            display.blit(loadTile("coin.png", 50, 50), (700, 635))
            display.blit(amountOfGold, (760, 630))

            #Rerenders stock since it will change
            for i, storeItem in enumerate(self.store):
                itemStock = storeFont.render(str(storeItem.stock), 1, BLACK)
                display.blit(itemStock, (650, 170 + i*50))

            exitButton.draw()
            if exitButton.isLeftClicked(events):
                selling = False
            
            #Checks which item player is trying to purchase with buy button
            for button in buttons:
                button.draw()

            for i, button in enumerate(buttons):
                if button.isLeftClicked(events):
                    #Player purchases the item and has enough gold and space
                    if player.goldAmount >= self.store[i].cost and len(player.inventory) != player.maxInventorySize and self.store[i].stock > 0:
                        player.goldAmount -= self.store[i].cost
                        player.inventory.append(self.store[i].item)
                        self.store[i].stock -= 1
                        drawTextBoxes(["Thanks for buying!", "Here's your "  + self.store[i].item.name], 500, BEIGE, self.name)
                    else:
                        drawTextBoxes(["I can't purchase this right now!"], 500, BEIGE, "(Thinking to yourself)")
            pygame.display.update()


class GivingVillager(Villager):
    def __init__(self, areaNumber, gridX, gridY, name, remainingHealth, maxHealth, speed, attack, direction, dialogue, items):
        Villager.__init__(self, areaNumber, gridX, gridY, name, remainingHealth, maxHealth, speed, attack, direction, dialogue)
        self.items = items
    def speak(self):
        drawTextBoxes(self.dialogue, 1000, BEIGE, self.name)
    
    def giveItem(self, player):
        if(len(player.inventory) == player.maxInventorySize):
            drawTextBoxes(["Throw out some items please"], 1000, BEIGE, self.name)
        else:
            if len(self.items) > 0:
                for i in self.items:
                    player.inventory.append(i)
                    drawTextBoxes(["HERE IS A " + i.name + "!"], 1000, BEIGE, self.name)      
                self.items.clear()     

class Player(MovingCharacter):
    maxInventorySize = 16
    def __init__(self, areaNumber, x, y, name, remainingHealth, maxHealth, speed, attack, direction, goldAmount, inventory, activeWeapon, activeShield, addDamage):
        MovingCharacter.__init__(self, areaNumber, x, y, name, remainingHealth, maxHealth, speed, attack, direction)
        self.goldAmount = goldAmount
        self.inventory = inventory
        self.activeWeapon = activeWeapon
        self.activeShield = activeShield    
        self.addDamage = addDamage

    def displayInventory(self, inBattle):
        #Gets inventory background
        inventorySurface = pygame.Surface((600, 600)).convert_alpha()
        inventorySurface.fill(BEIGE)

        allButtons = []
        for i in range(4):
            buttonRow = []
            for k in range(4):
                pygame.draw.rect(inventorySurface, DARK_BEIGE, (20 + i*155, 70 + k*130, 100, 100), 0)
                buttonRow.append(Button(420 + k*155, 170 + i*130, 100, 100, BEIGE, "", BEIGE, BEIGE))
            allButtons.append(buttonRow)
        
        exitButton = Button(950, 100, 50, 50, RED, "X", BLACK, DARK_RED)
        inInventory = True
        while(inInventory):
            events = pygame.event.get()
            checkIfExitGame(events)

            display.blit(inventorySurface, (400, 100))
            exitButton.draw()
            if exitButton.isLeftClicked(events):
                inInventory = False

            itemCounter = 0
            for i in range(4):
                for k in range(4):
                    if itemCounter < len(self.inventory):
                        item = self.inventory[itemCounter]
                        display.blit(pygame.transform.scale(item.sprite, (80, 80)), (430 + k*155, 170 + i*130))
                    itemCounter += 1

            for i in range(4):
                for k in range(4):
                    if i*4 + k < len(self.inventory):
                        if allButtons[i][k].isHovered():
                            currItem = self.inventory[i*4 + k]
                            itemName = textFont.render(currItem.name, 1, BLACK)
                            className = self.inventory[i*4 + k].__class__.__name__

                            if k < 2:
                                itemRect = itemName.get_rect(topleft = (430 + k*155, 170 + i*130))
                            else:
                                itemRect = itemName.get_rect(topright = (430 + k*155, 170 + i*130))
                            pygame.draw.rect(display, WHITE, itemRect, 0)
                            display.blit(itemName, itemRect)
                            pygame.draw.rect(display, GREY, (itemRect[0], itemRect[1] + itemRect[3], itemRect[2], 30))
                            if className == "Weapon" or className == "StrengthPotion":
                                stats = textFont.render("+" + str(currItem.effect) + " atk", 1, BLACK)
                            elif className == "Shield" or className == "HealthPotion":
                                stats = textFont.render("+" + str(currItem.effect) + " health", 1, BLACK)
                            
                            display.blit(stats, (itemRect[0] + 5, itemRect[1] + itemRect[3] + 3))



                        if allButtons[i][k].isLeftClicked(events):
                            className = self.inventory[i*4 + k].__class__.__name__
                            usedItem = self.inventory[i*4 + k]
                            #Swaps weapons
                            if className == "Weapon":
                                if not inBattle:
                                    self.inventory.pop(i*4 + k)
                                    if self.activeWeapon != None:
                                        self.inventory.append(self.activeWeapon)
                                    self.activeWeapon = usedItem
                            #Swaps shields
                            elif className == "Shield":
                                if not inBattle:
                                    self.inventory.pop(i*4 + k)
                                    if self.activeShield != None:
                                        self.maxHealth -= self.activeShield.effect
                                        self.inventory.append(self.activeShield)
                                    self.activeShield = usedItem
                                    self.maxHealth += self.activeShield.effect
                            #Uses health potion if you can
                            elif className == "HealthPotion":
                                if self.remainingHealth != self.maxHealth:
                                    self.inventory.pop(i*4 + k)
                                    usedItem.usePot(self)
                                    drawTextBoxes(["You gained " + str(usedItem.effect) + " health"], 500, BEIGE, "Mysterious voice")
                                    if inBattle:
                                        return
                                else:
                                    drawTextBoxes(["I am already healthy", "I can not use this right now"], 500, BEIGE, "Thinking to yourself")
                            elif className == "StrengthPotion":
                                if inBattle:
                                    drawTextBoxes(["You gained " + str(usedItem.effect) + " damage"], 500, BEIGE, "Mysterious voice")
                                    return
                                else:
                                    drawTextBoxes(["I can only use this in battle!"], 750, BEIGE, "Thinking to yourself")
                        elif allButtons[i][k].isRightClicked(events) and not inBattle:
                            if self.inventory[i*4 + k].throwable:
                                threwAway = self.inventory.pop(i*4 + k)
                                drawTextBoxes(["Threw away " + threwAway.name], 750, BEIGE, "Yourself")
                            else:
                                drawTextBoxes(["You should not throw this away!"], 750, BEIGE, "Voice in your head")

                            #Updates hotbar
                        pygame.draw.rect(display, BLACK, (150, 780, 1100, 105), 0)
                        
                        if not inBattle:
                            self.loadHotBar()
                            self.drawHotBar(events, inBattle)
            pygame.display.update()
        
class PlayerMap(Player):
    hotBarSurface = None
    inventoryButton = Button(830, 795, 100, 30, DARK_BEIGE, "Inventory", BLACK, WHITE)
    canCut = False
    canPush = False

    sprites = loadDirectionalSprites("player", "Player")
    def __init__(self, areaNumber, x, y, name, remainingHealth, maxHealth, speed, attack, direction, goldAmount, inventory, activeWeapon, activeShield, addDamage):
        Player.__init__(self, areaNumber, x, y, name, remainingHealth, maxHealth, speed, attack, direction, goldAmount, inventory, activeWeapon, activeShield, addDamage)

    def draw(self):
         display.blit(self.sprites[self.direction], (self.x, self.y))

    def getMovement(self, grid, mobs):
        if not player.slide(currObstacleMap, mobs): 
            newX = self.x
            newY = self.y
            for i in range(self.speed):
                keys = pygame.key.get_pressed()
                if keys[pygame.K_RIGHT] or keys[pygame.K_LEFT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
                    if keys[pygame.K_RIGHT]:
                        self.direction = 2
                    elif keys[pygame.K_LEFT]:
                        self.direction = 4
                    elif keys[pygame.K_UP]:
                        self.direction = 1
                    elif keys[pygame.K_DOWN]:
                        self.direction = 3
                    newX += movement[self.direction][0]
                    newY += movement[self.direction][1]
                
                #Allows you to move if no collision
                if not self.isCollide(grid, newX, newY):
                    self.x = newX
                    self.y = newY

    def goNewArea(self): #Returns 0 if player has not left area, otherwise returns the direction they left from (clockwise starting from top)
        cornerLocations = []
        cornerLocations.append(self.getGridPos(self.x, self.y, False))
        cornerLocations.append(self.getGridPos(self.x + SQUARE_SIZE, self.y + SQUARE_SIZE, False)) 
        
        #Finds if you have left the area and returns which area you are leaving to
        for i in range(2): #xPos
            for k in range(2): #yPos
                pointX = cornerLocations[i][0]
                pointY = cornerLocations[k][1]
                if(pointY <= 1):
                   return 1
                elif(pointX >= GRID_WIDTH+1):
                    return 2
                elif(pointY >= GRID_HEIGHT+1):
                    return 3
                elif(pointX <= 1):
                    return 4
        return 0
        
    def getSpaceInfront(self): #Extra +- 1 removes issue of player being exactly right next to object due to nature of coordinate system
        if self.direction == 1:
            playerCoord = self.getGridPos(self.x + SQUARE_SIZE/2, self.y, True)
            return (playerCoord[0], playerCoord[1] - 1)
        elif self.direction == 2:
            playerCoord = self.getGridPos(self.x + SQUARE_SIZE - 1, self.y + SQUARE_SIZE/2, True)
            return (playerCoord[0] + 1, playerCoord[1])
        elif self.direction == 3:
            playerCoord = self.getGridPos(self.x + SQUARE_SIZE/2, self.y + SQUARE_SIZE - 1, True)
            return (playerCoord[0], playerCoord[1] + 1)
        elif self.direction == 4:
            playerCoord = self.getGridPos(self.x, self.y + SQUARE_SIZE/2, True)
            return (playerCoord[0] - 1, playerCoord[1])

    def interactAndUpdate(self, currObstacleMap, signs, chests, givingVillagers, sellingVillagers): #Used to interact with environment and returns if map needs to be updated
        spaceInfront = self.getSpaceInfront()
        #Checks if space is in map
        if isInConstraint(spaceInfront[0], 0, GRID_WIDTH + 2) and isInConstraint(spaceInfront[1], 0, GRID_HEIGHT + 2):
            #If it is a sign
            if currObstacleMap[spaceInfront[1]][spaceInfront[0]] == "S":
                for s in signs:
                    if s.areaNumber == self.areaNumber and s.gridX == spaceInfront[0] and s.gridY == spaceInfront[1]:
                        s.read(self)
                        return False
            #If it is a chest
            elif currObstacleMap[spaceInfront[1]][spaceInfront[0]] == "C":
                for c in chests:
                    if c.areaNumber == self.areaNumber and c.gridX == spaceInfront[0] and c.gridY == spaceInfront[1]:
                        c.giveItem(self)
                        return True
            #If it is a cutting tree
            elif currObstacleMap[spaceInfront[1]][spaceInfront[0]] == "T":
                if self.canCut:
                    currObstacleMap[spaceInfront[1]][spaceInfront[0]] = "."
                else:
                    #Checks if player has acquired an axe and if they have allows them to cut trees
                    hasAxe = False 
                    for item in self.inventory:
                        if item.name == "Axe":
                            hasAxe = True
                    if hasAxe:
                        self.canCut = True
                        currObstacleMap[spaceInfront[1]][spaceInfront[0]] = "."          
                return True
            #if it is a moveable rock
            elif currObstacleMap[spaceInfront[1]][spaceInfront[0]] == "O":
                movedX = spaceInfront[0] + movement[self.direction][0]
                movedY = spaceInfront[1] + movement[self.direction][1]
                if currObstacleMap[movedY][movedX] == ".":
                    currObstacleMap[movedY][movedX] = "O"
                    currObstacleMap[spaceInfront[1]][spaceInfront[0]] = "."
                    return True
            #If it is a giving villager
            elif currObstacleMap[spaceInfront[1]][spaceInfront[0]] == "G":
                for v in givingVillagers:
                    if v.areaNumber == self.areaNumber and v.gridX == spaceInfront[0] and v.gridY == spaceInfront[1]:
                        v.speak()
                        v.giveItem(self)
                        return False
            #If it is a selling villager
            elif currObstacleMap[spaceInfront[1]][spaceInfront[0]] == "$":
                for v in sellingVillagers:
                    if v.areaNumber == self.areaNumber and v.gridX == spaceInfront[0] and v.gridY == spaceInfront[1]:
                        v.speak()
                        v.sell(self)
                        return True

    def loadHotBar(self):
        #Gets hotbar background
        newHotBarSurface = pygame.Surface((500, 100))
        newHotBarSurface.fill(BEIGE)
        pygame.draw.rect(newHotBarSurface, DARK_BEIGE, (20, 10, 80, 80), 0)
        pygame.draw.rect(newHotBarSurface, DARK_BEIGE, (120, 10, 80, 80), 0)

        #Displays active weapons
        if self.activeWeapon != None:
            newHotBarSurface.blit(pygame.transform.scale(self.activeWeapon.sprite, (70, 70)), (25, 15))
        elif self.activeShield != None:
            newHotBarSurface.blit(pygame.transform.scale(self.activeShield.sprite, (70, 70)), (125, 15))

        #Displays gold amount
        goldText = textFont.render(str(self.goldAmount), 1, BLACK)
        goldCoin = loadTile("coin.png", 25, 25)
        newHotBarSurface.blit(goldCoin, (220, 15))
        newHotBarSurface.blit(goldText, (250, 10))

        #Displays health bar
        self.displayHealthBar(newHotBarSurface, 220, 60, 150, WHITE, BLACK)
        self.hotBarSurface = newHotBarSurface
            
    def drawHotBar(self, events, inBattle):
        display.blit(self.hotBarSurface, (450, 785))
        self.inventoryButton.draw()
        if self.inventoryButton.isLeftClicked(events):
            self.displayInventory(inBattle)

#Player battle container is not completley related to the player
class PlayerBattle(Player):
    jumpCounter = 0
    gravityCounter = 0
    sprite = loadTile("heart.png", 50, 50)
    def __init__(self, playerMap):
        self.areaNumber = None
        self.x = 700
        self.y = 550
        self.direction = None
        self.goldAmount = playerMap.goldAmount
        self.speed = playerMap.speed - 2
        self.attack = playerMap.attack
        self.remainingHealth = playerMap.remainingHealth  
        self.maxHealth = playerMap.maxHealth
        self.inventory = playerMap.inventory
        self.activeWeapon = playerMap.activeWeapon
        self.activeShield = playerMap.activeShield
        self.addDamage = playerMap.addDamage
        
    def getMovement(self, gravity):
        newX = self.x
        newY = self.y
        for i in range(self.speed):
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                newX += 1
            elif keys[pygame.K_LEFT]:
                newX -= 1
        
            if not gravity:
                if keys[pygame.K_UP]:
                    newY -= 1
                if keys[pygame.K_DOWN]:
                    newY += 1
                if newY >= 100 and newY <= 550:
                    self.y = newY

            if newX >= 300 and newX <= 1050:
                self.x = newX
                
        if gravity:
            #If the character should still be rising
            if self.jumpCounter < 50 and self.jumpCounter != 0:
                self.y -= 4
                self.jumpCounter += 1
            #If character has reached peak
            elif self.jumpCounter == 50:
                self.jumpCounter = 0
            #If character tries to jump
            if keys[pygame.K_UP] and self.y == 550:
                self.jumpCounter = 1
            #If character is in mid air
            if self.y != 550:
                newY = self.y
                for i in range(round(self.gravityCounter**2/7500)):
                    newY += 1
                    if newY == 550:
                        self.gravityCounter = 0
                        break
                self.y = newY
                if newY != 550:
                    self.gravityCounter += 1

    def draw(self):
        display.blit(self.sprite, (self.x, self.y))

#Environmental obstacles 
class Environmental(GameObject, GridRestrictedObject):
    def __init__(self, areaNumber, gridX, gridY):
        GameObject.__init__(self, areaNumber)
        GridRestrictedObject.__init__(self, gridX, gridY)

class Sign(Environmental):
    def __init__(self, areaNumber, gridX, gridY, text):
        Environmental.__init__(self, areaNumber, gridX, gridY)
        self.text = text
    def read(self, player):
        drawTextBoxes(self.text, 1000, WHITE, player.name + " (Reading aloud)")

class Chest(Environmental):
    def __init__(self, areaNumber, gridX, gridY, items, gold):
        Environmental.__init__(self, areaNumber, gridX, gridY)
        self.items = items
        self.gold = gold
    def giveItem(self, player):
        if len(self.items) == 0 :
            drawTextBoxes(["The chest is empty..."], 1000, BEIGE, player.name + " (Shaking your fist)")
        else:
            if(len(player.inventory) == player.maxInventorySize):
                drawTextBoxes(["Your bag is too heavy to take another item"], 1000, BEIGE, player.name + " (Thinking to yourself)")
            else:
                for i in self.items:
                    player.inventory.append(i)
                    drawTextBoxes(["YOU GOT " + i.name + "!"], 1000, BEIGE, player.name + " (Thinking to yourself)")  

            if self.gold != 0:
                player.goldAmount += self.gold
                drawTextBoxes(["The chest had " + str(self.gold) + " gold!"], 1000, BEIGE, player.name + " (Thinking to yourself)")           
                self.gold = 0
            self.items.clear()

#Functions that load different parts of the game
def getMap(areaNumber, areas, folder):
    mapGrid = []
    with open(os.path.join(cwd, folder, areas[areaNumber]), "r") as mapFile:
        for line in mapFile:
            mapGrid.append(list(line.strip("\n")))
    return mapGrid

def getMapSurface(groundGrid, obstacleGrid, givingVillagers, sellingVillagers):
    background = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
    for i in range(30):
        for k in range(40):
            if groundGrid[i+1][k+1] in groundDict.keys():
                background.blit(groundDict[groundGrid[i+1][k+1]], (WIDTH/2 - GRID_WIDTH * SQUARE_SIZE/2 + k*SQUARE_SIZE, GRID_DIST_TOP + i*SQUARE_SIZE))
    for i in range(30):
        for k in range(40):  
            if obstacleGrid[i+1][k+1] in obstacleDict.keys():
                background.blit(obstacleDict[obstacleGrid[i+1][k+1]], (WIDTH/2 - GRID_WIDTH * SQUARE_SIZE/2 + k*SQUARE_SIZE, GRID_DIST_TOP + i*SQUARE_SIZE))
            elif obstacleGrid[i+1][k+1] == "$":
                for villager in sellingVillagers:
                    if villager.gridX == k+1 and villager.gridY == i+1:
                        villagerImage = loadTile("sellingVillager" + str(villager.direction) + ".png", 25, 25)
                        background.blit(villagerImage, (WIDTH/2 - GRID_WIDTH * SQUARE_SIZE/2 + k*SQUARE_SIZE, GRID_DIST_TOP + i*SQUARE_SIZE))
            elif obstacleGrid[i+1][k+1] == "G":
                for villager in givingVillagers:
                    if villager.gridX == k+1 and villager.gridY == i+1:
                        villagerImage = loadTile("givingVillager" + str(villager.direction) + ".png", 25, 25)
                        background.blit(villagerImage, (WIDTH/2 - GRID_WIDTH * SQUARE_SIZE/2 + k*SQUARE_SIZE, GRID_DIST_TOP + i*SQUARE_SIZE))
    return background.convert_alpha()

#Code to load in objects from the files
def loadSigns():
    signs = []
    with open(os.path.join(cwd, "objectFiles", "signs.txt"), "r") as signFile:
        for line in signFile:
            signInfo = line.split(";")
            signs.append(Sign(int(signInfo[0]), int(signInfo[1]), int(signInfo[2]), signInfo[3].split("/")))
    return signs

def loadChests():
    chests = []
    with open(os.path.join(cwd, "objectFiles", "chests.txt"), "r") as chestFile:
        for line in chestFile:
            chestInfo = line.split(";")
            chestItems = []
            
            chestItemNames = chestInfo[3].split("/")
            for i in chestItemNames:
                chestItems.append(createItem(i))

            chests.append(Chest(int(chestInfo[0]), int(chestInfo[1]), int(chestInfo[2]), chestItems, int(chestInfo[4])))
    return chests

def loadSellingVillagers():
    sellingVillagers = []
    with open(os.path.join(cwd, "objectFiles", "sellingVillagers.txt")) as sellingVillagerFile:
        for line in sellingVillagerFile:
            listOfStoreItems = []
            vInfo = line.split(";")
            dialogue = vInfo[5].split("/")
            allStoreItems = vInfo[6].split("/")
            for storeItem in allStoreItems:
                storeItemInfo = storeItem.split(":")
                listOfStoreItems.append(StoreItem(createItem(storeItemInfo[0]), int(storeItemInfo[1]), int(storeItemInfo[2])))
            sellingVillagers.append(SellingVillager(int(vInfo[0]), int(vInfo[1]), int(vInfo[2]), vInfo[3], 0, 0, 0, 0, int(vInfo[4]), dialogue, listOfStoreItems))
    return sellingVillagers

def loadGivingVillagers():
    givingVillagers = []
    with open(os.path.join(cwd, "objectFiles", "givingVillagers.txt")) as givingVillagerFile:
        for line in givingVillagerFile:
            #Gets villager's dialogue
            vInfo = line.split(";")
            dialogue = vInfo[5].split("/")
            #Gets villager's items
            items = []
            for i in vInfo[6].split("/"):
                items.append(createItem(i))
            givingVillagers.append(GivingVillager(int(vInfo[0]), int(vInfo[1]), int(vInfo[2]), vInfo[3], 0, 0, 0, 0, vInfo[4], dialogue, items))
    return givingVillagers

def createItem(itemName):
    #Checks if its a weapon
    with open(os.path.join(cwd, "objectFiles", "weaponTypes.txt")) as weaponFile:
        for line in weaponFile:
            itemInfo = line.split(";")
            if itemInfo[0] == itemName:

                return Weapon(itemInfo[0], itemInfo[1], pygame.image.load(os.path.join(cwd, "art", "weaponArt", itemInfo[2].strip())).convert_alpha(), textToBool(itemInfo[3]))
    #Checks if its a shield
    with open(os.path.join(cwd, "objectFiles", "shieldTypes.txt")) as shieldFile:
        for line in shieldFile:
            itemInfo = line.split(";")
            if itemInfo[0] == itemName:
                return Shield(itemInfo[0], itemInfo[1], pygame.image.load(os.path.join(cwd, "art", "shieldArt", itemInfo[2].strip())).convert_alpha(), textToBool(itemInfo[3]))
    #Checks if its a health potion
    with open(os.path.join(cwd, "objectFiles", "healthPotionTypes.txt")) as healthPotFile:
        for line in healthPotFile:
            itemInfo = line.split(";")
            if itemInfo[0] == itemName:
                return HealthPotion(itemInfo[0], int(itemInfo[1]), pygame.image.load(os.path.join(cwd, "art", "pots", itemInfo[2].strip())).convert_alpha(), textToBool(itemInfo[3]))
    #Checks if it is a strength potion
    with open(os.path.join(cwd, "objectFiles", "strengthPotionTypes.txt")) as strengthPotFile:
        for line in strengthPotFile:
            itemInfo = line.split(";")
            if itemInfo[0] == itemName:
                return StrengthPotion(itemInfo[0], int(itemInfo[1]), pygame.image.load(os.path.join(cwd, "art", "pots", itemInfo[2].strip())).convert_alpha(), textToBool(itemInfo[3]))

def spawnMobs(player, obstacleMap): 
    mobs = []
    excludeX = []
    excludeY = []
    mobChances = spawnChances[player.areaNumber]

    if player.areaNumber == 3 and not bossDefeated:
        mobs.append(Necromancer(3, 700, 300, "Overlord", 500, 500, 20, 10, 3, 5))

    if spawnRates[player.areaNumber] == 0:
        return mobs

    playerLocation = player.getGridPos(player.x, player.y, True)

    for i in range(spawnRates[player.areaNumber]):
        correctSpawn = False
        while(not correctSpawn):
            x = randint(3, GRID_WIDTH - 1)
            y = randint(3, GRID_HEIGHT - 1)
            #Checks if location is an obstacle or the player
            if (obstacleMap[y][x] in moveableSpaces) and playerLocation != (x, y):
                #Checks if location is another mob already
                if not x in excludeX and not y in excludeY:
                    correctSpawn = True
                    excludeX.append(x)
                    excludeY.append(y)
                    mobNumber = randint(1, 100)
                    mobLevel = randint(1, 3)
                    screenPos = getScreenPos(x, y)
                    
                    if mobNumber <= mobChances[0]:
                        mobs.append(Zombie(player.areaNumber, screenPos[0], screenPos[1], "Zombie", 40 + mobLevel*3, 40 + mobLevel*3, 1+mobLevel, 5+mobLevel*2, 3, mobLevel))
                    elif mobNumber > mobChances[1] + mobChances[0] and mobNumber <= mobChances[2] + mobChances[1] + mobChances[0]:
                        mobs.append(Slime(player.areaNumber, screenPos[0], screenPos[1], "Slime", 40 + mobLevel*3, 40 + mobLevel*3, 1+mobLevel, 5+mobLevel*2, 3, mobLevel))
                    else:
                        mobs.append(Book(player.areaNumber, screenPos[0], screenPos[1], "Book", 40 + mobLevel*3, 40 + mobLevel*3, 1+mobLevel, 5+mobLevel*2, 3, mobLevel))
    return mobs

def updateAfterBattle(currentMobBattle, playerBattle, player, victory):
    player.inventory = battlingPlayer.inventory
    player.remainingHealth = battlingPlayer.remainingHealth
    if victory:
        player.goldAmount += currentMobBattle.level * 25
    player.loadHotBar()

########################################################################################################################################
#Initializing player character
player = PlayerMap(7, 275, 700, "Nite", 50, 100, 4, 10, 1, 0, [], None, None, 0)
player.loadHotBar()

#Initializing general map info
areaNumberX = 0
areaNumberY = 2
currGroundMap = getMap(player.areaNumber, groundAreas, "mapAreaGround")
currObstacleMap = getMap(player.areaNumber, obstacleAreas, "mapAreaObstacles")

#Initializing map object info
givingVillagers = loadGivingVillagers()
sellingVillagers = loadSellingVillagers()
chests = loadChests()
signs = loadSigns()
mobs = spawnMobs(player, currObstacleMap)
mobPathCounter = 0

#Initializing map background
background = getMapSurface(currGroundMap, currObstacleMap, givingVillagers, sellingVillagers)

#Initializing battle screen info
currentMobBattle = None
attackButton = Button(100, 700, 300, 60, RED, "ATTACK", BLACK, WHITE)
inventoryButton = Button(500, 700, 400, 60, DARK_BEIGE, "INVENTORY", BLACK, WHITE)
runButton = Button(1000, 700, 300, 60, FOREST_GREEN, "RUN", BLACK, WHITE)
battleSurface = pygame.Surface((WIDTH, HEIGHT))
pygame.draw.rect(battleSurface, WHITE, (300, 100, 800, 500), 3)
#Booleans to tell game state
inStart = True
inMap = False
inBattle = False

inPlay = True
clock = pygame.time.Clock()

while(inPlay):
    eventQueue = pygame.event.get()

    #Closing window leaves game
    checkIfExitGame(eventQueue)
                
    if inStart:
        display.fill(BLACK)
        title = titleFont.render("CRYSTALNITE", 1, WHITE)
        titleRect = title.get_rect(center = (WIDTH/2, 400))
        display.blit(title, titleRect)
        startButton = Button(600, 500, 200, 50, WHITE, "START", BLACK, BEIGE)
        startButton.draw()
        if startButton.isLeftClicked(eventQueue):
            inStart = False
            inMap = True
        pygame.display.update()

    #Death screen
    elif player.remainingHealth <= 0:
        display.fill(BLACK)
        deathMessage = titleFont.render("YOU DIED", 1, DARK_RED)
        deathRect = deathMessage.get_rect(center = (WIDTH/2, HEIGHT/2))
        display.blit(deathMessage, deathRect)
        pygame.display.update()
        pygame.time.wait(1000)
        inMap = True
        inBattle = False
        player.x = 275
        player.y = 700
        player.remainingHealth = player.maxHealth
        player.areaNumber = areaMap[areaNumberY][areaNumberX]
        player.loadHotBar()
        currGroundMap = getMap(player.areaNumber, groundAreas, "mapAreaGround")
        currObstacleMap = getMap(player.areaNumber, obstacleAreas, "mapAreaObstacles")
        background = getMapSurface(currGroundMap, currObstacleMap, givingVillagers, sellingVillagers)
        mobs = spawnMobs(player, currObstacleMap)

    #If player is moving around the map(main game)
    elif inMap:
        mobPathCounter += 1
        display.fill(BLACK)
        display.blit(background, (0, 0))

        #Character movement
        player.getMovement(currObstacleMap, mobs)
        player.draw()

        #Updates all the mobs
        for i, mob in enumerate(mobs):
            mob.draw()
            if mobPathCounter % 30 == 0:
                mob.getPlayerPath(player, currObstacleMap, mobs)
            mob.moveToPlayer(player, currObstacleMap, mobs)
            if mob.isContactEntity(player, mob.x, mob.y):
                #Makes sure boss never respawns
                currentMobBattle = mobs.pop(i)
                inBattle = True
                inMap = False

        #Allows player to use space to interact with objects
        for event in eventQueue:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    isUpdate = player.interactAndUpdate(currObstacleMap, signs, chests, givingVillagers, sellingVillagers)
                    if isUpdate:
                        background = getMapSurface(currGroundMap, currObstacleMap, givingVillagers, sellingVillagers)
                        player.loadHotBar()
                break

        player.drawHotBar(eventQueue, False)

        #Loads in new map area or stays in current one
        loadMapVal = player.goNewArea() 
        if loadMapVal != 0:
            if loadMapVal == 1:
                areaNumberY -= 1
                player.y = GRID_DIST_TOP + GRID_HEIGHT * SQUARE_SIZE - SQUARE_SIZE - 10
            elif loadMapVal == 2:
                areaNumberX += 1
                player.x = WIDTH/2 - GRID_WIDTH*SQUARE_SIZE/2 + 10
            elif loadMapVal == 3:
                areaNumberY += 1
                player.y = GRID_DIST_TOP + 10
            elif loadMapVal == 4 :
                areaNumberX-=1
                player.x = WIDTH/2 + GRID_WIDTH*SQUARE_SIZE/2 - SQUARE_SIZE - 10 
            
            player.areaNumber = areaMap[areaNumberY][areaNumberX]
            currGroundMap = getMap(player.areaNumber, groundAreas, "mapAreaGround")
            currObstacleMap = getMap(player.areaNumber, obstacleAreas, "mapAreaObstacles")
            background = getMapSurface(currGroundMap, currObstacleMap, givingVillagers, sellingVillagers)
            mobs = spawnMobs(player, currObstacleMap)
                
        #Resets mob counter so that it doesnt overflow
        if mobPathCounter == 1000:
                mobPathCounter = 0
        pygame.display.update()

    #Enters the battle screen
    elif inBattle:
        playerMove = True
        battling = True
        
        #Creates a copy of the player that will be the battlescreen
        battlingPlayer = PlayerBattle(player)
        while battling:
            events = pygame.event.get()
            checkIfExitGame(events)

            display.blit(battleSurface, (0, 0))
            battlingPlayer.displayHealthBar(display, 250, 650, 300, WHITE, WHITE)
            battlingPlayer.x = 700
            battlingPlayer.jumpCounter = 0
            battlingPlayer.gravityCounter = 0
            battlingPlayer.y = 550
            currentMobBattle.displayHealthBar(display, 850, 650, 300, WHITE, WHITE)
            attackButton.draw()
            inventoryButton.draw()
            runButton.draw()
            battlingPlayer.draw()

            if playerMove:
                if attackButton.isLeftClicked(events):
                    currentMobBattle.remainingHealth -= battlingPlayer.attack
                    if currentMobBattle.remainingHealth <= 0:
                        battling = False
                        if currentMobBattle.name == "Overlord":
                            bossDefeated = True
                        updateAfterBattle(currentMobBattle, battlingPlayer, player, True)
                        
                    playerMove = False
                elif runButton.isLeftClicked(events):
                    number = randint(1, 100)
                    if number > currentMobBattle.percentRun:
                        battling = False
                        updateAfterBattle(currentMobBattle, battlingPlayer, player, False)
                    else:
                        playerMove = False
                elif inventoryButton.isLeftClicked(events):
                    battlingPlayer.displayInventory(True)
            else:
                projectiles = currentMobBattle.loadProjectiles()
                gravity = False
                if projectiles[0].__class__.__name__  == "ZombieProjectile":
                    gravity = True               
                timer = pygame.time.get_ticks()
                while(not playerMove):
                    events = pygame.event.get()

                    secondsPassed = (pygame.time.get_ticks()-timer)/1000 
                    if secondsPassed > 8 or len(projectiles) == 0:
                        playerMove = True

                    if battlingPlayer.remainingHealth <= 0:
                        battling = False
                        updateAfterBattle(currentMobBattle, battlingPlayer, player, False)
                        break

                    display.blit(battleSurface, (0, 0))
                    battlingPlayer.displayHealthBar(display, 250, 650, 300, WHITE, WHITE)
                    currentMobBattle.displayHealthBar(display, 850, 650, 300, WHITE, WHITE)
                    battlingPlayer.getMovement(gravity)
                    battlingPlayer.draw()

                    for i, projectile in enumerate(projectiles):
                        projectile.draw()
                        if projectile.isContact(battlingPlayer):
                            battlingPlayer.remainingHealth -= currentMobBattle.level * 4
                            projectiles.pop(i)

                        if projectile.finished():
                            projectiles.pop(i)
                        projectile.move()
                    pygame.display.update()

            pygame.display.update()
        
        inBattle = False
        inMap = True

    clock.tick(60)
pygame.quit()
