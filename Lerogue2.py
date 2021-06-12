#from Lerogue import theGame
from abc import ABCMeta, abstractmethod
import copy
import math
import random
from tkinter import *
from abc import ABC
from playsound import playsound
from PIL import Image, ImageTk
import winsound
# exceptions

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


class Element(metaclass = ABCMeta):
    """Base class for game elements. Have a name."""
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

class Equipment(Element):
    """A piece of equipment"""
    def __init__(self, name, abbrv="", usage=None):
        Element.__init__(self, name, abbrv)
        self.usage = usage

    def meet(self, hero):
        """Makes the hero meet an element. The hero takes the element."""
        if len(theGame().hero._inventory)<5:
            hero.take(self)
            theGame().addMessage("You pick up a " + self.name)
        return True
    
    def use(self, creature):
        """Uses the piece of equipment. Has effect on the hero according usage.
            Return True if the object is consumed."""
        if self.usage is None:
            if isinstance(creature, Hero):
                theGame().addMessage("The " + self.name + " is not usable")
                return False
            else:
                creature.hp-=50
        else:
            theGame().addMessage('The Hero uses ' + self.name)
            return self.usage(self, creature)

class Food(Equipment):
    """Food"""
    def __init__(self, name, abbrv = '', usage = None):
        Equipment.__init__(self, name, abbrv, usage)
    
    def use(self, creature):
        theGame().addMessage('You consumed the ' + self.name)
        return self.usage(self, creature)

class MegaMetal(metaclass=ABCMeta):
    def __init__(self, name, abbrv =''):
        Equipment.__init__(self,name,abbrv)

class Metal(MegaMetal,Equipment):
    """Metal"""
    def __init__(self,name,abbrv = '', attack = 0, usage = None):
        Equipment.__init__(self,name,abbrv)
        self.usage = usage
        self.attack = attack
    
    def use(self, creature):
        """Uses the piece of equipment. Has effect on the hero according usage.
            Return True if the object is consumed."""
        theGame().addMessage("The " + creature.name + " uses the " + self.name)
        return self.usage(self, creature)
        

class Projectile(Element):
    """Projectiles used for guns"""
    def __init__(self,name,abbrv = '', usage = None):
        self.name = name
        self.abbrv = abbrv
        
    
    def meet(self,hero):
        hero.takeProjectile(self)
        theGame().addMessage("You pick up a " + self.name)
        return True
    
    def dessineProjectilesInventaire(self):
        cptBee = 0
        cptArrow = 0
        stock = (str(i) for i in theGame().hero._stock)
        for j in stock:
            if j == 'Bee':
                cptBee+=1
            if j == 'Arrow':
                cptArrow+=1
        canvasInventaire.create_image(320,760, anchor = NW, image = textures['items']['Arrow'])
        canvasInventaire.create_text(430,790, text = 'X ' + str(cptArrow) , font = 'Arial 30') 
        canvasInventaire.create_image(520,760, anchor = NW, image = textures['items']['Bee'])
        canvasInventaire.create_text(630,790, text = 'X ' + str(cptBee) , font = 'Arial 30') 


class MetallicProjectile(MegaMetal,Projectile):
    """Projectiles but metallic"""
    def __init__(self,name,abbrv = '', dmg = 20,usage = None):
            Projectile.__init__(self,name,abbrv)
            self.dmg = dmg
            
class Sword(Equipment):
    """Swords"""
    def __init__(self, name, abbrv= '',attack = 10, usage = None):
        Equipment.__init__(self, name, abbrv, usage)
        self.attack = attack
        self.usage = usage
    
    def use(self, creature):
        theGame().addMessage('You equipped ' + self.name + '. Strength +' +  str(self.attack))
        return self.usage(self,creature)
    
    def dessineEquippedSword(self):
        canvasInventaire.create_image(495,170, anchor = NW, image = textures['interface']['Strength'])
        canvasInventaire.create_text(535,180, text = str(theGame().hero.strength), font = "Arial 12", fill = 'red')
        for i in theGame().hero.sword:
            if i.abbrv == 'Rainbow Sword':
                canvasInventaire.create_image(500,100, anchor = NW, image = textures['items']['Rainbow Sword'])
            if i.abbrv == 'Katana':
                canvasInventaire.create_image(500,100, anchor = NW, image = textures['items']['Katana'])
            if i.abbrv == 'Gun':
                canvasInventaire.create_image(500,100, anchor = NW, image = textures['items']['Gun'])

class Armor(Equipment):
    """Armors"""
    def __init__(self,name, abbrv = '', armor = 10,usage = None):
        Equipment.__init__(self, name, abbrv, usage)
        self.usage = usage
        self.armor = armor
    
    def use(self, creature):
        theGame().addMessage('You equipped ' + self.name + '. Armor +' +  str(self.armor))
        return self.usage(self,creature)
    
    def dessineEquippedArmor(self):
        canvasInventaire.create_image(588,168, anchor = NW, image = textures['interface']['Shield'])
        canvasInventaire.create_text(625,180, text = str(theGame().hero.protection), font = "Arial 12", fill = 'red')
        for i in theGame().hero.armor:
            if i.abbrv == 'Blue Armor':
                canvasInventaire.create_image(580,95, anchor = NW, image = textures['items']['Blue Armor'])
            
            if i.abbrv == 'Iron Armor':
                canvasInventaire.create_image(595,105, anchor = NW, image = textures['items']['Iron Armor'])

class Creature(Element):
    """A creature that occupies the dungeon.
        Is an Element. Has hit points and strength."""
    
    def __init__(self, name, hp, hpMax=10, abbrv="", strength=1, xp = 1, on=None):
        Element.__init__(self, name, abbrv)
        self.hpMax = hpMax
        self.hp = hp
        self.bonus = 0
        self.strength = strength
        self.xp = xp
        self.on = on

    def description(self):
        """Description of the creature"""
        return Element.description(self) + "(" + str(self.hp) + ")"

    def meet(self, other):
        """The creature is encountered by an other creature.
            The other one hits the creature. Return True if the creature is dead."""
        if isinstance(self, Hero):
            if theGame().hero.protection > other.strength:
                self.hp-=1
            else:
                self.hp -= other.strength - theGame().hero.protection
        else:
            self.hp -= other.strength
        
        if str(other.abbrv) == 'Metallica':
            for j in theGame().hero._inventory:
                if isinstance(j, MegaMetal):
                    theGame().hero._inventory.remove(j)
            theGame().addEffect("Metallica destroyed your metallic stuff !\n" )
            for i in theGame().hero._stock:
                if isinstance(i, MegaMetal):
                    theGame().hero._stock.remove(i)
            theGame().addEffect("Metallica destroyed your metallic ammos !")
        
        theGame().addMessage("The " + other.name + " hits the " + self.name)
        if self.hp > 0:
            return False
        return True
    
    def use(self, elem):
        """Uses the piece of equipment. Has effect on the hero according usage.
            Return True if the object is consumed."""
        if elem.usage is None:
            self.hp-=10
            return False
        else:
            elem.use(self)

