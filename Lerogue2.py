import copy
import math
import random
from tkinter import *
from PIL import Image, ImageTk
from playsound import playsound
import winsound
# exceptions


def _find_getch():
    """Single char input, only works only on mac/linux/windows OS terminals"""
    try:
        import termios
    except ImportError:
        # Non-POSIX. Return msvcrt's (Windows') getch.
        import msvcrt
        return lambda: msvcrt.getch().decode('utf-8')
    # POSIX system. Create and return a getch that manipulates the tty.
    import sys
    import tty

    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    return _getch


def sign(x):
    if x > 0:
        return 1
    return -1


class Coord(object):
    """Implementation of a map coordinate"""
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return '<' + str(self.x) + ',' + str(self.y) + '>'

    def __add__(self, other):
        return Coord(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Coord(self.x - other.x, self.y - other.y)

    def distance(self, other):
        """Returns the distance between two coordinates."""
        d = self - other
        return math.sqrt(d.x * d.x + d.y * d.y)

    cos45 = 1 / math.sqrt(2)

    def direction(self, other):
        """Returns the direction between two coordinates."""
        d = self - other
        cos = d.x / self.distance(other)
        if cos > Coord.cos45:
            return Coord(-1, 0)
        elif cos < -Coord.cos45:
            return Coord(1, 0)
        elif d.y > 0:
            return Coord(0, -1)
        return Coord(0, 1)


class Element(object):
    """Base class for game elements. Have a name.
        Abstract class."""
    def __init__(self, name, abbrv=""):
        self.name = name
        if abbrv == "":
            abbrv = name[0]
        self.abbrv = abbrv

    def __repr__(self):
        return self.abbrv

    def description(self):
        """Description of the element"""
        return "<" + self.name + ">"

    def meet(self, hero):
        """Makes the hero meet an element. Not implemented. """
        raise NotImplementedError('Abstract Element')


class Creature(Element):
    """A creature that occupies the dungeon.
        Is an Element. Has hit points and strength."""
    
    def __init__(self, name, hp, hpMax=10, abbrv="", strength=1, xp = 1):
        Element.__init__(self, name, abbrv)
        self.hpMax = hpMax
        self.hp = hp
        self.bonus = 0
        self.strength = strength
        self.xp = xp

    def description(self):
        """Description of the creature"""
        return Element.description(self) + "(" + str(self.hp) + ")"

    def meet(self, other):
        """The creature is encountered by an other creature.
            The other one hits the creature. Return True if the creature is dead."""
        self.hp -= other.strength
        for i in range(len(theGame().floor._mat)):
            for j in theGame().floor._mat[i]:
                if str(j) == 'Metallica':
                    print('oui')
                    for j in theGame().hero._inventory:
                        if isinstance(j, Metal):
                            theGame().hero._inventory.remove(j)
        theGame().addMessage("The " + other.name + " hits the " +
                             self.description())
        if self.hp > 0:
            return False
        return True

class Money(Element):
    def __init__(self,name, abbrv, value = 1):
        Element.__init__(self, name, abbrv)
        self.value = value

    def meet(self,hero):
        hero.takeMoney(self)
        return True
    
    def showMoney(self):
        banque = (str(w) for w in theGame().hero._banque)
        canvasInventaire.create_text(200,700, text = 'Porte-monnaie :', font = 'Arial 20')
        canvasInventaire.create_image(90,740, anchor = NW, image = textures['interface']['money'])
        canvasInventaire.create_text(230,790, text = 'X ' + str(len(theGame().hero._banque)) , font = 'Arial 30')

class Hero(Creature):
    """The hero of the game.
        Is a creature. Has an inventory of elements. """
    def __init__(self,
                 name="Hero",
                 hp=10,
                 hpMax=20,
                 abbrv="@",
                 strength=5,
                 xp=0,
                 lvl=1):
        Creature.__init__(self, name, hp, hpMax, abbrv, strength)
        self.xp = xp
        self.lvl = lvl
        self._inventory = []
        self._banque =[]
        self._bag=[]

    def description(self):
        """Description of the hero"""
        return Creature.description(self) + str(self._inventory)

    def fullDescription(self):
        ""r"Complete description of the hero"""
        res = ''
        for e in self.__dict__:
            if e[0] != '_':
                res += '> ' + e + ' : ' + str(self.__dict__[e]) + '\n'
        res += '> INVENTORY : ' + str([x.name for x in self._inventory])
        return res

    def checkEquipment(self, o):
        ""r"Check if o is an Equipment."""
        if not isinstance(o, Equipment):
            raise TypeError('Not a Equipment')
    
    def checkMoney(self, el):
        if not isinstance(el, Money):
            raise TypeError('This is not money')
        return True

    def take(self, elem):  ### ajoute elem à l'inventaire du héro
    
        self.checkEquipment(elem)
        if len(self._inventory)<10:
            self._inventory.append(elem)
        return True
    
    def takeMoney(self, money):
        if self.checkMoney(money):
            theGame().hero._banque.append(money)
    
    def checkKids(self, kids):
        if not isinstance(kids, Kids):
            raise TypeError('Not a Kid')

    def takeKids(self, kids):
        self.checkKids(kids)
        theGame().hero._bag.append(kids)

    def use(self, elem):
        """Use a piece of equipment"""
        if elem is None:
            return
        self.checkEquipment(elem)
        if elem not in self._inventory:
            raise ValueError('Equipment ' + elem.name + 'not in inventory')
        if elem.use(self):
            self._inventory.remove(elem)
    
    def addXP(self,x) :
        """Add x XP's points to the hero"""
        self.xp += x
    
    def refreshXP(self) :
        """If the XP is big enough, the hero wins one level and gains strength and HP"""
        if self.xp >= (self.lvl+1)**2:
            for i in range(self.lvl,self.lvl+10) :
                if self.xp >= i**2 :
                    self.lvl+=1
                    self.xp = self.xp-(i**2)
                    self.hp = 8 + self.lvl*2
                    self.strength+=2
                    self.hp+=60
                else :
                    break
    
    def dessineXp(self):
        self.refreshXP()
        canvasInventaire.create_text(400,300, text = str(self.xp) + '/' +str((self.lvl+1)**2), font = 'Arial 20')

        canvasInventaire.create_rectangle(100,680,700,650, fill ='black')
        canvasInventaire.create_rectangle(100,680,100+600*(self.xp/((self.lvl+1)**2)),650, fill ='blue')
        canvasInventaire.create_image(650,625, anchor = NW, image = textures['interface']['circle'])
        canvasInventaire.create_text(692,666, text = str(self.lvl), font = 'Arial 20')

        canvasInventaire.create_image(600,600, anchor = NW, image = textures['interface']['Monosuke'])
        canvasInventaire.create_image(480,600, anchor = NW, image = textures['interface']['Monophanie'])
        canvasInventaire.create_image(360,590, anchor = NW, image = textures['interface']['Monotaro'])
        canvasInventaire.create_image(240,600, anchor = NW, image = textures['interface']['Monodam'])
        canvasInventaire.create_image(120,600, anchor = NW, image = textures['interface']['Monokid'])


class Equipment(Element):
    """A piece of equipment"""
    def __init__(self, name, abbrv="", usage=None):
        Element.__init__(self, name, abbrv)
        self.usage = usage

    def meet(self, hero):
        """Makes the hero meet an element. The hero takes the element."""
        if len(theGame().hero._inventory)<10:
            hero.take(self)
            theGame().addMessage("You pick up a " + self.name)
        else:
            theGame().hero._inventory.remove(theGame().hero._inventory[0])
            hero.take(self)
        return True

    def ecritInventaire(self):
        l=100
        inventory = (str(i) for i in theGame().hero._inventory)
        canvasInventaire.create_text(500,700, text = 'Niveau de la map : '+str(theGame().level), font = 'Arial 20')
        if theGame().hero.take:
            canvasInventaire.create_text(200,50, text = 'Inventaire : ', font = 'Arial 20') #### affiche l'inventaire du héros en string
            for j in range(len(theGame().hero._inventory)):
                eq = theGame().hero._inventory[j]
                if eq.abbrv == 'Arrow':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['items']['Arrow'])
                    l+=50
                if eq.abbrv == 'Potion de vie':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['inventaire']['Health Pot'])
                    l+=50
                if eq.abbrv == 'bow':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['inventaire']['Bow'])
                    l+=50
                if eq.abbrv == 'TNT':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['inventaire']['TNT'])
                    l+=50                                    
                if eq.abbrv == 'Moonstaff':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['inventaire']['Moonstaff'])
                    l+=50
                if eq.abbrv == 'Gun':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['inventaire']['Gun'])
                    l+=50        
                if eq.abbrv == 'Rainbow Sword':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['inventaire']['Rainbow Sword'])
                    l+=50         
    def use(self, creature):
        """Uses the piece of equipment. Has effect on the hero according usage.
            Return True if the object is consumed."""
        if self.usage is None:
            theGame().addMessage("The " + self.name + " is not usable")
            return False
        else:
            theGame().addMessage("The " + creature.name + " uses the " +
                                 self.name)
            return self.usage(self, creature)

