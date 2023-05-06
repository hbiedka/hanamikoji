import random

action_names = ["secret","remove","double_pair","triplet"]

class TableCard:
    name = ""
    points = 0
    
    coin_owner = None
    players = list()
    player_cards = list()

    def __init__(self,name,points,players):
        self.name = name
        self.points = points
        self.players = players

        self.start()

    def start(self):
        self.player_cards = list()
        #create empty deck of cards for each player
        for player in self.players:
            self.player_cards.append(0)

    def add_player_card(self,player):
        for index, player_of in enumerate(self.players):
            if player is player_of:
                self.player_cards[index]+=1
                return True
        
        #no player
        return False

    def move_coin(self):
        max_value = None
        winner_index = None

        for index, cards in enumerate(self.player_cards):
            if max_value is None or cards > max_value:
                #if first iteration or some player has more cards than others
                max_value = cards
                winner_index = index
            elif cards == max_value:
                #draw - winner not recognised
                return

        if winner_index is not None:
            self.coin_owner = self.players[winner_index]
        return


    def player_winner(self):
        return self.coin_owner

    def view(self):
        #TODO refactorize
        coin_pl0 = "*" if self.players[0] is self.coin_owner else " "
        coin_pl1 = "*" if self.players[1] is self.coin_owner else " "
        print(f"{self.player_cards[0]} {coin_pl0}[{self.full_name()}\t]{coin_pl1} {self.player_cards[1]}")

    def full_name(self):
        return f"{self.name}-{self.points}pts"

class Player:
    id = 0

    cards_on_hand = list()
    card_secret = None
    cards_removed = list()
    actions = list()

    def __init__(self,id):
        self.id = id
        self.start()

    def start(self):
        self.actions = [True,True,True,True]
        self.drop_cards()

    def drop_cards(self):
        self.cards_on_hand = list()
        self.card_secret = None
        self.cards_removed = list()

    def assign_card(self,card):
        self.cards_on_hand.append(card)
    
    def assign_cards(self,cards):
        self.cards_on_hand.extend(cards)

    def how_many_cards(self):
        return len(self.cards_on_hand)
    
    def actions_available(self,verbose=False):
        out = list()
        for i in range(len(self.actions)):
            if self.actions[i]:
                out.append(i)

        if verbose:
            print("actions available: ",end="")
            for action in out:
                print(f"{action_names[action]} ({action}), ",end="")

            print("")

        return out
    
    def can_move(self):
        return len(self.actions_available())>0

    def use_action(self,action):
        if action >= len(self.actions):
            print("unknown move")
            return False
        
        if self.actions[action]:
            self.actions[action] = False
            return True
        else:
            return False
        
    def use_card(self,card_id):
        return self.cards_on_hand.pop(card_id)
    
    def use_cards(self,card_ids):
        cards_to_use = list()
        ids_to_rm = list()

        for id_or_set in card_ids:
            if type(id_or_set) is list:
                cards_to_use.append(list())
                for id in id_or_set:
                    cards_to_use[-1].append(self.cards_on_hand[id])
                    ids_to_rm.append(id)
            else:
                cards_to_use.append(self.cards_on_hand[id_or_set])
                ids_to_rm.append(id_or_set)

        for id in ids_to_rm:
            self.cards_on_hand[id] = -1

        try:
            while True:
                self.cards_on_hand.remove(-1)
        except ValueError:
            pass

        return cards_to_use