class Money(Element):
    """Money"""
    def __init__(self,name, abbrv, value = 1):
        Element.__init__(self, name, abbrv)
        self.value = value

    def meet(self,hero):
        hero.takeMoney(self)
        return True
    
    def showMoney(self):
        canvasInventaire.create_image(90,740, anchor = NW, image = textures['interface']['money'])
        canvasInventaire.create_text(230,790, text = 'X ' + str(len(theGame().hero._banque)) , font = 'Arial 30')

class Hero(Creature):
    """The hero of the game.
        Is a creature. Has an inventory of elements. """
    def __init__(self,
                 on = None,
                 name="Hero",
                 hp=10,
                 hpMax=70,
                 abbrv="@",
                 strength=5,
                 protection = 0,
                 xp=0,
                 lvl=1):
        Creature.__init__(self, name, hp, hpMax, abbrv, strength, on)
        self.hunger = 100
        self.starve = 2
        self.faim = 0
        self.kill = 0
        self.protection = protection
        self.xp = xp
        self.lvl = lvl
        self._inventory = []
        self._banque =[]
        self._bag=[]
        self._stock = []
        self.sword = [] ### liste de longueur 1 max
        self.armor = [] ### liste de longueur 1 max
        self.poison = 0
        self.poisoned = False
        self.invisible = None
        self.equipped = False
        self.armored = False
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
    
    def checkProjectile(self,el):
        if not isinstance(el, Projectile):
            raise TypeError('Not a projectile')

    def takeKids(self, kids):
        self.checkKids(kids)
        theGame().hero._bag.append(kids)
        theGame().addMessage('You picked up ' + str(kids))
    
    def takeProjectile(self, el):
        self.checkProjectile(el)
        theGame().hero._stock.append(el)

    def use(self, elem):
        """Use a piece of equipment"""
        self.checkEquipment(elem)
        if elem not in self._inventory:
            raise ValueError('Equipment ' + elem.name + 'not in inventory')
        if elem.use(self):
            if isinstance(elem, Metal) or isinstance(elem, Sword) or isinstance(elem, Armor):
                if isinstance(elem, Sword) or isinstance(elem, Metal):
                    theGame().addMessage('You gained ' + str(elem.attack) + 'strength')
                    self.sword.append(elem)
                if isinstance(elem, Armor):
                    theGame().addMessage('You gained ' + str(elem.armor) + 'armor')
                    self.armor.append(elem)
            self._inventory.remove(elem)
            if self.on != None :
                self.take(self.on[0])
                self.on = None
    
    def addXP(self,x) :
        """Add x XP's points to the hero"""
        self.xp += x
    
    def refreshXP(self) :
        """If the XP is big enough, the hero wins one level and gains strength and HP"""
        if self.xp >= (self.lvl+1)**2:
            for i in range(self.lvl,self.lvl+10) :
                if self.xp >= i**2 :
                    self.lvl+=1
                    self.xp -= i**2
                    self.hp += 5 
                    self.strength+=2 + math.floor(self.lvl/7)
                    self.hpMax += 5
                    if self.lvl%4==0:
                        self.protection += 1  
                else :
                    break
    
    def dessineXp(self):
        self.refreshXP()
        canvasInventaire.create_text(180,700, text = 'XP', font = 'Arial 20')

        canvasInventaire.create_rectangle(100,680,700,650, fill ='black')
        canvasInventaire.create_rectangle(100,680,100+600*(self.xp/((self.lvl+1)**2)),650, fill ='cyan')
        canvasInventaire.create_image(650,625, anchor = NW, image = textures['interface']['circle'])
        canvasInventaire.create_text(692,666, text = str(self.lvl), font = 'Arial 20')

        canvasInventaire.create_image(600,600, anchor = NW, image = textures['interface']['Monosuke'])
        canvasInventaire.create_image(480,600, anchor = NW, image = textures['interface']['Monophanie'])
        canvasInventaire.create_image(360,590, anchor = NW, image = textures['interface']['Monotaro'])
        canvasInventaire.create_image(240,600, anchor = NW, image = textures['interface']['Monodam'])
        canvasInventaire.create_image(120,600, anchor = NW, image = textures['interface']['Monokid'])


    def ecritInventaire(self):
        l=50
        if theGame().level<8:
            canvasInventaire.create_text(500,700, text = "Gangsta's Paradise: "+str(theGame().level), font = 'Arial 20')
        elif 8<=theGame().level<13:
            canvasInventaire.create_text(500,700, text = 'Earth, Wind & Fire: '+str(theGame().level), font = 'Arial 20')
        elif theGame().level>=13:
            canvasInventaire.create_text(500,700, text = 'Highway to Hell: '+str(theGame().level), font = 'Arial 20')

        canvasInventaire.create_image(430,280, anchor = NW, image = textures['interface']['WoU opacité'])
        if theGame().hero.take:
            canvasInventaire.create_text(200,50, text = 'Inventaire : ', font = 'Arial 20') #### affiche l'inventaire du héros en string
            for j in range(len(theGame().hero._inventory)):
                eq = theGame().hero._inventory[j]
                if eq.abbrv == 'Arrow':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['items']['Arrow'])
                    l+=100
                if eq.abbrv == 'Potion de vie':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['inventaire']['Health Pot'])
                    l+=100
                if eq.abbrv == "Potion d'invisibilité":
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['items']['Invisible pot'])
                    l+=100
                if eq.abbrv == 'bow':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['inventaire']['Bow'])
                    l+=100
                if eq.abbrv == 'TNT':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['inventaire']['TNT'])
                    l+=100                                    
                if eq.abbrv == 'Moonstaff':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['inventaire']['Moonstaff'])
                    l+=100
                if eq.abbrv == 'Gun':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['inventaire']['Gun'])
                    l+=100       
                if eq.abbrv == 'Rainbow Sword':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['inventaire']['Rainbow Sword'])
                    l+=100      
                if eq.abbrv == 'Apple':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['items']['Apple'])
                    l+=100      
                if eq.abbrv == 'Pizza':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['items']['Pizza'])
                    l+=100
                
                if eq.abbrv == 'Katana':
                    canvasInventaire.create_image(150,l, anchor = NW, image = textures['items']['Katana'])
                    l+=100
                
                if eq.abbrv == 'Blue Armor':
                    canvasInventaire.create_image(140,l-20, anchor = NW, image = textures['items']['Blue Armor'])
                    l+=100

                if eq.abbrv == 'Iron Armor':
                    canvasInventaire.create_image(140,l-20, anchor = NW, image = textures['items']['Iron Armor'])
                    l+=100
                
                if eq.abbrv == 'Chicken' :
                    canvasInventaire.create_image(140,l, anchor = NW, image = textures['items']['Chicken'])
                    l+=100
    
    def unequipped(self):
        if len(self._inventory) < 5:
            self._inventory.append(self.sword[0])
        self.strength-=self.sword[0].attack
        theGame().addMessage('You lost ' + str(self.sword[0].attack))
        self.sword.remove(self.sword[0])
        self.equipped = False 
    
    def unequippedArmor(self):
        if len(self._inventory) < 5:
            self._inventory.append(self.armor[0])
        self.protection-=self.armor[0].armor
        theGame().addMessage('You lost ' + str(self.armor[0].armor))
        self.armor.remove(self.armor[0])
        self.armored = False 

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
        map.put(self.randEmptyCoord(map), theGame().randAmmo())

