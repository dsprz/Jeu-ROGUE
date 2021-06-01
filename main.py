import copy
import math
import random
from tkinter import *
from PIL import Image, ImageTk
from playsound import playsound
import threading
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
    def __init__(self, name, hp, hpMax=10, abbrv="", strength=1):
        Element.__init__(self, name, abbrv)
        self.hpMax = hpMax
        self.hp = hp
        self.strength = strength

    def description(self):
        """Description of the creature"""
        return Element.description(self) + "(" + str(self.hp) + ")"

    def meet(self, other):
        """The creature is encountered by an other creature.
            The other one hits the creature. Return True if the creature is dead."""
        self.hp -= other.strength
        theGame().addMessage("The " + other.name + " hits the " +
                             self.description())
        if self.hp > 0:
            return False
        return True


class Hero(Creature):
    """The hero of the game.
        Is a creature. Has an inventory of elements. """
    def __init__(self,
                 name="Hero",
                 hp=10,
                 hpMax=20,
                 abbrv="@",
                 strength=2,
                 xp=0,
                 level=1):
        Creature.__init__(self, name, hp, hpMax, abbrv, strength)
        self.xp = xp
        self.level = level
        self._inventory = []

    def description(self):
        """Description of the hero"""
        return Creature.description(self) + str(self._inventory)

    def fullDescription(self):
        """Complete description of the hero"""
        res = ''
        for e in self.__dict__:
            if e[0] != '_':
                res += '> ' + e + ' : ' + str(self.__dict__[e]) + '\n'
        res += '> INVENTORY : ' + str([x.name for x in self._inventory])
        return res

    def checkEquipment(self, o):
        """Check if o is an Equipment."""
        if not isinstance(o, Equipment):
            raise TypeError('Not a Equipment')

    def take(self, elem):  ### ajoute elem à l'inventaire du héro

        self.checkEquipment(elem)
        self._inventory.append(elem)

    def use(self, elem):
        """Use a piece of equipment"""
        if elem is None:
            return
        self.checkEquipment(elem)
        if elem not in self._inventory:
            raise ValueError('Equipment ' + elem.name + 'not in inventory')
        if elem.use(self):
            self._inventory.remove(elem)


class Equipment(Element):
    """A piece of equipment"""
    def __init__(self, name, abbrv="", usage=None):
        Element.__init__(self, name, abbrv)
        self.usage = usage

    def meet(self, hero):
        """Makes the hero meet an element. The hero takes the element."""
        hero.take(self)
        theGame().addMessage("You pick up a " + self.name)
        return True

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

    def __init__(self, size=20, hero=None):
        self._mat = []
        self._elem = {}
        self._rooms = []
        self._roomsToReach = []

        for i in range(size):
            self._mat.append([Map.empty] * size)
        if hero is None:
            hero = Hero()
        self.hero = hero
        self.generateRooms(10)
        self.reachAllRooms()
        for r in self._rooms:
            r.decorate(self)

        nb = random.randint(1,len(self._rooms)-1)
        b=self._rooms[nb].center()
        self._mat[b.y][b.x]='stairs'

    def dessineSol(self):
        for i in range(len(self._mat)):
            for j in range(len(self._mat[i])):
                if self._mat[i][j] != Map.empty:
                    canvas.create_image(j * 50,
                                        i * 50,
                                        anchor=NW,
                                        image=textures['map']['sol'])
        canvas.pack()

    def dessineMobs(self):
        for i in range(len(self._mat)):
            for j in range(len(self._mat[i])):
                el = self._mat[i][j]
                if isinstance(el, Element):
                    if el.abbrv == "G":
                        canvas.create_image(j * 50,
                                            i * 50,
                                            anchor=NW,
                                            image=textures['mobs']['Gobelin'])

                    if el.abbrv == "D":
                        canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Doge'])
                    
                    if el.abbrv == "H":
                        canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Harvest']),
                    
                    if el.abbrv == "B":
                        canvas.create_image(j*50, i*50, anchor=NW, image = textures['mobs']['Blob']),


        canvas.pack()

    def dessineHero(self):
        for i in range(len(self._mat)):
            for j in range(len(self._mat[i])):
                el = self._mat[i][j]
                if isinstance(el, Hero):
                    canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['Hero'])
        canvas.pack()
    
    def dessineItems(self):

        for i in range(len(self._mat)):
            for j in range(len(self._mat[i])):
                el = self._mat[i][j]
                if isinstance(el, Equipment):
                    if el.abbrv == 'Moon':
                        canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Moonstaff'])

                    if el.abbrv == 'TNT':
                        canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['TNT'])

                    if el.abbrv == "hp":
                        canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Health Pot'])

        canvas.pack()
    
    def dessineStairs(self):

        for i in range(len(self._mat)):
            for j in range(len(self._mat[i])):
                el = self._mat[i][j]
                if el == 'stairs':
                    canvas.create_image(j*50, i*50, anchor = NW, image = textures['map']['stairs'])
                    
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
        """Check if the coordinates c is valid in the map."""
        if not isinstance(c, Coord):
            raise TypeError('Not a Coord')
        if not c in self:
            raise IndexError('Out of map coord')

    def checkElement(self, o):
        """Check if o is an Element."""
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
            if self.get(dest) == Map.ground:
                self._mat[orig.y][orig.x] = Map.ground
                self._mat[dest.y][dest.x] = e
                self._elem[e] = dest
            elif self.get(dest) != Map.empty and self.get(dest).meet(
                    e) and self.get(dest) != self.hero:
                self.rm(dest)

    def moveAllMonsters(
        self
    ):  #### tous les mobs bougent après chaque tour, si un mob est à 1 case du héro, le mob attaque le héro.

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


