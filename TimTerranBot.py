import sc2
from sc2 import run_game, maps, Race, Difficulty, game_info
from sc2.ids.upgrade_id import UpgradeId
from sc2.player import Bot, Computer
from sc2.constants import *
import random, time
import cv2 #Open CVuses 0,0 for top left but uses 0,0 as bottom left for coordinates
import numpy as np

#TODO (after finishing on_step functions)
#Allow new base to be build by first base then flown to a new location
#get vespene to be created using game time not just willy nilly
#learn to wall off base
#don't place supply depots next to the command center

class TimTerranBot(sc2.BotAI):
    def __init__(self): #initialization method
        self.MAX_WORKERS = 40
        self.MAX_COMMANDCENTERS = 3
        self.MAX_BARRACKS = 5


	# what to do every step of the program
    async def on_step(self, iteration):
        print(self.time)
        await self.distribute_workers() #method to distribute workers to mineral patches located in sc2/bot_ai.py
        await self.build_scvs() #method to create probes
        await self.build_refinery() #method to create assimilators
        await self.build_supplydepot() #method to create supply depots
        await self.expand_bases() #method to build another base
        await self.build_offensive_buildings() #method to build barracks/other miltary buildings
        await self.build_offensive_units() #method to build army units such a marines
        await self.intel() #
        await self.attack() #method to attack/defend



    async def intel(self):
        game_data = np.zeros((self.game_info.map_size[1],self.game_info.map_size[0], 3), np.uint8)
        for commandcenter in self.units(COMMANDCENTER):
            cmd_pos = commandcenter.position
            cv2.circle(game_data, (int(cmd_pos[0]), int(cmd_pos[1])), 10, (0,255,0), -1)


        flipped = cv2.flip(game_data, 0) # flipping game data for coordinates
        resized = cv2.resize(flipped, dsize=None, fx=2, fy=2)
        cv2.imshow('Intel', resized)
        cv2.waitKey(1)



    async def build_scvs(self):
       for commandcenter in self.units(COMMANDCENTER).ready:
            if self.can_afford(SCV) and commandcenter.noqueue and len(self.units(SCV)) < self.MAX_WORKERS:
                await self.do(commandcenter.train(SCV))
                time.sleep(0.05)



    async def build_refinery(self):
        for commandcenter in self.units(COMMANDCENTER).ready:
            geysers = self.state.vespene_geyser.closer_than(15.0, commandcenter)
            for geyser in geysers:
                if self.can_afford(REFINERY):	
                    scv = self.select_build_worker(geyser.position)
                    if scv is None:
                        break
                    if not self.units(REFINERY).closer_than(1.0, geyser).exists:
                        await self.do(scv.build(REFINERY, geyser))


    async def build_supplydepot(self):
        if self.supply_left < 5 and not self.already_pending(SUPPLYDEPOT):
            commandcenters = self.units(COMMANDCENTER).ready
            if commandcenters.exists:
                if self.can_afford(SUPPLYDEPOT):
                    await self.build(SUPPLYDEPOT, near=commandcenters.first)
                    time.sleep(0.05)



    async def expand_bases(self):
        if self.units(COMMANDCENTER).amount < self.MAX_COMMANDCENTERS and self.can_afford(COMMANDCENTER):
            await self.expand_now()
            time.sleep(0.05)


    async def build_offensive_buildings(self):
        if self.units(SUPPLYDEPOT).ready.exists:
            supply_depot = self.units(SUPPLYDEPOT).ready.random

            if self.can_afford(BARRACKS) and self.units(BARRACKS).amount < self.MAX_BARRACKS and not self.already_pending(BARRACKS):
                    await self.build(BARRACKS, near = supply_depot)


    async def build_offensive_units(self):
        for rax in self.units(BARRACKS).ready.noqueue:
            if self.can_afford(MARINE) and self.supply_left > 0:
                await self.do(rax.train(MARINE))
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
        combat_units = {MARINE: [25, 5]}


        for UNIT in combat_units:
            if self.units(UNIT).amount > combat_units[UNIT][0] and self.units(UNIT).amount > combat_units[UNIT][1]:
                for s in self.units(UNIT).idle:
                    await self.do(s.attack(self.find_target(self.state)))

            elif self.units(UNIT).amount > combat_units[UNIT][1]:
                if len(self.known_enemy_units) > 0:
                    for s in self.units(UNIT).idle:
                        await self.do(s.attack(random.choice(self.known_enemy_units)))


run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Terran, TimTerranBot()),
    Computer(Race.Terran, Difficulty.Easy)
], realtime=True)