class Kids(Element):
    """Kids to pick up"""
    def __init__(self, name, abbrv = " "):
        Element.__init__(self, name, abbrv)
    
    def meet(self,hero):
        hero.takeKids(self)
        self.destroyKids()
        return True
    
    def destroyKids(self):
        if theGame().Monophanie in theGame().hero._bag and theGame().Monosuke in theGame().hero._bag and theGame().Monotaro in theGame().hero._bag and theGame().Monokid in theGame().hero._bag and theGame().Monodam in theGame().hero._bag:
           theGame().hero._bag.clear()
           theGame().hero.hp+=50
           theGame().hero.strength+=5
           theGame().hero.protection+=2
           theGame().floor.dist = 4
    


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
    WoU = ''
    def __init__(self, size=20, hero=None):
        self.size = size
        self._mat = []
        self._elem = {}
        self._rooms = []
        self._roomsToReach = []
        self.dist=3
        self.change = False
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
        
        if 'WoU' not in str(Game.copieNext):
            Map.WoU = False
        else:
            Map.WoU = True

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
                            # dessine rectangle

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
                            Map.WoU = True
                        
                        if el.abbrv == 'Sans': ### peut regarder dans les 4 directions en fonction de la position du héro
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
                    if theGame().hero.invisible != None :
                        if 'Gun' in (str(i) for i in theGame().hero.sword):
                            if 'Iron Armor' in (str(i) for i in theGame().hero.armor):
                                canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroIronArmorCowBoyInvisible'])
                            else:
                                canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroCBInvisible'])

                        elif 'Rainbow Sword' in (str(i) for i in theGame().hero.sword):
                            if 'Iron Armor' in (str(i) for i in theGame().hero.armor):
                                canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroIronArmorRainbowSwordInvisible'])
                            else:
                                canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroSwordInvisible'])
                        elif 'Katana' in (str(i) for i in theGame().hero.sword):
                            if 'Iron Armor' in (str(i) for i in theGame().hero.armor):
                                canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroIronArmorKatanaInvisible'])
                            elif 'Blue Armor' in (str(i) for i in theGame().hero.armor):
                                canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroBlueArmorKatanaInvisible'])                            
                            else:
                                canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroKatanaInvisible'])
                        
                        elif 'Iron Armor' in (str(i) for i in theGame().hero.armor):
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroIronArmorInvisible'])
                        
                        elif 'Blue Armor' in (str(i) for i in theGame().hero.armor):
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroBlueArmorInvisible'])
                        else:
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroInv'])

                    elif 'Rainbow Sword' in (str(i) for i in theGame().hero.sword):
                        if 'Iron Armor' in (str(i) for i in theGame().hero.armor):
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroIronArmorRainbowSword'])
                        elif 'Blue Armor' in (str(i) for i in theGame().hero.armor):
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroBlueArmorRainbowSword'])
                        else:
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroSword'])

                    elif 'Katana' in (str(i) for i in theGame().hero.sword):
                        if 'Iron Armor' in (str(i) for i in theGame().hero.armor):
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroIronArmorKatana'])
                        elif 'Blue Armor' in (str(i) for i in theGame().hero.armor):
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroBlueArmorKatana'])
                        else:
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroKatana'])

                    elif 'Gun' in (str(i) for i in theGame().hero.sword):
                        if 'Iron Armor' in (str(i) for i in theGame().hero.armor):
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroIronArmorCowBoy'])
                        else:
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroCB'])
                    
                    elif 'Iron Armor' in (str(i) for i in theGame().hero.armor):
                        canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroIronArmor'])
                    
                    elif 'Blue Armor' in (str(i) for i in theGame().hero.armor):
                        canvas.create_image(j*50, i*50, anchor = NW, image = textures['hero']['HeroBlueArmor'])
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

                        if el.abbrv == "Potion d'invisibilité":
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Invisible pot'])
                        
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

                        if el.abbrv == 'Apple':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Apple'])       

                        if el.abbrv == 'Pizza':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Pizza'])

                        if el.abbrv == 'Katana':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Katana'])
                    
                        if el.abbrv == 'Blue Armor':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Blue Armor'])
                       
                        if el.abbrv == 'Iron Armor':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Iron Armor'])
                        
                        if el.abbrv == 'Chicken':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Chicken'])
                           

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
    
    def dessineProjectiles(self):
        for i in range(len(self._mat)):
            for j in range(len(self._mat[i])):
                el = self._mat[i][j]
                if isinstance(el, Projectile):
                    if self.affiche(Coord(j,i)):
                        if el.abbrv == 'Arrow':
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Arrow'])
                        if el.abbrv == 'Bee' :
                            canvas.create_image(j*50, i*50, anchor = NW, image = textures['items']['Bee'])
    
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

    def dig(self, coord):  ### Transforme n'importe quelle case en Ground. Gère les salles atteintes.
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
                    if e.on != None :
                        
                        self._mat[e.on[1].y][e.on[1].x] = e.on[0]
                        e.on = None
                    else :
                        self._mat[orig.y][orig.x] = Map.ground
                    self._mat[dest.y][dest.x] = e
                    self._elem[e] = dest
                elif self.get(dest) != Map.empty and isinstance(self.get(dest), Equipment) and len(self.hero._inventory) == 5 :
                    if e.on != None :
                        
                        self._mat[orig.y][orig.x] = e.on[0]
                        e.on = None
                    else :
                        self._mat[orig.y][orig.x] = Map.ground
                        
                    e.on = [self._mat[dest.y][dest.x], dest]

                    self._mat[dest.y][dest.x] = e
                    self._elem[e] = dest
                    

                elif self.get(dest) != Map.empty  and self.get(dest).meet(
                        e) and self.get(dest) != self.hero:
                        
                        if isinstance(self.get(dest), Kids):
                            theGame().l.remove(self.get(dest))
                        if isinstance(self.get(dest), Creature):
                            theGame().hero.kill+=1
                            theGame().hero.addXP(self.get(dest).xp)
                        if e.on != None :
                            self._mat[orig.y][orig.x] = e.on[0]
                            e.on = None
                        else :
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
                if e.abbrv == 'Sans': ### gagne de l'attaque à chaque mob tué
                    e.strength=theGame().hero.kill
                    e.xp+=theGame().bonus
                    if theGame().hero.kill%2==0:  ### gagne de la vie pour chaque 2 monstres tués
                        e.hp=theGame().hero.kill
                    e.xp+=theGame().bonus
                    self.change = False
                if e.abbrv=='WoU':
                    if self.get(c + d) in [Map.ground, Map.empty, self.hero]:
                        self.move(e, d)
                else:
                    if self.get(c + d) in [Map.ground, self.hero]:
                        self.move(e, d)            
            

def makeInvisible(creature) :
    if creature == theGame().hero:

        theGame().hero.invisible = 20
    else:
        creature.hp-=10
    return True

