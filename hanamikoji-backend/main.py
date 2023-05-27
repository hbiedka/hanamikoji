from hanamikoji import Game

import asyncio
from websockets.server import serve

from enum import Enum

class moveStage(Enum):
    notMoved = 0
    waitingForAcion = 1
    waitingForCards = 2
    waitingForOpponent = 3
    finishing = 4


class GameHandler:
    g = None
    player_sockets = list()

    #player moving
    current_player = None

    #move stage
    move_stage = moveStage.notMoved

    #current move reply
    current_action = None
    current_move = None

    #for now, there is a list of questions and list of answers
    #to be changed to JSON exchange
    player_msg_prompt = list()
    player_msg_response = list()


    def __init__(self):
        self.g = Game()

    async def assign_player(self,ws):
        if self.has_free_slots():
            player_id = len(self.player_sockets)
            self.player_sockets.append(ws)

            if len(self.player_sockets) == len(self.g.players):
                #launch new game
                await self.launch()

            return player_id
        else:
            return None
        
    def has_free_slots(self):
        return len(self.player_sockets) < len(self.g.players)
    
    def id_of_player(self,player):
        return self.g.players.index(player)
    
    def ws_of_player(self,player):
        return self.player_sockets[self.id_of_player(player)]
    
    async def launch(self):
        #start game
        self.g.start()
        self.current_player = self.g.first_player()

        #do first move
        #TODO

    async def recv(self,player_id,msg):
        #TODO
        pass

games = list()

async def echo(websocket):

    my_game = None
    player_id = None

    #find a slot
    for game in games:
        if game.has_free_slots():
            await websocket.send("Joining existing game")
            my_game = game

    if my_game is None:
        my_game = GameHandler()
        games.append(my_game)
        await websocket.send(f"creating new game #{len(games)}")

    player_id = await my_game.assign_player(websocket)


    async for message in websocket:
        await my_game.recv(player_id, message)

async def main():
    async with serve(echo, "localhost", 8765):
        await asyncio.Future()  # run forever

asyncio.run(main())