class Metal(Equipment):
    def __init__(self,name,abbrv = '', usage = None):
        Equipment.__init__(self,name,abbrv)
        pass
    
class Room(object):
    """A rectangular room in the map"""
    def __init__(self, c1, c2):
        self.c1 = c1
        self.c2 = c2

    def __repr__(self):
        return "[" + str(self.c1) + ", " + str(self.c2) + "]"

    def __contains__(self, coord):
        return self.c1.x <= coord.x <= self.c2.x and self.c1.y <= coord.y <= self.c2.y

    def intersect(self, other):
        """Test if the room has an intersection with another room"""
        sc3 = Coord(self.c2.x, self.c1.y)
        sc4 = Coord(self.c1.x, self.c2.y)
        return self.c1 in other or self.c2 in other or sc3 in other or sc4 in other or other.c1 in self

    def center(self):  ### renvoie les coordonnées du centre de la salle

        return Coord((self.c1.x + self.c2.x) // 2,
                     (self.c1.y + self.c2.y) // 2)

    def randCoord(self):  #### return une coordonnée random de la map

        return Coord(random.randint(self.c1.x, self.c2.x),
                     random.randint(self.c1.y, self.c2.y))

    def randEmptyCoord(
            self,
            map):  ##### return une coordonnée random de case vide de la map

        c = self.randCoord()
        while map.get(c) != Map.ground or c == self.center():
            c = self.randCoord()
        return c

    def decorate(
            self,
            map):  #### génère des objets et des mobs aléatoirement dans la map

        map.put(self.randEmptyCoord(map), theGame().randEquipment())
        map.put(self.randEmptyCoord(map), theGame().randMonster())
        map.put(self.randEmptyCoord(map), theGame().randMoney())

class Kids(Element):
    """Kids to pick up"""
    def __init__(self, name, abbrv = " ", hp = 20):
        Element.__init__(self, name, abbrv)
        self.hp = hp
    
    def meet(self,hero):
        hero.takeKids(self)
        self.destroyKids()
        return True
    
    def destroyKids(self):
        if theGame().Monophanie in theGame().hero._bag and theGame().Monosuke in theGame().hero._bag and theGame().Monotaro in theGame().hero._bag and theGame().Monokid in theGame().hero._bag and theGame().Monodam in theGame().hero._bag:
           theGame().hero._bag.clear()
           theGame().hero.hp+=80
           theGame().hero.strength+=5
    


class Map(object):
    """A map of a game floor.
        Contains game elements."""

    ground = '.'  # A walkable ground cell
    dir = {
        'z': Coord(0, -1),
        's': Coord(0, 1),
        'd': Coord(1, 0),
        'q': Coord(-1, 0)
    }  # four direction user keys
    empty = ' '  # A non walkable cell
    stairs = 'stairs'
    chariot = ''
    def __init__(self, size=20, hero=None):
        self._mat = []
        self._elem = {}
        self._rooms = []
        self._roomsToReach = []
        self.dist=3
        for i in range(size):
            self._mat.append([Map.empty] * size)
        if hero is None:
            hero = Hero()
        self.hero = hero
        while len(self._roomsToReach) < 6:
            self.generateRooms(1)
        self.reachAllRooms()
        for r in self._rooms:
            r.decorate(self)

        nb = random.randint(1,len(self._rooms)-1)
        b=self._rooms[nb].center()
        self._mat[b.y][b.x]='stairs'


 


    def dessineSol(self):
        for i in range(len(self._mat)):
            for j in range(len(self._mat[i])):
                if self._mat[i][j] != Map.empty :
                    if self.affiche(Coord(j,i)) :
                        canvas.create_image(j * 50,
                                            i * 50,
                                            anchor=NW,
                                            image=textures['map']['sol'])
                    else:
                        canvas.create_image(j*50, i*50, anchor = NW, image = textures['map']['solFoncé'])
        canvas.pack()
    
    def affiche(self, coord):
        ### renvoie True si on doit dessiner la case
        ###  sinon False
        if self.pos(self.hero).distance(coord) < self.dist :
            return True
        return False

    def dessineMobs(self):
        if 'Silver Chariot' not in str(Game.copieNext):
            Map.chariot = False
        else:
            Map.chariot = True
        for i in range(len(self._mat)):
            for j in range(len(self._mat[i])):
                el = self._mat[i][j]
                if isinstance(el, Element):
                    if self.affiche(Coord(j,i)):
                        if el.abbrv == "G":
                            canvas.create_image(j * 50,
                                                i * 50,
                                                anchor=NW,
                                                image=textures['mobs']['Gobelin'])

                        if el.abbrv == "D":
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Doge'])
                        
                        if el.abbrv == "H":
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Harvest'])
                        
                        if el.abbrv == "B":
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Blob'])
                        
                        if el.abbrv == 'Dragon':
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Dragon'])
                        
                        if el.abbrv == 'Napstablook':
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Napstablook'])

                        if el.abbrv == 'Silver Chariot':
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Silver Chariot Requiem'])
                            Map.chariot = True
                        
                        if el.abbrv == 'Regirust':
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Regirust'])
                        
                        if el.abbrv == 'Unjoy':
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Unjoy'])

                        if el.abbrv == 'WoU' : 
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['WoU'])
                        
                        if el.abbrv == 'Sans':
                            if self.pos(el).direction(self.pos(self.hero)) == Coord(-1,0):
                                canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['sans L'])
                            if self.pos(el).direction(self.pos(self.hero)) == Coord(1,0):
                                canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['sans R'])
                            if self.pos(el).direction(self.pos(self.hero)) == Coord(0,-1):
                                canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['sans U'])
                            if self.pos(el).direction(self.pos(self.hero)) == Coord(0,1):
                                canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['sans D'])
                        
                        if el.abbrv == 'Metallica':
                            canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Metallica'])


                          



    def dessineHero(self):
        for i in range(len(self._mat)):
            for j in range(len(self._mat[i])):
                el = self._mat[i][j]
                if isinstance(el, Hero):
                    if 'Gun' in (str(i) for i in theGame().hero._inventory):
                        canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroCB'])
                    else:
                        canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['Hero'])

    
    def dessineItems(self):

        for i in range(len(self._mat)):
            for j in range(len(self._mat[i])):
                el = self._mat[i][j]
                if isinstance(el, Equipment):
                    if self.affiche(Coord(j,i)):
                        if el.abbrv == 'Moonstaff':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Moonstaff'])

                        if el.abbrv == 'TNT':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['TNT'])

                        if el.abbrv == "Potion de vie":
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Health Pot'])
                        
                        if el.abbrv == 'Arrow':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Arrow'])
                        
                        if el.abbrv == 'Dogecoin':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Dogecoin'])
                        
                        if el.abbrv == 'bow':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Bow'])

                        if el.abbrv == 'Gun':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Gun'])
                        
                        if el.abbrv == 'Rainbow Sword':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Rainbow Sword'])                       



    
    def dessineStairs(self):

        for i in range(len(self._mat)):
            for j in range(len(self._mat[i])):
                if self.affiche(Coord(j,i)):
                    el = self._mat[i][j]
                    if el == 'stairs':
                        canvas.create_image(j*50, i*50, anchor = NW, image = textures['map']['stairs'])
    
    def dessineMoney(self):
        for i in range(len(self._mat)):
            for j in range(len(self._mat[i])):
                el = self._mat[i][j]
                if isinstance(el, Money):
                    if self.affiche(Coord(j,i)):
                        if el.abbrv == 'Dogecoin':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Dogecoin'])
    
    def dessineKids(self):
        for i in range(len(self._mat)):
            for j in range(len(self._mat[i])):
                el = self._mat[i][j]
                if isinstance(el, Kids):
                    if self.affiche(Coord(j,i)):
                        if el.abbrv == 'Monophanie':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['kids']['Monophanie'])
                        if el.abbrv == 'Monosuke' :
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['kids']['Monosuke'])
                        if el.abbrv == 'Monodam' :
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['kids']['Monodam'])
                        if el.abbrv == 'Monotaro' :
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['kids']['Monotaro'])
                        if el.abbrv == 'Monokid' :
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['kids']['Monokid'])
    def addRoom(self, room):
        """Adds a room in the map."""
        self._roomsToReach.append(room)
        for y in range(room.c1.y, room.c2.y + 1):
            for x in range(room.c1.x, room.c2.x + 1):
                self._mat[y][x] = Map.ground

    def findRoom(self, coord):
        """If the coord belongs to a room, returns the room elsewhere returns None"""
        for r in self._roomsToReach:
            if coord in r:
                return r
        return None

    def intersectNone(self, room):
        """Tests if the room shall intersect any room already in the map."""
        for r in self._roomsToReach:
            if room.intersect(r):
                return False
        return True

    def dig(
        self, coord
    ):  ### Transforme n'importe quelle case en Ground. Gère les salles atteintes.
        """Puts a ground cell at the given coord.
            If the coord corresponds to a room, considers the room reached."""
        self._mat[coord.y][coord.x] = Map.ground
        r = self.findRoom(coord)
        if r:
            self._roomsToReach.remove(r)
            self._rooms.append(r)

    def corridor(self, cursor, end):
        """Digs a corridors from the coordinates cursor to the end, first vertically, then horizontally."""
        d = end - cursor
        self.dig(cursor)
        while cursor.y != end.y:
            cursor = cursor + Coord(0, sign(d.y))
            self.dig(cursor)
        while cursor.x != end.x:
            cursor = cursor + Coord(sign(d.x), 0)
            self.dig(cursor)

    def reach(self
              ):  ### Prend 2 rooms random et creuse un couloir entre les deux
        """Makes more rooms reachable.
            Start from one random reached room, and dig a corridor to an unreached room."""
        roomA = random.choice(self._rooms)
        roomB = random.choice(self._roomsToReach)

        self.corridor(roomA.center(), roomB.center())

    def reachAllRooms(self):
        """Makes all rooms reachable.
            Start from the first room, repeats @reach until all rooms are reached."""
        self._rooms.append(self._roomsToReach.pop(0))
        while len(self._roomsToReach) > 0:
            self.reach()

    def randRoom(self):  ### return une room aléatoire
        """A random room to be put on the map."""
        c1 = Coord(random.randint(0,
                                  len(self) - 3),
                   random.randint(0,
                                  len(self) - 3))
        c2 = Coord(min(c1.x + random.randint(3, 8),
                       len(self) - 1),
                   min(c1.y + random.randint(3, 8),
                       len(self) - 1))
        return Room(c1, c2)

    def generateRooms(
            self, n
    ):  ### Génère n rooms aléatoires et les ajoute aux salles à atteindre
        """Generates n random rooms and adds them if non-intersecting."""
        for i in range(n):
            r = self.randRoom()
            if self.intersectNone(r):
                self.addRoom(r)

    def __len__(self):
        return len(self._mat)

    def __contains__(self, item):
        if isinstance(item, Coord):
            return 0 <= item.x < len(self) and 0 <= item.y < len(self)
        return item in self._elem

    def __repr__(self):
        s = ""
        for i in self._mat:
            for j in i:
                s += str(j)
            s += '\n'
        return s

    def checkCoord(self, c):
        ""r"Check if the coordinates c is valid in the map."""
        if not isinstance(c, Coord):
            raise TypeError('Not a Coord')
        if not c in self:
            raise IndexError('Out of map coord')

    def checkElement(self, o):
        ""r"Check if o is an Element."""
        if not isinstance(o, Element):
            raise TypeError('Not a Element')

    def put(self, c, o):

        self.checkCoord(c)
        self.checkElement(o)
        if self._mat[c.y][c.x] != Map.ground:
            raise ValueError('Incorrect cell')
        if o in self._elem:
            raise KeyError('Already placed')
        self._mat[c.y][c.x] = o
        self._elem[o] = c

    def get(self, c):
        self.checkCoord(c)
        return self._mat[c.y][c.x]

    def pos(self, o):

        self.checkElement(o)
        return self._elem[o]

    def rm(self, c):

        self.checkCoord(c)
        del self._elem[self._mat[c.y][c.x]]
        self._mat[c.y][c.x] = Map.ground

    def move(self, e, way):

        orig = self.pos(e)
        dest = orig + way
        if dest in self:
            if self.get(dest) == Map.stairs:
                theGame().newFloor()
            else:
                if self.get(dest) == Map.ground:
                    self._mat[orig.y][orig.x] = Map.ground
                    self._mat[dest.y][dest.x] = e
                    self._elem[e] = dest
                elif self.get(dest) != Map.empty  and self.get(dest).meet(
                        e) and self.get(dest) != self.hero:
                        if isinstance(self.get(dest), Kids):
                            theGame().l.remove(self.get(dest))
                        if isinstance(self.get(dest), Creature):
                            theGame().hero.addXP(self.get(dest).xp)
                        self._mat[orig.y][orig.x] = Map.ground
                        self.rm(dest)
                        self._mat[dest.y][dest.x] = e
                        self._elem[e] = dest




    def moveAllMonsters(
        self
    ):  #### tous les mobs bougent après chaque tour, si un mob est à 1 case du héro sans avoir bougé, le mob attaque le héro.

        h = self.pos(self.hero)
        for e in self._elem:
            c = self.pos(e)
            if isinstance(e,
                          Creature) and e != self.hero and c.distance(h) < 6:
                d = c.direction(h)
                if self.get(c + d) in [Map.ground, self.hero]:
                    self.move(e, d)