def makeVisible(creature) :
    creature.invisible = None

def heal(creature, satiety = 0):
    """Heal the creature"""
    if 'WoU' in str(theGame().floor):
        return False
    if creature.hp + 30 >= creature.hpMax:
        creature.hp = creature.hpMax
    else:
        creature.hp += 30
    if isinstance(creature, Hero):
        theGame().hero.hunger+=satiety
    return True

def nourrir(creature,qte, name = '') :
    if name == 'Chicken':
        creature.strength +=1
    if isinstance(creature, Hero) :
        if (creature.hunger + qte) > 100 :
            creature.hunger = 100
        else :
            creature.hunger += qte
    else:
        creature.hp+=30
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

def equip(creature,attack):
    """ equip the hero with a weapon"""
    if creature == theGame().hero:
        theGame().hero.equipped = True 
        if len(theGame().hero.sword) == 0:
            theGame().hero.strength+=attack
        
        elif len(theGame().hero.sword) != 0 and len(theGame().hero._inventory) < 5:
            theGame().hero.strength-=theGame().hero.sword[0].attack
            theGame().hero.strength+=attack
            theGame().hero._inventory.append(theGame().hero.sword[0])
            theGame().hero.sword.remove(theGame().hero.sword[0])
        
        elif len(theGame().hero.sword) != 0 and len(theGame().hero._inventory) >=5:
            theGame().hero.sword.remove(theGame().hero.sword[0])
    
    else:
        creature.hp-=50
        if creature.hp<0:
            theGame().hero.addXP(theGame().floor.get(theGame().floor.pos(creature)).xp)
            theGame().floor.rm(theGame().floor.pos(creature))
    return True

def equipArmor(creature, armor):
    if creature == theGame().hero:
        theGame().hero.armored = True
        if len(theGame().hero.armor) == 0:
            theGame().hero.protection+=armor
        
        elif len(theGame().hero.armor) != 0 and len(theGame().hero._inventory) < 5:
            theGame().hero._inventory.append(theGame().hero.armor[0])
            theGame().hero.armor.remove(theGame().hero.armor[0])

        elif len(theGame().hero.sword) != 0 and len(theGame().hero._inventory) >=5:
            theGame().hero.armor.remove(theGame().hero.armor[0]) 
    
    else:
        creature.hp-=50
        if creature.hp<0:
            theGame().hero.addXP(theGame().floor.get(theGame().floor.pos(creature)).xp)
            theGame().floor.rm(theGame().floor.pos(creature))
    return True 

def throw(creature,dmg):
    creature.hp-=dmg
    if creature.hp<0:
        theGame().hero.addXP(theGame().floor.get(theGame().floor.pos(creature)).xp)
        theGame().floor.rm(theGame().floor.pos(creature))

    return True