class Game:
    table_cards = list()
    card_pool = list()
    players = list()

    round_result = None
    player_action_cb = None

    def __init__(self):
        """
            New game constructos
        """
        self.players = [Player(1), Player(2)]

        self.table_cards = [
            TableCard("red",2,self.players),
            TableCard("lemon",2,self.players),
            TableCard("purple",2,self.players),
            TableCard("orange",3,self.players),
            TableCard("blue",3,self.players),
            TableCard("green",4,self.players),
            TableCard("pink",5,self.players)
        ]

        #initialize first game
        self.start()


    def start(self):

        #remove cards from table
        for card in self.table_cards:
            card.start()


        #set pool
        self.card_pool = list()
        for card in self.table_cards:
            for _ in range(card.points):
                self.card_pool.append(card)


        #shuffle
        random.shuffle(self.card_pool)

        for player in self.players:
            player.start()

        #give cards for players
        for _ in range(6):
            for player in self.players:
                player.assign_card(self.card_pool.pop())
        
    def first_player(self):
        return self.players[0]

    def opponent_of(self,current_player):
        for player in self.players:
            if player is not current_player:
                return player
            
        #impossible - no opponents
        return None
        
    def card_ids_repeat(self,set):
        ids_met = list()

        for item in set:
            if type(item) is list:
                for subitem in item:
                    if subitem in ids_met:
                        return True
                    ids_met.append(subitem)
            else:
                if item in ids_met:
                    return True
                ids_met.append(item)

        return False
        
    def premove(self,player):
        #pick one card
        player.assign_card(self.card_pool.pop())

    def move(self,player,action,cards):
        #TODO validate player
        if player not in self.players:
            return -3

        # can player move
        if action not in player.actions_available():
            return -1
        
        #todo validate card set
        if action == 0:
            #secret
            player.card_secret = player.use_cards(cards)[0]

        elif action == 1:
            #remove two cards
            if self.card_ids_repeat(cards):
                return -2
            player.cards_removed = player.use_cards(cards)

        elif action in [2,3]:
            if self.card_ids_repeat(cards):
                return -2

            #double pair or triplet
            opponent = self.opponent_of(player)
            cards_for_opp = player.use_cards(cards)

            #request action
            opp_action = self.player_action_cb(opponent,action,cards_for_opp)

            if action == 2:
                opp_cards = cards_for_opp.pop(opp_action)
                mover_cards = cards_for_opp[0]

                for card in mover_cards:
                    card.add_player_card(player)
                
                for card in opp_cards:
                    card.add_player_card(opponent)
                
            elif action == 3:
                opp_card = cards_for_opp.pop(opp_action)

                opp_card.add_player_card(opponent)

                for card in cards_for_opp:
                    card.add_player_card(player)

        player.use_action(action)

        return 0

    def is_end(self):
        can_somebody_move = False

        for player in self.players:
            if player.can_move():
                can_somebody_move = True

        return not can_somebody_move

    def round_finish(self):
        #assign secrets
        for player in self.players:
            player.card_secret.add_player_card(player)

        #move coins and count pts
        self.round_result = dict()

        for player in self.players:
            self.round_result[player.id] = dict()
            self.round_result[player.id]["cards"] = 0
            self.round_result[player.id]["points"] = 0

        for card in self.table_cards:
            card.move_coin()
            winner = card.player_winner()

            
            if winner is not None:
                self.round_result[winner.id]["points"]+=card.points
                self.round_result[winner.id]["cards"]+=1

        #find winner
        how_many_winners = 0
        round_winner = None

        for player in self.players:
            player_result = self.round_result[player.id]

            if player_result["cards"] >= 4 or player_result["points"] >= 11:
                how_many_winners += 1
                round_winner = player

        if how_many_winners == 1:
            #only one winner
            return round_winner
        else:
            #draw - no winner or more than one winner
            return None

    def view(self):
        print("TABLE")
        print()
        print("P1\t\tP2")
        for card in self.table_cards:
            card.view()

        print()

        
        for player in self.players:
            print(f"Player {player.id}:")
        
            print("Cards: ",end="")
            for index,card in enumerate(player.cards_on_hand):
                print(f"{index}[{card.full_name() }], ", end="")

            print()
            player.actions_available(verbose=True)

    def show_results(self):
        if self.round_result is None:
            print("no results yet")
            return

        for player in self.players:
            result = self.round_result[player.id]
            print(f"Player {player.id} results: {result['cards']} cards, {result['points']} pts")

        for player in self.players:
            print(f"secret of Player {player.id}: {player.card_secret.full_name()}")
            print(f"cards removed by Player {player.id}: ",end="")
            for card in player.cards_removed:
                print(f"{card.full_name()}, ",end="")
            print()
            


g = None

def player_action(player,action,cards):
    print(f"action for player {player.id}: {action_names[action]}")

    if action == 2:
        for i in range(len(cards)):
            print(f"{i+1}: {cards[i][0].full_name()} / {cards[i][1].full_name()}")

    elif action == 3:
        for i in range(len(cards)):
            print(f"{i+1}: {cards[i].full_name()}")

    while True: 
        out = int(input("Card/Set?: "))-1

        if out < 0 or out >= len(cards):
            print("out of range!")
            continue

        return out


def play():
    g = Game()
    g.player_action_cb = player_action

    player_starting = g.first_player()
    player = g.first_player()

    while True:
        g.premove(player)

        g.view()

        while True:
            print(f"PLAYER {player.id} MOVE.")
            action =int(input("action? :"))

            cards = list()
            if action == 0:
                id = int(input("card ID to secret?"))
                cards.append(id)
            elif action == 1:
                for i in range(2):
                    id = int(input(f"card id to remove ({i+1} of 2): "))
                    cards.append(id)

            elif action == 2:
                for i in range(2):
                    set = list()
                    for j in range(2):
                        id = int(input(f"(set {i+1} of 2) card id to double-pair ({j+1} of 2): "))
                        set.append(id)
                    cards.append(set)

            elif action == 3:
                for i in range(3):
                    id = int(input(f"card id to triplet ({i+1} of 3): "))
                    cards.append(id)

            else:
                continue

            error = g.move(player,action,cards)
            if error == 0:
                break
            elif error == -1:
                print("move not available or unknown")
            elif error == -2:
                print("the same card used multiple times")

        if (g.is_end()):
            print("game end!")
            winner = g.round_finish()
            g.view()
            g.show_results()
            
            if winner is not None:
                print(f"player {winner.id} wins!")
                break
            else:
                print("draw")
                g.start()
                player_starting = g.opponent_of(player_starting)

                player = player_starting
                continue

        #next player
        player = g.opponent_of(player)


import time

def test_cb(player,action,cards):
    time.sleep(0.5)
    return 0

def test():

    g = Game()
    g.player_action_cb = test_cb

    player_starting = g.first_player()
    player = g.first_player()

    winner = None
    while winner is None:

        for action in range(4):
            for i in range(2):

                print(f"player {player.id} move:")
                g.premove(player)
                g.view()

                e = 0
                if action == 0:
                    e = g.move(player,0,[0])
                elif action == 1:
                    e = g.move(player,1,[0,1])
                elif action == 2:
                    e = g.move(player,2,[[0,1],[2,3]])
                elif action == 3:
                    e = g.move(player,3,[0,1,2])

                if e != 0:
                    print(f"move error {e}")
                    return

                if (g.is_end()):
                    print("game end!")
                    winner = g.round_finish()
                    g.view()
                    g.show_results()
                    
                    if winner is not None:
                        print(f"player {winner.id} wins!")
                    else:
                        print("draw")
                        g.start()
                        player_starting = g.opponent_of(player_starting)
                        player = player_starting
                        time.sleep(2)
                
                player = g.opponent_of(player)
                time.sleep(0.5)



if __name__ == "__main__":
    test()
    #play()