class Game(object):
    """ Class representing game state """
    """ available equipments """
    equipments = {0: [Equipment("Health pot", "hp", usage=lambda self, hero: heal(hero)), \
                      Equipment("gold", "o")], \
                  1: [Equipment("potion", "!", usage=lambda self, hero: teleport(hero, True))], \
                  2: [Equipment("bow", usage=lambda self, hero: throw(1, True)),
                      Equipment('TNT','TNT', usage =lambda self, hero : throw(1,True))  ], \
                  3: [Equipment("portoloin", "w", usage=lambda self, hero: teleport(hero, False)),Equipment("moonstaff", "Moon")], \
                  }
    """ available monsters """
    monsters = {
        0: [
            Creature("Goblin", 4),
            Creature("Bat", 2, "W"),
            Creature("Harvest", 2),
            Creature("Doge",5)
        ],
        1: [Creature("Ork", 6, strength=2),
            Creature("Blob", 10)],
        5: [Creature("Dragon", 20, strength=3)],
    }

    """ available actions """
    _actions = {'z': lambda h: theGame().floor.move(h, Coord(0, -1)), \
                'q': lambda h: theGame().floor.move(h, Coord(-1, 0)), \
                's': lambda h: theGame().floor.move(h, Coord(0, 1)), \
                'd': lambda h: theGame().floor.move(h, Coord(1, 0)), \
                'i': lambda h: theGame().addMessage(h.fullDescription()), \
                'k': lambda h: h.__setattr__('hp', 0), \
                'u': lambda h: h.use(theGame().select(h._inventory)), \
                ' ': lambda h: None, \
                'h': lambda hero: theGame().addMessage("Actions disponibles : " + str(list(Game._actions.keys()))), \
                'b': lambda hero: theGame().addMessage("I am " + hero.name), \
                }

    def __init__(self, level=1, hero=None):
        self.level = level
        self._message = []
        if hero == None:
            hero = Hero()
        self.hero = hero
        self.floor = None

    def buildFloor(self):  ### initialise le floor à une nouvelle map
        self.floor = Map(hero=self.hero)

    def newFloor(self):  ### Nouvel étage
        self.buildFloor()

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
        return copy.copy(random.choice(l))

    def randEquipment(self):  #### génère un équipement aléatore

        return self.randElement(Game.equipments)

    def randMonster(self):  #### génère un mob aléatoire

        return self.randElement(Game.monsters)

    def select(self, l):  #### permet de sélectionner un item
        print("Choose item> " +
              str([str(l.index(e)) + ": " + e.name for e in l]))
        c = getch()
        if c.isdigit() and int(c) in range(len(l)):
            return l[int(c)]

    def dessineTout(self):
        
        self.floor.dessineSol()
        self.floor.dessineStairs()


        self.floor.dessineMobs()
                
        self.floor.dessineItems()
        self.floor.dessineHero()

    def stillAlive(self):
        if self.hero.hp > 0:
            return True
        return False

    def press(self, event):
        gameOver = Label(window, text='Game Over', font=("Arial 20"))
        event = event.char
        if self.stillAlive():
            if event in Game._actions:
                Game._actions[event](self.hero)
                self.floor.moveAllMonsters()
                self.dessineTout()
                window.update()
                self.continuer(event)
        else:
            gameOver.pack()


    def play(self):
        """Main game loop"""
        self.buildFloor()   

        self.floor.put(self.floor._rooms[0].center(), self.hero)
        self.dessineTout()
        playsound("I:/jeu Poo/musique jeu/ClosingArgumentDGS.mp3", False)
        window.bind('<Any-KeyPress>',self.press)
        self.floor.moveAllMonsters()
        print (self.hero.hp)
    
    def continuer(self,event):
        self.press

def theGame(game=Game()):
    """Game singleton"""
    return game


window = Tk()
window.state("zoomed")

w, h = window.winfo_screenwidth(), window.winfo_screenheight()
debut = Label(text='Bienvenue dans le Rogue', font=('Arial 20'))
canvas = Canvas(window, width=w, height=h, bg='black')

textures = {
    'map': {
        'murs': ImageTk.PhotoImage(Image.open("I:/jeu Poo/images jeu/wall.png")),
        'sol': ImageTk.PhotoImage(Image.open("I:/jeu Poo/images jeu/path.png")),
        'stairs' : ImageTk.PhotoImage(Image.open("I:/jeu Poo/images jeu/stairs.png"))
    },
    'mobs': {
        'Harvest': ImageTk.PhotoImage(Image.open("I:/jeu Poo/images jeu/harvest.png")), #à redim + trans
        'Gobelin': ImageTk.PhotoImage(Image.open("I:/jeu Poo/images jeu/gobelin (1).png")),
        'Doge': ImageTk.PhotoImage(Image.open("I:/jeu Poo/images jeu/doge.png")), # à redim + trans
        'Blob' : ImageTk.PhotoImage(Image.open("I:/jeu Poo/images jeu/blob.png"))# à redim + trans
    },
    'items': {
        'TNT': ImageTk.PhotoImage(Image.open("I:/jeu Poo/images jeu/TNT.png")),
        'Health Pot': ImageTk.PhotoImage(Image.open("I:/jeu Poo/images jeu/healthpot.png")),
        'Rainbow Sword': ImageTk.PhotoImage(Image.open("I:/jeu Poo/images jeu/sword (2).png")),  ### à redim
        'Moonstaff': ImageTk.PhotoImage(Image.open("I:/jeu Poo/images jeu/moonstaff(1).png"))
    },  #### à redim
    'hero': {
        "Hero": ImageTk.PhotoImage(Image.open("I:/jeu Poo/images jeu/monokuma.png"))
    }
}


getch = _find_getch()
window.bind('<KeyPress>',theGame().press)
theGame().play()
window.mainloop()