class Game(object):
    """ Class representing game state """
    """ available equipments """
    copieNext = ''
    equipments = {0: [Food("Health pot", "Potion de vie", usage=lambda self, creature: heal(creature,20)),
                      Food("Invisible pot", "Potion d'invisibilité", usage=lambda self, creature: makeInvisible(creature)),
                      MetallicProjectile("Arrow", "Arrow"),
                      MetallicProjectile("Bee Gees", "Bee"),
                      Metal("Bow",'bow', usage=lambda self,creature: equip(creature,20)),
                      Food("Apple", "Apple", usage=lambda self, creature: nourrir(creature, 30)),
                      Armor('Iron Armor', 'Iron Armor', usage = lambda self, creature : equipArmor(creature,10)) ], \
                  1: [
                      Metal('Gun', 'Gun', attack = 0,usage =lambda self, creature : equip(creature, 0)),
                    Metal('Gun', 'Gun', attack = 0,usage =lambda self, creature : equip(creature, 0)),
                      Metal('Gun', 'Gun', attack = 0,usage =lambda self, creature : equip(creature, 0)),
                      Metal('Gun', 'Gun', attack = 0,usage =lambda self, creature : equip(creature, 0)),
                      Metal('Gun', 'Gun', attack = 0,usage =lambda self, creature : equip(creature, 0)),

                      Food('Pizza', 'Pizza', usage=lambda self, creature: nourrir(creature, 50)),
                      Sword("Catch the Rainbow", abbrv = "Rainbow Sword", attack = 12, usage =lambda self, creature : equip(creature,12)),
                      Sword('Katana', 'Katana', attack = 10, usage =lambda self, creature : equip(creature,10)),
                       ], \
                  2: [
                      Equipment('TNT','TNT', usage =lambda self, creature : throw(creature,70))  ], \
                  3: [
                      Equipment("Moonstaff", "Moonstaff", usage =lambda self, creature : throw(creature,10)),
                      Armor('Blue Armor', 'Blue Armor', usage = lambda self, creature : equipArmor(creature,12)) ],
                  7: [Food('The Chicken', 'Chicken', usage = lambda self, creature : nourrir(creature, 75, name = 'Chicken'))]
                  }
    munitions = {0 :[MetallicProjectile("Bee Gees", "Bee"),
                    MetallicProjectile("Bee Gees", "Bee"),
                    MetallicProjectile("Bee Gees", "Bee"),
                    MetallicProjectile("Bee Gees", "Bee"),
                    MetallicProjectile("Bee Gees", "Bee"),
                    MetallicProjectile("Bee Gees", "Bee"),
                 ]
}
    """ available monsters """
    monsters = {
        0: [
            Creature("Goblin", 4, xp=1),
            Creature("Napstablook", 2, abbrv ='Napstablook', xp=1),
            Creature("Harvest", 2, xp=1),
            Creature("Doge",4, xp=1),
        ],
        1: [Creature("Blob", 10,xp=2)
            ],
         
        6: [Creature("Dragon", 8, abbrv = 'Dragon', strength=3, xp=4)],
        
        8: [Creature('Regirust', 20, abbrv='Regirust', strength = 1, xp=5),
            Creature('Unjoy',20,abbrv ='Unjoy', strength=2, xp=50)],
        
        9:[Creature('Silver Chariot', 20, strength = 6, abbrv = 'Silver Chariot', xp=55)],
        
        10:[Creature('Wonder Of U', 60, abbrv = 'WoU', strength=8, xp = 110 ),
            Creature('Metallica', 3, abbrv = 'Metallica', strength=3, xp=1),
            Creature('Sans', 5, abbrv = 'Sans', strength=1, xp=3)],
        

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
                '&': lambda hero: theGame().hero.use(theGame().hero._inventory[theGame().select]),\
                "x": lambda hero: theGame().hero.unequipped(),
                "w": lambda hero: theGame().hero.unequippedArmor(),
       
                }
    _retry  = {'c' :lambda h : theGame().play()}



    def __init__(self, level=1, money = Money('Dogecoin', 'Dogecoin'), equipment = None, hero=None, projectile = None, sword = None, armor = None):
        self.level = level
        self._message = []
        self.effect = []
        if equipment is None:
            equipment = Equipment(name = 'Rien')
        if money is None:
            money = Money()
        self.equipment = equipment
        if hero is None:
            hero = Hero()
        if projectile is None:
            projectile = Projectile(name = 'Rien')
        if sword is None:
            sword = Sword(name = 'rien')
        if armor is None:
            armor = Armor(name = 'Rien')
        self.sword = sword
        self.armor = armor
        self.projectile = projectile
        self.posInventaire=0
        self.hero = hero
        self.floor = None
        self.hero.hp = 70
        self.hero.hpMax = 70
        self.money = money
        self.bonus=0
        self.select = 0
        self.Monokid =  Kids("Monokid","Monokid")
        self.Monosuke = Kids("Monosuke", "Monosuke")
        self.Monotaro = Kids("Monotaro", "Monotaro")
        self.Monophanie = Kids("Monophanie", "Monophanie")
        self.Monodam = Kids ("Monodam", "Monodam")
        self.hunger = 100
        self.calamitycpt = 0
        
        self.l = [self.Monosuke,self.Monophanie,self.Monotaro,self.Monodam,self.Monokid]

    def buildFloor(self):  ### initialise le floor à une nouvelle map
        self.floor = Map(hero=self.hero)
    
    def newFloor(self):  ### Nouvel étage
        self.bonus+=1
        canvas.delete('all')
        if self.floor.chariot is True: 
            present = True
        else:            
            present = False

        if self.floor.WoU is True:
            presentWoU = True
        else:
            presentWoU = False
        
        if self.hero.hp+30>self.hero.hpMax:   
            self.hero.hp=self.hero.hpMax
        else:
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
        if 'WoU' not in str(self.copieNext):
            if 'Silver Chariot' in str(self.copieNext) and present == False:   #### si chariot dans la salle et chariot mort de la salle précédente
                winsound.PlaySound(r"musique jeu\chariot.wav", winsound.SND_ASYNC)
                        

                                        ### si chariot n'est pas dans la salle et chariot mort dans la salle précédente    
            elif 'Silver Chariot' not in str(self.copieNext) and present == True:
                winsound.PlaySound(r"musique jeu\ClosingArgumentDGS.wav", winsound.SND_ASYNC)
        
        if 'WoU' in str(self.copieNext) and presentWoU is False:
                winsound.PlaySound(r"musique jeu\WoU.wav", winsound.SND_ASYNC)
        if 'WoU' not in str(self.copieNext) and presentWoU is True:
                winsound.PlaySound(r"musique jeu\ClosingArgumentDGS.wav", winsound.SND_ASYNC)

                   #### si chariot dans la salle et chariot mort de la salle précédente     
        self.press

    def addMessage(self, msg):  #### ajoute un message à la liste de messages

        self._message.append(msg)

    def addEffect(self, msg):
        self.effect.append(msg)

    def readMessages(
            self):  #### lis les messages et clear la liste de messages

        s = ''
        for m in self._message:
            s += m
        self._message.clear()
        canvasInventaire.create_text(200,300, text = s, font= 'Arial', fill = 'red')
    
    def readEffect(self): ### lis les effets des mobs
        s = ''
        for m in self.effect:
            s+=m
        self.effect.clear()
        canvasInventaire.create_text(200,500, text = s, font = 'Arial', fill = 'blue')

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
    def randAmmo(self):
        
        return self.randElement(Game.munitions)

    def putRandomKids(self): ### put des kids dans la map
        if self.l == []:
            self.l = [self.Monosuke,self.Monophanie,self.Monotaro,self.Monodam,self.Monokid]
        rng = random.randint(0,10)
        if (rng == 1 or rng == 6 or rng == 2) and self.Monosuke in self.l and self.Monosuke not in theGame().hero._bag:
            self.floor.put(self.floor._rooms[random.randint(0,len(self.floor._rooms)-1)].randEmptyCoord(self.floor),self.Monosuke)

        if (rng == 2 or rng == 7 or rng == 3) and self.Monophanie in self.l and self.Monophanie not in theGame().hero._bag:          
            self.floor.put(self.floor._rooms[random.randint(0,len(self.floor._rooms)-1)].randEmptyCoord(self.floor),self.Monophanie)

        if (rng == 3 or rng == 8 or rng == 4) and self.Monotaro in self.l and self.Monotaro not in theGame().hero._bag :
            self.floor.put(self.floor._rooms[random.randint(0,len(self.floor._rooms)-1)].randEmptyCoord(self.floor),self.Monotaro)

        if (rng == 4 or rng == 9 or rng == 5) and self.Monodam in self.l and self.Monodam not in theGame().hero._bag:
            self.floor.put(self.floor._rooms[random.randint(0,len(self.floor._rooms)-1)].randEmptyCoord(self.floor),self.Monodam)

        if (rng == 5 or rng == 10 or rng == 6) and self.Monokid in self.l and self.Monokid not in theGame().hero._bag:
            self.floor.put(self.floor._rooms[random.randint(0,len(self.floor._rooms)-1)].randEmptyCoord(self.floor),self.Monokid)
        
    
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
    
    def calamity(self): ### mécanique de jeu
        if 'WoU' in str(theGame().floor):
            canvasInventaire.create_image(430,280, anchor = NW, image = textures['interface']['WoU'])
            theGame().hero.starve=8
            return True
        
        theGame().hero.starve=2
        return False
    ############################################################### Throw
    def throwUP(self,event):
        a = theGame().floor.pos(theGame().hero)
        b = copy.deepcopy(a)
            
        try:
            while theGame().floor.get(Coord(b.x,b.y-1))!=Map.empty:
                b.y-=1
                if isinstance(theGame().floor.get(Coord(b.x,b.y)), Creature) and theGame().floor.get(Coord(b.x,b.y))!=self.hero: ### si objet rencontre creature
                    creature = True
                    break
                creature = False
        except IndexError:
            b.y = 0
            creature = False
        
        if 'Gun' not in (str(i) for i in self.hero.sword) or 'Bee' not in (str(j) for j in self.hero._stock):
            if len(theGame().hero._inventory) == 0:
                theGame().addMessage("Empty inventory, can't throw")
                canvasInventaire.delete('all')
                canvas.delete('all')
                self.dessineTout()
                return False
            if creature is False:
                    
                if isinstance(theGame().floor.get(Coord(b.x,b.y)), Equipment) or isinstance(theGame().floor.get(Coord(b.x,b.y)), Money):
                    theGame().floor.rm(Coord(b.x,b.y))
                    
                elif isinstance(theGame().floor.get(Coord(b.x,b.y)),Kids):
                    theGame().hero._inventory.remove(theGame().hero._inventory[self.select])
                

                theGame().floor.put(Coord(b.x,b.y), theGame().hero._inventory[self.select])
            else:
                theGame().floor.get(Coord(b.x,b.y)).use(theGame().hero._inventory[self.select])
            theGame().hero._inventory.remove(theGame().hero._inventory[self.select])

        else:
            for i in self.hero._stock:
                if str(i) == 'Bee':
                    self.hero._stock.remove(i)
                    playsound(r'musique jeu\Gunshot.wav')
                    if creature is True:
                        theGame().floor.get(Coord(b.x,b.y)).hp-=i.dmg
                        if theGame().floor.get(Coord(b.x,b.y)).hp<0:
                            theGame().hero.addXP(theGame().floor.get(Coord(b.x,b.y)).xp)
                            theGame().floor.rm(theGame().floor.pos(theGame().floor.get(Coord(b.x,b.y))))
                    break

        
        canvasInventaire.delete('all')
        canvas.delete('all')
        self.floor.moveAllMonsters()
        self.dessineTout()
        

    def throwDown(self,event): ### doit vérifier qu'il y ait pas d'item sur la case d'arrivée
        a = theGame().floor.pos(theGame().hero)
        b = copy.deepcopy(a)      
        try:
            while theGame().floor.get(Coord(b.x,b.y+1))!=Map.empty:
                b.y+=1
                if isinstance(theGame().floor.get(Coord(b.x,b.y)), Creature) and theGame().floor.get(Coord(b.x,b.y))!=self.hero: ### si objet rencontre creature
                    creature = True
                    break
                creature = False
        except IndexError:
            b.y = theGame().floor.size-1
            creature = False
        
        if 'Gun' not in (str(i) for i in self.hero.sword) or 'Bee' not in (str(j) for j in self.hero._stock):
            if len(theGame().hero._inventory) == 0:
                theGame().addMessage("Empty inventory, can't throw")
                canvasInventaire.delete('all')
                canvas.delete('all')
                self.dessineTout()
                return False
            if creature is False:
                if isinstance(theGame().floor.get(Coord(b.x,b.y)), Equipment) or isinstance(theGame().floor.get(Coord(b.x,b.y)), Money):
                    theGame().floor.rm(Coord(b.x,b.y))
                
                elif isinstance(theGame().floor.get(Coord(b.x,b.y)),Kids):
                    theGame().hero._inventory.remove(theGame().hero._inventory[self.select])

                theGame().floor.put(Coord(b.x,b.y), theGame().hero._inventory[self.select])
            
            else:
                theGame().floor.get(Coord(b.x,b.y)).use(theGame().hero._inventory[self.select])
        
            theGame().hero._inventory.remove(theGame().hero._inventory[self.select])
        else:
            for i in self.hero._stock:
                if str(i) == 'Bee':
                    self.hero._stock.remove(i)
                    playsound(r'musique jeu\Gunshot.wav')
                    if creature is True:
                        theGame().floor.get(Coord(b.x,b.y)).hp-=i.dmg
                        if theGame().floor.get(Coord(b.x,b.y)).hp<0:
                            theGame().hero.addXP(theGame().floor.get(Coord(b.x,b.y)).xp)
                            theGame().floor.rm(theGame().floor.pos(theGame().floor.get(Coord(b.x,b.y))))

                    break

        canvasInventaire.delete('all')
        canvas.delete('all')
        self.floor.moveAllMonsters()

        self.dessineTout()
    
    def throwRight(self,event): ### doit vérifier qu'il y ait pas d'item sur la case d'arrivée
        a = theGame().floor.pos(theGame().hero)
        b = copy.deepcopy(a)
        try:
            while theGame().floor.get(Coord(b.x+1,b.y))!=Map.empty:
                b.x+=1
                if isinstance(theGame().floor.get(Coord(b.x,b.y)), Creature) and theGame().floor.get(Coord(b.x,b.y))!=self.hero: ### si objet rencontre creature
                    creature = True
                    break
                creature = False               
        except IndexError:
            b.x = theGame().floor.size-1
            creature = False
        
        if 'Gun' not in (str(i) for i in self.hero.sword) or 'Bee' not in (str(j) for j in self.hero._stock):
            if len(theGame().hero._inventory) == 0:
                theGame().addMessage("Empty inventory, can't throw")
                canvasInventaire.delete('all')
                canvas.delete('all')
                self.dessineTout()
                return False
            if creature is False:
                if isinstance(theGame().floor.get(Coord(b.x,b.y)), Equipment) or isinstance(theGame().floor.get(Coord(b.x,b.y)), Money):
                    theGame().floor.rm(Coord(b.x,b.y))
                
                elif isinstance(theGame().floor.get(Coord(b.x,b.y)),Kids):
                    theGame().hero._inventory.remove(theGame().hero._inventory[self.select])

                theGame().floor.put(Coord(b.x,b.y), theGame().hero._inventory[self.select])
            
            else:
                theGame().floor.get(Coord(b.x,b.y)).use(theGame().hero._inventory[self.select])
        
            theGame().hero._inventory.remove(theGame().hero._inventory[self.select])
        
        else:
            for i in self.hero._stock:
                if str(i) == 'Bee':
                    self.hero._stock.remove(i)
                    playsound(r'musique jeu\Gunshot.wav')
                    if creature is True:
                        theGame().floor.get(Coord(b.x,b.y)).hp-=i.dmg
                        if theGame().floor.get(Coord(b.x,b.y)).hp<0:
                            theGame().hero.addXP(theGame().floor.get(Coord(b.x,b.y)).xp)
                            theGame().floor.rm(theGame().floor.pos(theGame().floor.get(Coord(b.x,b.y))))                   
                    break
                    
        canvasInventaire.delete('all')
        canvas.delete('all')
        self.floor.moveAllMonsters()
        self.dessineTout()
    
    def throwLeft(self,event): ### doit vérifier qu'il y ait pas d'item sur la case d'arrivée
        a = theGame().floor.pos(theGame().hero)
        b = copy.deepcopy(a)

        try:
            while theGame().floor.get(Coord(b.x-1,b.y))!=Map.empty:
                b.x-=1
                if isinstance(theGame().floor.get(Coord(b.x,b.y)), Creature) and theGame().floor.get(Coord(b.x,b.y))!=self.hero: ### si objet rencontre creature
                    creature = True
                    break
                creature = False                
        except IndexError:
            b.x = theGame().floor.size-1
            creature = False
        if 'Gun' not in (str(i) for i in self.hero.sword) or 'Bee' not in (str(j) for j in self.hero._stock):
            if len(theGame().hero._inventory) == 0:
                theGame().addMessage("Empty inventory, can't throw")
                canvasInventaire.delete('all')
                canvas.delete('all')
                self.dessineTout()
                return False
            if creature is False:
                
                if isinstance(theGame().floor.get(Coord(b.x,b.y)), Equipment) or isinstance(theGame().floor.get(Coord(b.x,b.y)), Money):
                    theGame().floor.rm(Coord(b.x,b.y))
                
                elif isinstance(theGame().floor.get(Coord(b.x,b.y)),Kids):
                    theGame().hero._inventory.remove(theGame().hero._inventory[self.select])

                theGame().floor.put(Coord(b.x,b.y), theGame().hero._inventory[self.select])

            else:
                theGame().floor.get(Coord(b.x,b.y)).use(theGame().hero._inventory[self.select])
            
            theGame().hero._inventory.remove(theGame().hero._inventory[self.select])
        else:
            for i in self.hero._stock:
                if str(i) == 'Bee':
                    self.hero._stock.remove(i)
                    playsound(r'musique jeu\Gunshot.wav')
                    if creature is True:
                        theGame().floor.get(Coord(b.x,b.y)).hp-=i.dmg
                        if theGame().floor.get(Coord(b.x,b.y)).hp<0:
                            theGame().hero.addXP(theGame().floor.get(Coord(b.x,b.y)).xp)
                            theGame().floor.rm(theGame().floor.pos(theGame().floor.get(Coord(b.x,b.y))))

                    break
 
        canvasInventaire.delete('all')
        canvas.delete('all')
        self.floor.moveAllMonsters()
        self.dessineTout()

    def dessineVie(self):
        l=50
        if self.calamity() or theGame().hero.poisoned == True:
            canvasInventaire.create_image(350,300,anchor = NW, image = textures['interface']['viePSN'])

        else:
            canvasInventaire.create_image(350,300,anchor = NW, image = textures['interface']['vie'])
        canvasInventaire.create_rectangle(115,905,815,875, fill ='black')
        if theGame().hero.hunger>50:

            canvasInventaire.create_rectangle(115,905,100+715*(theGame().hero.hunger/100),875, fill ='green')
        elif 25<=theGame().hero.hunger<=50:
            canvasInventaire.create_rectangle(115,905,100+715*(theGame().hero.hunger/100),875, fill ='orange')
        elif theGame().hero.hunger<25:
            canvasInventaire.create_rectangle(115,905,100+715*(theGame().hero.hunger/100),875, fill ='red')
            if theGame().hero.hunger == 0:
                canvasInventaire.create_text(470,890, text = 'Vous perdez des hp', font = 'Arial 20', fill = 'cyan')
        
        canvasInventaire.create_text(390,336, text = str(self.hero.hp), font = 'Arial 20')
        canvasInventaire.create_image(60,850, anchor = NW, image = textures['interface']['Apple'] )

    def dessineTout(self):
        self.floor.dessineSol()
        self.floor.dessineStairs()
        self.floor.dessineMobs()
        self.floor.dessineKids()
        self.floor.dessineItems()
        self.floor.dessineProjectiles()
        self.floor.dessineHero()
        self.floor.dessineMoney()
        self.hero.ecritInventaire()
        self.projectile.dessineProjectilesInventaire()
        self.sword.dessineEquippedSword()
        self.armor.dessineEquippedArmor()
        self.money.showMoney()
        self.dessineVie()
        self.hero.dessineXp()
        self.dessineKidsInterface()
        self.readMessages()
        self.readEffect()
    
    def stillAlive(self):
        if self.hero.hp > 0:
            return True
        else : 
            self.gameOver()

    def press(self, event): ### méthode principale pour jouer
        event = event.char
        if self.stillAlive():
            if event in Game._actions:
                Game._actions[event](self.hero)
                if self.hero.invisible == None :
                    self.floor.moveAllMonsters()          
                else :
                    theGame().hero.invisible -= 1
                    if theGame().hero.invisible <= 0 :
                
                        theGame().hero.invisible = None 
                ### status
                theGame().hero.faim+=1
                if theGame().hero.faim%3==0:
                    if theGame().hero.hunger-theGame().hero.starve<0:
                        theGame().hero.hunger = 0
                        theGame().hero.hp -=1
                    else:
                        theGame().hero.hunger-=theGame().hero.starve
                
                if self.hero.poisoned is True:
                    self.hero.poison+=1
                    if self.hero.poison%2==0:
                        self.hero.hp-=1
                
                #### mob abilties
                if 'WoU' in str(self.floor):
                    if self.level < 10:
                        theGame().calamitycpt+=1
                    elif 10<=self.level<13 :
                        theGame().calamitycpt+=2
                    elif self.level>=13:
                        theGame().calamitycpt+=3
                    if theGame().calamitycpt%15==0:
                        if len(theGame().hero._inventory)>0:
                            theGame().hero._inventory.remove(theGame().hero._inventory[0])    
                    
                canvasInventaire.delete('all')
                canvas.delete('all')
                self.dessineTout()
                window.update()
                self.press

    def retry(self):
        window.bind('<Any-KeyPress>', theGame().press)
        theGame().play()