def heal(creature):
    """Heal the creature"""
    if creature.hp + 3 >= creature.hpMax:
        creature.hp = creature.hpMax
    else:
        creature.hp += 3
    return True


def teleport(creature, unique):
    """Teleport the creature"""
    r = theGame().floor.randRoom()
    c = r.randCoord()
    while not theGame().floor.get(c) == Map.ground:
        c = r.randCoord()
    theGame().floor.rm(theGame().floor.pos(creature))
    theGame().floor.put(c, creature)
    return unique


class Game(Creature):
    """ Class representing game state """
    """ available equipments """
    copieNext = ''
    equipments = {0: [Equipment("Health pot", "Potion de vie", usage=lambda self, hero: heal(hero)), 
                      Metal("Arrow", "Arrow"),
                      Metal("bow",'bow', usage=lambda self, hero: throw(1, True))], \
                  1: [Equipment("potion", "TPotion", usage=lambda self, hero: teleport(hero, True)),
                      Metal('Gun', 'Gun'),
                      Equipment('Rainbow Sword', 'Rainbow Sword')  ], \
                  2: [
                      Equipment('TNT','TNT', usage =lambda self, hero : throw(1,True))  ], \
                  3: [Equipment("portoloin", "Portoloin", usage=lambda self, hero: teleport(hero, False)),
                      Equipment("moonstaff", "Moonstaff")], \
                  }
    """ available monsters """
    monsters = {
        0: [
            Creature("Goblin", 4, xp=1),
            Creature("Napstablook", 2, abbrv ='Napstablook', xp=1),
            Creature("Harvest", 2, xp=1),
            Creature("Doge",4, xp=1),
            Creature('Sans', 5, abbrv = 'Sans', strength=1, xp = 3 )
            
        ],
        1: [Creature("Ork", 6, strength=2, xp=3),
            Creature("Blob", 5,xp=2)
            ],
         
        6: [Creature("Dragon", 8, abbrv = 'Dragon', strength=3, xp=4)],
        
        8: [Creature('Silver Chariot', 13, strength = 3, abbrv = 'Silver Chariot', xp=5),
            Creature('Regirust', 20, abbrv='Regirust', strength = 1, xp=5),
            Creature('Unjoy',20,abbrv ='Unjoy', strength=2, xp=50)],
        10:[Creature('Wonder Of U', 60, abbrv = 'WoU', strength=8, xp = 110 ),
            Creature('Metallica', 3, abbrv = 'Metallica', strength=5, xp = 1)],
        

    }
    """Escaliers"""
    element = {
        0:
        [
            Element('Stairs', 'stairs'),
        ]
    
    }

    """Monnaie"""
    money = {0:
        [Money('Dogecoin', 'Dogecoin', value = 1)]
        
        }
    """ available actions """
    _actions = {'z': lambda h: theGame().floor.move(h, Coord(0, -1)), \
                'q': lambda h: theGame().floor.move(h, Coord(-1, 0)), \
                's': lambda h: theGame().floor.move(h, Coord(0, 1)), \
                'd': lambda h: theGame().floor.move(h, Coord(1, 0)), \
                'i': lambda h: theGame().addMessage(h.fullDescription()), \
                'k': lambda h: h.__setattr__('hp', 0), \
                'u': lambda h: theGame().selectionnerInventaire(), \
                ' ': lambda h: None, \
                'h': lambda hero: theGame().addMessage("Actions disponibles : " + str(list(Game._actions.keys()))), \
                'b': lambda hero: theGame().addMessage("I am " + hero.name), \
                }



    def __init__(self, level=1, money = Money('Dogecoin', 'Dogecoin'), equipment = None, hero=None):
        self.level = level
        self._message = []
        if equipment is None:
            equipment = Equipment(name = 'Rien')
        if money is None:
            money = Money()
        self.equipment = equipment
        if hero is None:
            hero = Hero()

        self.posInventaire=0
        self.hero = hero
        self.floor = None
        self.hero.hp = 70
        self.money = money
        self.bonus=0
        self.Monokid =  Kids("Monokid","Monokid")
        self.Monosuke = Kids("Monosuke", "Monosuke")
        self.Monotaro = Kids("Monotaro", "Monotaro")
        self.Monophanie = Kids("Monophanie", "Monophanie")
        self.Monodam = Kids ("Monodam", "Monodam")
        
        self.l = [self.Monosuke,self.Monophanie,self.Monotaro,self.Monodam,self.Monokid]

    def buildFloor(self):  ### initialise le floor à une nouvelle map
        self.floor = Map(hero=self.hero)
    
    def newFloor(self):  ### Nouvel étage
        self.bonus+=1
        canvas.delete('all')
        if self.floor.chariot is True: ### si chariot a été dessiné dans la map précédente (map précédente avec mobs tués)
            present = True
        else:            
            present = False
            
        self.hero.hp+=30
        self.level+=1
        self.buildFloor()
        if 'stairs' not in str(self.floor):
            randomRoom = random.randint(1, len(self.floor._mat))
            self.floor._mat[self.floor._rooms[randomRoom].center().y][self.floor._rooms[randomRoom].center().x] = 'stairs'
        
        self.floor._mat[self.floor._rooms[0].center().y][self.floor._rooms[0].center().x] = Map.ground
        self.floor.put(self.floor._rooms[0].center(), self.hero)
        self.putRandomKids()

        Game.copieNext = copy.deepcopy(theGame().floor) ### inchangeable copie de la map non modifiée

        self.dessineTout()
        
        if 'Silver Chariot' in str(self.copieNext) and present == False:   #### si chariot dans la salle et chariot mort de la salle précédente
            winsound.PlaySound(r"musique jeu/chariot.wav", winsound.SND_ASYNC)
                    

                                    ### si chariot n'est pas dans la salle et chariot mort dans la salle précédente    
        if 'Silver Chariot' not in str(self.copieNext) and present == True:
            winsound.PlaySound(r"musique jeu/ClosingArgumentDGS.wav", winsound.SND_ASYNC)  
          
        self.press

    def addMessage(self, msg):  #### ajoute un message à la liste de messages

        self._message.append(msg)

    def readMessages(
            self):  #### lis les messages et clear la liste de messages

        s = ''
        for m in self._message:
            s += m + '. '
        self._message.clear()
        return s

    def randElement(self, collect):  #### génère un élément aléatoire
        """Returns a clone of random element from a collection using exponential random law."""
        x = random.expovariate(1 / self.level)
        for k in collect.keys():
            if k <= x:
                l = collect[k]
        a = copy.copy(random.choice(l))
        if isinstance(a, Creature):
            a.strength += self.bonus 
            a.hp+=self.bonus
            a.xp+=self.bonus/2
        return a
    
    def randEquipment(self):  #### génère un équipement aléatore

        return self.randElement(Game.equipments)

    def randMonster(self):  #### génère un mob aléatoire

        return self.randElement(Game.monsters)
    
    def randMoney(self):
        return self.randElement(Game.money)
    
    def putRandomKids(self):
        if self.l == []:
            self.l = [self.Monosuke,self.Monophanie,self.Monotaro,self.Monodam,self.Monokid]
        rng = random.randint(0,10)
        print (self.l)
        if (rng == 1 or rng == 6) and self.Monosuke in self.l and self.Monosuke not in theGame().hero._bag:
            self.floor.put(self.floor._rooms[random.randint(0,len(self.floor._rooms)-1)].randEmptyCoord(self.floor),self.Monosuke)

        if (rng == 2 or rng == 7) and self.Monophanie in self.l and self.Monophanie not in theGame().hero._bag:          
            self.floor.put(self.floor._rooms[random.randint(0,len(self.floor._rooms)-1)].randEmptyCoord(self.floor),self.Monophanie)

        if (rng == 3 or rng == 8) and self.Monotaro in self.l and self.Monotaro not in theGame().hero._bag :
            self.floor.put(self.floor._rooms[random.randint(0,len(self.floor._rooms)-1)].randEmptyCoord(self.floor),self.Monotaro)

        if (rng == 4 or rng == 9) and self.Monodam in self.l and self.Monodam not in theGame().hero._bag:
            self.floor.put(self.floor._rooms[random.randint(0,len(self.floor._rooms)-1)].randEmptyCoord(self.floor),self.Monodam)

        if (rng == 5 or rng == 10) and self.Monokid in self.l and self.Monokid not in theGame().hero._bag:
            self.floor.put(self.floor._rooms[random.randint(0,len(self.floor._rooms)-1)].randEmptyCoord(self.floor),self.Monokid)
        
         

    def select(self, l):  #### permet de sélectionner un item
        print("Choose item> " +
              str([str(l.index(e)) + ": " + e.name for e in l]))
        c = getch()
        if c.isdigit() and int(c) in range(len(l)):
            return l[int(c)]
    
    def dessineKidsInterface(self):
        for i in theGame().hero._bag:
            if str(i) == 'Monosuke':
                canvasInventaire.create_image(600,600, anchor = NW, image = textures['kids']['Monosuke'])
            if str(i) == 'Monophanie':
                canvasInventaire.create_image(480,600, anchor = NW, image = textures['kids']['Monophanie'])
            if str(i) == 'Monotaro':
                canvasInventaire.create_image(360,590, anchor = NW, image = textures['kids']['Monotaro'])
            if str(i) == 'Monodam':
                canvasInventaire.create_image(240,600, anchor = NW, image = textures['kids']['Monodam'])
            if str(i) == 'Monokid':
                canvasInventaire.create_image(120,600, anchor = NW, image = textures['kids']['Monokid'])

    def dessineVie(self):
        l=50
        canvasVie.delete('all')
        for i in range (self.hero.hp):
            canvasVie.create_image(5,l+50, anchor = NW, image = textures['interface']['vie'])
            l+=25
    def dessineTout(self):
        self.floor.dessineSol()
        self.floor.dessineStairs()
        self.floor.dessineMobs()
        self.floor.dessineKids()
        self.floor.dessineItems()
        self.floor.dessineHero()
        self.floor.dessineMoney()
        self.equipment.ecritInventaire()
        self.money.showMoney()
        self.dessineVie()
        self.hero.dessineXp()
        self.dessineKidsInterface()
    
    def stillAlive(self):
        if self.hero.hp > 0:
            return True
        else : 
            self.gameOver()

    def press(self, event):
        event = event.char
        if self.stillAlive():
            if event in Game._actions:
                Game._actions[event](self.hero)
                self.floor.moveAllMonsters()
                canvasInventaire.delete('all')
                canvas.delete('all')
                self.dessineTout()
                window.update()
     
                self.continuer(event)

    def retry(self):
        gameOver.destroy()
        retry.destroy()
        winsound.PlaySound(None, winsound.SND_PURGE)
        window.bind('<Any-KeyPress>', theGame().press)
        theGame().play()

    def selectionnerInventaire(self):
        canvasSelect.focus_set()
        canvasSelect.delete('all')

        canvasSelect.create_image(0,0, anchor= NW, image = textures['interface']['select'])
        canvasSelect.bind('<Up>', self.goUp)
        canvasSelect.bind('<Down>', self.goDown)


    
    def goUp(self,event):
        canvasSelect.delete('all')
        if self.posInventaire-50 <0 :
            canvasSelect.create_image(0,0, anchor= NW, image = textures['interface']['select'])
            self.posInventaire==0

        else:
            canvasSelect.create_image(0,self.posInventaire-50, anchor= NW, image = textures['interface']['select'])
            self.posInventaire-=50
    
    def goDown(self,event):
        canvasSelect.delete('all')
        if self.posInventaire+50>599:
            canvasSelect.create_image(0,599, anchor= NW, image = textures['interface']['select'])
            self.posInventaire==599
        else:
            canvasSelect.create_image(0,self.posInventaire+50, anchor= NW, image = textures['interface']['select'])
            self.posInventaire+=50

    def play(self):
        """1er étage"""

        cpt=0
        self.buildFloor()
   
        self.floor.put(self.floor._rooms[0].center(), self.hero)
        self.putRandomKids()
        self.dessineTout()
        if 'Silver Chariot' in str(self.floor):  
            winsound.PlaySound(r"musique jeu/chariot.wav", winsound.SND_ASYNC)
            self.floor.chariot = True
        else:
            winsound.PlaySound(r"musique jeu/ClosingArgumentDGS.wav", winsound.SND_ASYNC)
            self.floor.chariot = False

        window.bind('<Any-KeyPress>',self.press)
        self.floor.moveAllMonsters()
    
    def continuer(self,event):
        self.press
    
    def gameOver(self):
        canvasGameOver.create_text(200,200, text = 'GameOver', font = 'Arial 20')
    
