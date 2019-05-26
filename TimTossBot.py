#Timothy Dusek
#Summer 2019

#This program uses the python-sc2 library to create a bot which can play Starcraft 2
#Due to some errors in Python v3.7 this program was written using v3.6
#~4870 iterations per minute but this changes on each computer who runs this programk


#ToDo: start part 6
	#build_pylons creates 2 at once if resources are available since its so fast at checking. add a small pause in method 0.05
	#for build_pylons make sure it doesnt build pylons after it reaches 200 pop.
	#for build_pylons make sure pylons are put in correct spaces. second video youtube comments had a way to do this.
	#for build_assimilators vaspene should be vespene.

import sc2
from sc2 import run_game, maps, Race, Difficulty, game_info
from sc2.ids.upgrade_id import UpgradeId
from sc2.player import Bot, Computer
from sc2.constants import NEXUS, PROBE, PYLON, ASSIMILATOR, GATEWAY, \
CYBERNETICSCORE, STALKER, STARGATE, VOIDRAY
import random, time
import cv2
import numpy as np

class TimTossBot(sc2.BotAI):
	def __init__(self): #initialization method
		self.ITERATIONS_PER_MINUTE = 165
		self.MAX_WORKERS = 50


	# what to do every step of the program
	async def on_step(self, iteration):
		self.iteration = iteration
		await self.distribute_workers() #method to distribute workers to mineral patches located in sc2/bot_ai.py
		await self.build_workers() #method to create probes
		await self.build_pylons() #method to create pylons
		await self.build_assimilators() #method to create assimilators
		await self.expand() #method to build another base
		await self.offensive_force_buildings() #method to create buildings used to make an army
		await self.build_offensive_force() #method used to tell buildings what army units to create
		await self.intel()
		await self.attack() #method to attack the enemy


	async def intel(self):
		game_data = np.zeros((self.game_info.map_size[1],self.game_info.map_size[0], 3), np.uint8)
		for nexus in self.units(NEXUS):
			nex_pos = nexus.position
			cv2.circle(game_data, (int(nex_pos[0]), int(nex_pos[1])), 10, (0,255,0), -1)


		flipped = cv2.flip(game_data, 0) # flipping game data for coordinates
		resized = cv2.resize(flipped, dsize=None, fx=2, fy=2)
		cv2.imshow('Intel', resized)
		cv2.waitKey(1)

	async def build_workers(self):
		if len(self.units(NEXUS))*16 > len(self.units(PROBE)):
			if len(self.units(PROBE)) < self.MAX_WORKERS:
				for nexus in self.units(NEXUS).ready:
					if self.can_afford(PROBE) and nexus.noqueue:
						await self.do(nexus.train(PROBE))
						time.sleep(0.05)


	async def build_pylons(self):
		if self.supply_left < 5 and not self.already_pending(PYLON):
			nexuses = self.units(NEXUS).ready
			if nexuses.exists:
				if self.can_afford(PYLON):
					await self.build(PYLON, near=nexuses.first)
					time.sleep(0.05)



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
					time.sleep(0.05)


	async def expand(self):
		if self.units(NEXUS).amount < (self.iteration / self.ITERATIONS_PER_MINUTE) and self.can_afford(NEXUS):
			await self.expand_now()
			time.sleep(0.05)


	async def offensive_force_buildings(self):
		#print(self.iteration / self.ITERATIONS_PER_MINUTE)
		if self.units(PYLON).ready.exists:
			pylon = self.units(PYLON).ready.random

			if self.units(GATEWAY).ready.exists and not self.units(CYBERNETICSCORE):
				if self.can_afford(CYBERNETICSCORE) and not self.already_pending(CYBERNETICSCORE):
					await self.build(CYBERNETICSCORE, near=pylon)
					time.sleep(0.05)

			elif len(self.units(GATEWAY)) < 1:
				if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
					await self.build(GATEWAY, near=pylon)
					time.sleep(0.05)

			if self.units(CYBERNETICSCORE).ready.exists:
				if len(self.units(STARGATE)) < (self.iteration / self.ITERATIONS_PER_MINUTE):
					if self.can_afford(STARGATE) and not self.already_pending(STARGATE):
						await self.build(STARGATE, near=pylon)
						time.sleep(0.05)



	async def build_offensive_force(self):
		for sg in self.units(STARGATE).ready.noqueue:
			if self.can_afford(VOIDRAY) and self.supply_left > 0:
				await self.do(sg.train(VOIDRAY))
				time.sleep(0.05)


	def find_target(self, state):
		if len(self.known_enemy_units) > 0:
			return random.choice(self.known_enemy_units)

		elif len(self.known_enemy_structures) > 0:
			return random.choice(self.known_enemy_structures)

		else:
			return self.enemy_start_locations[0]


	async def attack(self):
		# {UNIT: [n to fight, n to defend]}
		aggressive_units = {VOIDRAY: [8, 3]}


		for UNIT in aggressive_units:
			if self.units(UNIT).amount > aggressive_units[UNIT][0] and self.units(UNIT).amount > aggressive_units[UNIT][1]:
				for s in self.units(UNIT).idle:
					await self.do(s.attack(self.find_target(self.state)))

			elif self.units(UNIT).amount > aggressive_units[UNIT][1]:
				if len(self.known_enemy_units) > 0:
					for s in self.units(UNIT).idle:
						await self.do(s.attack(random.choice(self.known_enemy_units)))




#run_game sets parameters for the method on how game should be launched
run_game(maps.get("AbyssalReefLE"), [
	Bot(Race.Protoss, TimTossBot()),
	Computer(Race.Terran, Difficulty.Hard)
], realtime=False)