#### inventaire
    def selectionnerInventaire(self):
        self.select=0
        canvasSelect.focus_set()
        canvasSelect.delete('all')

        canvasSelect.create_image(0,0, anchor= NW, image = textures['interface']['select'])
        canvasSelect.bind('<Up>', self.goUp)
        canvasSelect.bind('<Down>', self.goDown)
    
    def goUp(self,event):
        canvasSelect.delete('all')
        if self.posInventaire-100 <0 :
            canvasSelect.create_image(0,0, anchor= NW, image = textures['interface']['select'])
            self.posInventaire=0

        else:
            canvasSelect.create_image(0,self.posInventaire-100, anchor= NW, image = textures['interface']['select'])
            self.posInventaire-=100
        
        if self.select-1<0:
            self.select = 0
        else:
            self.select-=1
         
    def goDown(self,event):
        canvasSelect.delete('all')
        if self.posInventaire+100>400:
            canvasSelect.create_image(0,400, anchor= NW, image = textures['interface']['select'])
            self.posInventaire=400
        else:
            canvasSelect.create_image(0,self.posInventaire+100, anchor= NW, image = textures['interface']['select'])
            self.posInventaire+=100
        
        if self.select >= 4:
            self.select = 4
        else:    
            self.select += 1

    def play(self):
        """1er étage"""
        cpt=0
        self.buildFloor()

        if self.floor.get(self.floor._rooms[0].center()) !=Map.ground:
            self.floor._mat[self.floor._rooms[0].center().y][self.floor._rooms[0].center().x]=Map.ground
        self.floor.put(self.floor._rooms[0].center(), self.hero)
        self.putRandomKids()
        self.dessineTout()
        self.floor.chariot = False
        winsound.PlaySound(r"musique jeu\ClosingArgumentDGS.wav", winsound.SND_ASYNC)
        window.bind('<Alt-KeyPress-z>', self.throwUP)
        window.bind('<Alt-KeyPress-s>', self.throwDown)
        window.bind('<Alt-KeyPress-d>', self.throwRight)
        window.bind('<Alt-KeyPress-q>', self.throwLeft)
        window.bind('<Any-KeyPress>',self.press)
        self.floor.moveAllMonsters()
    
    def continuer(self,event):
        self.press
    
    def gameOver(self):
        winsound.PlaySound(None, winsound.SND_PURGE)
        canvas.delete('all')
        canvas.create_text(w/2,200, text = 'Game Over', font = 'Arial 70 bold', fill = 'white')
        canvas.create_text(w/2,500, text = 'Press c to retry', font = 'Arial 70 bold', fill = 'white')


