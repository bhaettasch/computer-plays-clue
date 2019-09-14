from strategies.player import Player
import random


class ProcastinationPlayer(Player):
    """
       Completely random decision based strategy
       """

    def __init__(self, figure):
        super().__init__(figure)
        self.STRATEGY = "easy"
        self.current_question = None

        self.unknown_figures = set()
        self.unknown_weapons = set()
        self.unknown_rooms = set()

        self.my_figures = set()
        self.my_weapons = set()
        self.my_rooms = set()
        self.all_cards=set()


    def set_game_reference(self, game):
        """
        (Override)
        Attach a reference to the central game logic object
        Overriding this to use this to also initiate our knowledge repository

        :param game: central game logic
        :type game: Game
        """
        super().set_game_reference(game)

        # Init knowledge repository with existing game elements (figures, weapons and rooms)
        self.unknown_figures = set(game.figure_names)
        self.unknown_weapons = set(game.weapons)
        self.unknown_rooms = set(game.room_manager.rooms)
        self.other_players = [player for player in game.players if player is not self]
        self.players_cards = {player: {'has':set(), 'has_not':set()} for player in self.game.players}
        self.last_question=set()


    def _note_seen_card(self, card):
        """
        Note that the given card was seen

        :param card: card that was shown
        :type card: str
        """
        # Add this card to knowledge repository (by removing it from set of unknown elements)
        print("See card '{}'".format(card))
        if card in self.game.figure_names:
            self.unknown_figures.discard(card)
        elif card in self.game.weapons:
            self.unknown_weapons.discard(card)
        else:
            self.unknown_rooms.discard(card)

    def set_own_card(self, card):
        """
        (Override)
        Set the given card as an own card
        Overriding this to update knowledge repository

        :param card: card (figure, weapon or room)
        :type card: str
        """
        super().set_own_card(card)

        self.players_cards[self]['has'] = self.cards
        self.players_cards[self]['has_not'] = set(
            [card for card in (self.game.figure_names + self.game.weapons + self.game.room_manager.rooms) if
             card not in list(self.cards)])

        if card in self.game.figure_names:
            self.my_figures.add(card)
        elif card in self.game.weapons:
            self.my_weapons.add(card)
        else:
            self.my_rooms.add(card)

        # Add card to knowledge repository
        self._note_seen_card(card)

    def next_room(self, possible_rooms):
        print(self.unknown_figures, self.unknown_weapons, self.unknown_rooms)

        self._check_if_nobody_has_card()
        intersect_list = [room for room in possible_rooms if room in self.unknown_rooms]
        if len(self.unknown_rooms) > 1 and intersect_list:
            return random.choice(intersect_list)

        intersect_list = [room for room in possible_rooms if room in self.my_rooms]
        if intersect_list:
            return random.choice(intersect_list)

        return random.choice(possible_rooms)

    def next_question(self):
        # Narrowed everything down to one option? Accuse
        if len(self.unknown_figures) == 1 and len(self.unknown_weapons) == 1 and len(self.unknown_rooms) == 1:
            self.current_question = (
                True,
                self.unknown_figures.pop(),
                self.unknown_weapons.pop(),
                self.unknown_rooms.pop()
            )
        # Not sure yet? Just ask
        else:
            # As we are the random player, we just ask randomly (at least only for cards we do not know yet).
            # Although there might be better ways :D
            self.current_question = (
                False,
                random.choice(list(self.unknown_figures)),
                random.choice(list(self.unknown_weapons)),
                self.figure.position)

        return self.current_question

    def choose_card_to_show(self, questioned_cards):
        # Show random card if player has at least one of them

        possible_cards = [card for card in questioned_cards if card in self.cards]

        if len(possible_cards) == 0:
            return None
        else:
            return random.choice(possible_cards)

    def see_card(self, card, showing_player):
        self._note_seen_card(card)
        self.players_cards[showing_player]['has'].add(card)

    def see_no_card(self, showing_player):
        self.players_cards[showing_player]['has_not'].add(self.current_question[1])
        self.players_cards[showing_player]['has_not'].add(self.current_question[2])
        self.players_cards[showing_player]['has_not'].add(self.current_question[3])

    def see_no_card_from_nobody(self):
        self.unknown_figures=set()
        self.unknown_figures.add(self.current_question[1])
        self.unknown_weapons=set()
        self.unknown_weapons.add(self.current_question[2])
        if self.current_question[3] not in self.cards:
            self.unknown_rooms = set()
            self.unknown_rooms.add(self.current_question[3])


    def observe_card_shown(self, showing_player, seeing_player, questioned_cards):
        intersect_list = [card for card in questioned_cards if card not in self.cards]
        if len(intersect_list) == 1:
            self.see_card(intersect_list[0], showing_player)

    def observe_no_card_shown(self, showing_player, seeing_player, questioned_cards):
        for card in questioned_cards:
            self.players_cards[showing_player]['has_not'].add(card)


    def observe_no_card_from_nobody(self, seeing_player, questioned_cards):
        pass


    def _check_if_nobody_has_card(self):
        all_cards_dict = {}
        for card in self.game.figure_names + self.game.weapons + self.game.room_manager.rooms:
           all_cards_dict[card]={}
           for player in self.game.players:
               if card in self.players_cards[player]['has_not']:
                   all_cards_dict[card][player]=True
               else:
                   all_cards_dict[card][player] = False


        for card in all_cards_dict:
            if False not in all_cards_dict[card].values():
                if card in self.game.figure_names:
                    self.unknown_figures=set()
                    self.unknown_figures.add(card)
                elif card in self.game.weapons:
                    self.unknown_weapons = set()
                    self.unknown_weapons.add(card)
                else:
                    self.unknown_rooms = set()
                    self.unknown_rooms.add(card)






