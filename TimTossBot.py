#Timothy Dusek
#Summer 2019

#This program uses the python-sc2 library to create a bot which can play Starcraft 2
#Due to some errors in Python v3.7 this program was written using v3.6

#ToDo: start part 6
	#build_pylons creates 2 at once if resources are available since its so fast at checking. add a small pause in method
	#add a max amount of workers so if a new nexus is up, extra workers can already go to it.
	#for build_pylons make sure it doesnt build pylons after it reaches 200 pop.
	#for build_pylons make sure pylons are put in correct spaces. second video youtube comments had a way to do this.
	#for build_assimilators vaspene should be vespene.

import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, \
CYBERNETICSCORE, STALKER
import random

class TimTossBot(sc2.BotAI):
	# what to do every step of the program
    async def on_step(self, iteration):
    	await self.distribute_workers() #method to distribute workers to mineral patches located in sc2/bot_ai.py
    	await self.build_workers() #method to create probes
    	await self.build_pylons() #method to create pylons
    	await self.build_assimilators() #method to create assimilators
    	await self.expand() #method to build another base
    	await self.offensive_force_buildings() #method to create buildings used to make an army
    	await self.build_offensive_force() #method used to tell buildings what army units to create
    	await self.attack() #method to attack the enemy


    async def build_workers(self):
    	for nexus in self.units(NEXUS).ready:
    		if self.can_afford(PROBE) and nexus.noqueue:
    			await self.do(nexus.train(PROBE))



    async def build_pylons(self):
    	if self.supply_left < 5 and not self.already_pending(PYLON):
    		nexuses = self.units(NEXUS).ready
    		if nexuses.exists:
    			if self.can_afford(PYLON):
    				await self.build(PYLON, near=nexuses.first)



    async def build_assimilators(self):
    	for nexus in self.units(NEXUS).ready:
    		vaspenes = self.state.vespene_geyser.closer_than(15.0, nexus)
    		for vaspene in vaspenes:
    			if not self.can_afford(ASSIMILATOR):
    				break
    			worker = self.select_build_worker(vaspene.position)
    			if worker is None:
    				break
    			if not self.units(ASSIMILATOR).closer_than(1.0, vaspene).exists:
    				await self.do(worker.build(ASSIMILATOR, vaspene))



    async def expand(self):
    	if self.units(NEXUS).amount < 3 and self.can_afford(NEXUS):
    		await self.expand_now()



    async def offensive_force_buildings(self):
    	if self.units(PYLON).ready.exists:
    		pylon = self.units(PYLON).ready.random


    		if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
    			if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
    				await self.build(CYBERNETICSCORE, near=pylon)
    		
    		elif len(self.units(GATEWAY)) < 3:
    			if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
    				await self.build(GATEWAY, near=pylon)



    async def build_offensive_force(self):
    	for gw in self.units(GATEWAY).ready.noqueue:
    		if self.can_afford(STALKER) and self.supply_left > 1:
    			await self.do(gw.train(STALKER))


    def find_target(self, state):
    	if len(self.known_enemy_units) > 0:
    		return random.choice(self.known_enemy_units)

    	elif len(self.known_enemy_structures) > 0:
    		return random.choice(self.known_enemy_structures)

    	else:
    		return self.enemy_start_locations[0]


    async def attack(self):
    	if self.units(STALKER).amount > 15:
    		for s in self.units(STALKER).idle:
    			await self.do(s.attack(self.find_target(self.state))) #self.state passes game state



    	elif self.units(STALKER).amount > 3:
    		if len(self.known_enemy_units) > 0:
    			for s in self.units(STALKER).idle:
    				await self.do(s.attack(random.choice(self.known_enemy_units))) #known_enemy_units is in bot_ai




#run_game sets parameters for the method on how game should be launched
run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Protoss, TimTossBot()),
    Computer(Race.Terran, Difficulty.Medium)
], realtime=True)