def theGame(game=Game()):
    """Game singleton"""
    return game
    


window = Tk()
window.state("zoomed")

w, h = window.winfo_screenwidth(), window.winfo_screenheight()
debut = Label(text='Bienvenue dans le Rogue', font=('Arial 20'))
canvas = Canvas(window, width=w, height=h, bg='black')
gameOver= Label(canvas, text='Game over', font=('Arial 20'))

canvasInventaire = Canvas(window, width = w, height = h, bg = '#4C4C4C')
canvasInventaire.place(relx=0.56, rely=0)

canvasSelect = Canvas(window, width = 30, height= 438, bg = 'red' )
canvasSelect.place(relx = 0.59, rely = 0.05)



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
        'Metallica' : ImageTk.PhotoImage(Image.open(r"images jeu\Metallica.png")),
        
    } ,
    'items': {
        'TNT': ImageTk.PhotoImage(Image.open(r"images jeu\TNT.png")),
        'Health Pot': ImageTk.PhotoImage(Image.open(r"images jeu\healthpot.png")),
        'Invisible pot' : ImageTk.PhotoImage(Image.open(r"images jeu\invisiblePotion.png").resize((40,40))),
        'Rainbow Sword': ImageTk.PhotoImage(Image.open(r"images jeu\sword.png")),  ### à redim
        'Moonstaff': ImageTk.PhotoImage(Image.open(r"images jeu\moonstaff.png")),
        'Arrow' : ImageTk.PhotoImage(Image.open(r"images jeu\arrow.png")),
        'Dogecoin' : ImageTk.PhotoImage(Image.open(r"images jeu\Dogecoin.png")),
        'Bow' : ImageTk.PhotoImage(Image.open(r"images jeu\Bow.png")),
        'Gun' : ImageTk.PhotoImage(Image.open(r"images jeu\coltPython.png")),
        'Bee' :  ImageTk.PhotoImage(Image.open(r"images jeu\Bee.png")),
        'Apple' : ImageTk.PhotoImage(Image.open(r"images jeu\apple_map.png").resize((40,40))),
        'Pizza' : ImageTk.PhotoImage(Image.open(r"images jeu\pizza.png").resize((40,40))),
        'Katana' : ImageTk.PhotoImage(Image.open(r"images jeu\katana.png")),
        'Blue Armor' : ImageTk.PhotoImage(Image.open(r"images jeu\blueArmor.png")),
        'Iron Armor' : ImageTk.PhotoImage(Image.open(r"images jeu\ironArmor.png")),
        'Chicken' : ImageTk.PhotoImage(Image.open(r"images jeu\chicken.png")),
    },  #### à redim
    'hero': {
        "Hero" : ImageTk.PhotoImage(Image.open(r'images jeu\monokuma.png')),
        "HeroInv" : ImageTk.PhotoImage(Image.open(r"images jeu\monokuma_invisible.png")),

        
        "HeroCB": ImageTk.PhotoImage(Image.open(r"images jeu\monokumaCowBoy.png")),
        "HeroCBInvisible": ImageTk.PhotoImage(Image.open(r"images jeu\monokumaCowBoyInvisible.png")),
        
        
        'HeroSword' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaSword.png")),
        'HeroSwordInvisible' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaSwordInvisible.png")),
        
        'HeroKatana' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaKatana.png")),
        'HeroKatanaInvisible' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaKatanaInvisible.png")),
        'HeroBlueArmorKatana' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaBlueArmorKatana.png")),
        'HeroBlueArmorKatanaInvisible' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaBlueArmorKatanaInvisible.png")),

        'HeroIronArmor' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaIronArmor.png")),
        'HeroIronArmorInvisible' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaIronArmorInvisible.png")),

        'HeroIronArmorKatana' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaIronArmorKatana.png")),
        'HeroIronArmorKatanaInvisible' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaIronArmorKatanaInvisible.png")),

        
        'HeroIronArmorRainbowSword' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaIronArmorRainbowSword.png")),
        'HeroIronArmorRainbowSwordInvisible' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaIronArmorRainbowSwordInvisible.png")),
        'HeroBlueArmorRainbowSword' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaBlueArmorRainbowSword.png")),

        'HeroIronArmorCowBoy' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaIronArmorCowBoy.png")),
        'HeroIronArmorCowBoyInvisible' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaIronArmorCowBoyInvisible.png")),

        'HeroBlueArmor' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaBlueArmor.png")),
        'HeroBlueArmorInvisible' : ImageTk.PhotoImage(Image.open(r"images jeu\monokumaBlueArmorInvisible.png")),

    },
    'interface' : 
        {'money' : ImageTk.PhotoImage(Image.open(r"images jeu\dogecoinCanvas.png")),
        'vie' : ImageTk.PhotoImage(Image.open(r"images jeu\heart.png")),
        'viePSN' : ImageTk.PhotoImage(Image.open(r"images jeu\heartpoison.png")),
        'select' : ImageTk.PhotoImage(Image.open(r"images jeu\selectArrow.png")),
        'circle' : ImageTk.PhotoImage(Image.open(r"images jeu\circle.png")),
        'Monosuke':ImageTk.PhotoImage(Image.open(r"images jeu\Monosuke test.png")),
        'Monotaro' : ImageTk.PhotoImage(Image.open(r"images jeu\Monotaro opacité.png")),
        'Monophanie' :ImageTk.PhotoImage(Image.open(r"images jeu\Monophanie opacité.png")),
        'Monokid' : ImageTk.PhotoImage(Image.open(r"images jeu\Monokid opacité.png")),
        'Monodam' : ImageTk.PhotoImage(Image.open(r"images jeu\Monodam opacité.png")),
        'Apple' : ImageTk.PhotoImage(Image.open(r'images jeu\apple.png')),
        'WoU' : ImageTk.PhotoImage(Image.open(r'images jeu\wonderOfU head.png')),
        'WoU opacité' : ImageTk.PhotoImage(Image.open(r'images jeu\wonderOfU head opacité.png')),
        'Strength' : ImageTk.PhotoImage(Image.open(r'images jeu\swordInterface.png')),
        'Shield' : ImageTk.PhotoImage(Image.open(r'images jeu\shield.png')),


        },
    'inventaire' : {
        'Health Pot': ImageTk.PhotoImage(Image.open(r"images jeu\healthpot.png").resize((50,50))),
        'Bow' : ImageTk.PhotoImage(Image.open(r"images jeu\bowInventaire.png")),
        'TNT' : ImageTk.PhotoImage(Image.open(r"images jeu\TNT.png").resize((50,75))),
        'Moonstaff' : ImageTk.PhotoImage(Image.open(r"images jeu\moonstaff.png").resize((50,75))),
        'Gun' : ImageTk.PhotoImage(Image.open(r"images jeu\coltPython.png").resize((72,72))),
        'Rainbow Sword': ImageTk.PhotoImage(Image.open(r"images jeu\sword.png")),  

    },
    'kids' :{
        'Monophanie' : ImageTk.PhotoImage(Image.open(r"images jeu\Monophanie.png")),
        'Monosuke' : ImageTk.PhotoImage(Image.open(r"images jeu\Monosuke.png")),
        'Monodam' : ImageTk.PhotoImage(Image.open(r"images jeu\Monodam.png")),
        'Monotaro' : ImageTk.PhotoImage(Image.open(r"images jeu\Monotaro.png")),
        'Monokid' : ImageTk.PhotoImage(Image.open(r"images jeu\Monokid.png"))
    }
}

window.bind('<KeyPress>',theGame().press)
theGame().play()
window.mainloop()
