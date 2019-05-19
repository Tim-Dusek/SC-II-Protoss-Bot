import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *
import random, time

#TODO (after finishing on_step functions)
#Allow new base to be build by first base then flown to a new location
#When implimenting gametime, tutorial 6 comments on Youtube has a way to do it better than iterations.
#get vespene to be created using game time not just willy nilly

class TimTerranBot(sc2.BotAI):
    def __init__(self): #initialization method
        self.MAX_WORKERS = 62



	# what to do every step of the program
    async def on_step(self, iteration):
        print(self.time)
        await self.distribute_workers() #method to distribute workers to mineral patches located in sc2/bot_ai.py
        await self.build_scvs() #method to create probes
        await self.build_refinery() #method to create assimilators
        #await self.build_supplydepot() #method to create supply depots
        #await self.expand_bases() #method to build another base
        #await self.build_offensive_buildings() #method to build barracks/other miltary buildings

    async def build_scvs(self): #Tested and works
       for commandcenter in self.units(COMMANDCENTER).ready:
            if self.can_afford(SCV) and commandcenter.noqueue and len(self.units(SCV)) < self.MAX_WORKERS:
                await self.do(commandcenter.train(SCV))
                time.sleep(0.05)




    async def build_refinery(self): #tested and works
        for commandcenter in self.units(COMMANDCENTER).ready:
            geysers = self.state.vespene_geyser.closer_than(15.0, commandcenter)
            for geyser in geysers:
                if self.can_afford(REFINERY):	
                    scv = self.select_build_worker(geyser.position)
                    if scv is None:
                        break
                    if not self.units(REFINERY).closer_than(1.0, geyser).exists:
                        await self.do(scv.build(REFINERY, geyser))


    


run_game(maps.get("AbyssalReefLE"), [
    Bot(Race.Terran, TimTerranBot()),
    Computer(Race.Terran, Difficulty.Easy)
], realtime=True)