def theGame(game=Game()):
    """Game singleton"""
    return game
    


window = Tk()
window.state("zoomed")

w, h = window.winfo_screenwidth(), window.winfo_screenheight()
debut = Label(text='Bienvenue dans le Rogue', font=('Arial 20'))
canvas = Canvas(window, width=w, height=h, bg='black')
gameOver= Label(canvas, text='Game over', font=('Arial 20'))
retry=Button(canvas, text = 'Retry', font =('Arial 20'), command = theGame().retry)

canvasInventaire = Canvas(window, width = w, height = h, bg = '#4C4C4C')
canvasInventaire.place(relx=0.56, rely=0)

canvasVie = Canvas(window, width = 25, height= h, bg = 'yellow')
canvasVie.place(relx=0.55)

canvasSelect = Canvas(window, width = 30, height= 638, bg = 'red' )
canvasSelect.place(relx = 0.59, rely = 0.05)

canvasGameOver = Canvas(window, width = 25, height= h, bg = 'red')


textures = {
    'map': {
        'murs': ImageTk.PhotoImage(Image.open(r"images jeu\wall.png")),
        'sol': ImageTk.PhotoImage(Image.open(r"images jeu\path.png")),
        'solFoncé': ImageTk.PhotoImage(Image.open(r"images jeu\path_black.png")),
        'stairs' : ImageTk.PhotoImage(Image.open(r"images jeu\stairs.png"))
    },
    'mobs': {
        'Harvest': ImageTk.PhotoImage(Image.open(r"images jeu\harvest.png")), #à redim + trans
        'Gobelin': ImageTk.PhotoImage(Image.open(r"images jeu\gobelin (1).png")),
        'Doge': ImageTk.PhotoImage(Image.open(r"images jeu\doge.png")), # à redim + trans
        'Blob' : ImageTk.PhotoImage(Image.open(r"images jeu\blob.png")),# à redim + trans
        'Dragon' : ImageTk.PhotoImage(Image.open(r"images jeu\Dragon.png")),
        'Napstablook' : ImageTk.PhotoImage(Image.open(r"images jeu\napstablook.png")),
        'Silver Chariot Requiem' : ImageTk.PhotoImage(Image.open(r"images jeu\SilverChariotRequiem.png")),
        'Regirust' : ImageTk.PhotoImage(Image.open(r"images jeu\regirust.png")),
        'Unjoy' : ImageTk.PhotoImage(Image.open(r"images jeu\unjoy.png")),
        'WoU' : ImageTk.PhotoImage(Image.open(r"images jeu\WonderOfU.png")),
        'sans L' : ImageTk.PhotoImage(Image.open(r"images jeu\killer sans.png")),
        'sans R' : ImageTk.PhotoImage(Image.open(r"images jeu\killer sans2.png")),
        'sans U' : ImageTk.PhotoImage(Image.open(r"images jeu\killer sansUP.png")),
        'sans D' : ImageTk.PhotoImage(Image.open(r"images jeu\killer sansdown.png")),
        'Metallica' : ImageTk.PhotoImage(Image.open(r"images jeu\Metallica.png"))
    } ,
    'items': {
        'TNT': ImageTk.PhotoImage(Image.open(r"images jeu\TNT.png")),
        'Health Pot': ImageTk.PhotoImage(Image.open(r"images jeu\healthpot.png")),
        'Rainbow Sword': ImageTk.PhotoImage(Image.open(r"images jeu\sword (2).png")),  ### à redim
        'Moonstaff': ImageTk.PhotoImage(Image.open(r"images jeu\moonstaff.png")),
        'Arrow' : ImageTk.PhotoImage(Image.open(r"images jeu\arrow.png")),
        'Dogecoin' : ImageTk.PhotoImage(Image.open(r"images jeu\Dogecoin.png")),
        'Bow' : ImageTk.PhotoImage(Image.open(r"images jeu\Bow.png")),
        'Gun' : ImageTk.PhotoImage(Image.open(r"images jeu\coltPython.png"))
    },  #### à redim
    'hero': {
        "Hero" : ImageTk.PhotoImage(Image.open(r'images jeu\monokuma.png')),
        "HeroCB": ImageTk.PhotoImage(Image.open(r"images jeu\monokumaCowBoy.png"))
    },
    'interface' : 
        {'money' : ImageTk.PhotoImage(Image.open(r"images jeu\dogecoinCanvas.png")),
        'vie' : ImageTk.PhotoImage(Image.open(r"images jeu\heart.png")),
        'select' : ImageTk.PhotoImage(Image.open(r"images jeu\selectArrow.png")),
        'circle' : ImageTk.PhotoImage(Image.open(r"images jeu\circle.png")),
        'Monosuke':ImageTk.PhotoImage(Image.open(r"images jeu\Monosuke test.png")),
        'Monotaro' : ImageTk.PhotoImage(Image.open(r"images jeu\Monotaro opacité.png")),
        'Monophanie' :ImageTk.PhotoImage(Image.open(r"images jeu\Monophanie opacité.png")),
        'Monokid' : ImageTk.PhotoImage(Image.open(r"images jeu\Monokid opacité.png")),
        'Monodam' : ImageTk.PhotoImage(Image.open(r"images jeu\Monodam opacité.png")),
        },
    'inventaire' : {
        'Health Pot': ImageTk.PhotoImage(Image.open(r"images jeu\healthpot.png").resize((50,50))),
        'Bow' : ImageTk.PhotoImage(Image.open(r"images jeu\bowInventaire.png")),
        'TNT' : ImageTk.PhotoImage(Image.open(r"images jeu\TNT.png").resize((50,75))),
        'Moonstaff' : ImageTk.PhotoImage(Image.open(r"images jeu\moonstaff.png").resize((50,75))),
        'Gun' : ImageTk.PhotoImage(Image.open(r"images jeu\coltPython.png").resize((72,72))),
        'Rainbow Sword': ImageTk.PhotoImage(Image.open(r"images jeu\sword (2).png")),  


    },
    'kids' :{
        'Monophanie' : ImageTk.PhotoImage(Image.open(r"images jeu\Monophanie.png")),
        'Monosuke' : ImageTk.PhotoImage(Image.open(r"images jeu\Monosuke.png")),
        'Monodam' : ImageTk.PhotoImage(Image.open(r"images jeu\Monodam.png")),
        'Monotaro' : ImageTk.PhotoImage(Image.open(r"images jeu\Monotaro.png")),
        'Monokid' : ImageTk.PhotoImage(Image.open(r"images jeu\Monokid.png"))
    }
}


getch = _find_getch()
window.bind('<KeyPress>',theGame().press)
theGame().play()
window.mainloop()
