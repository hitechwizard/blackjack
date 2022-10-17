import random

class Deck:
    FACES = [2,3,4,5,6,7,8,9,10,'J','Q','K','A']
    SUITS = ['\u2663', '\u2664', '\u2665', '\u2666']
    def __init__(self):
        self.cards = None
        self.shuffle()
        print(f"Deck has {len(self.cards)} cards")

    def shuffle(self):
        self.cards = []
        for suit in Deck.SUITS:
            for face in Deck.FACES:
                self.cards.append({
                    'face': face,
                    'suit': suit
                })

    def get_card(self):
        if len(self.cards):
            index = random.randrange(len(self.cards))
            card = self.cards.pop(index)
        else:
            print("There are no more cards in the deck.")
            card = None
        return card

class Hand:
    def __init__(self, player):
        self.cards = []
        self.value = 0
        self.player = player
        self.bet = player.bet
        player.money -= player.bet
        print(f"{player.name} bets ${self.bet}")
        self.has_played = False
        self.blackjack = False

    def add_card(self, card):
        self.cards.append(card)
        return self.calculate_value()

    def calculate_value(self):
        self.value = 0
        aces = 0
        for card in self.cards:
            if isinstance(card['face'], int):
                self.value = self.value + card['face']
            else:
                if card['face'] == 'A':
                    aces += 1
                else:
                    self.value += 10
        if aces == 1:
            if self.value < 11:
                self.value += 11
            else:
                self.value += 1
        elif aces == 2:
            if self.value < 10:
                self.value += 12
            else:
                self.value += 2
        elif aces == 3:
            if self.value < 9:
                self.value += 13
            else:
                self.value += 3
        elif aces == 4:
            if self.value < 8:
                self.value += 14
            else:
                self.value += 4

        return self.value

    def split(self):
        new_hand = Hand(self.player)
        new_hand.add_card(self.cards.pop(1))
        self.add_card(self.player.table.deck.get_card())
        new_hand.add_card(self.player.table.deck.get_card())
        self.player.hands.append(new_hand)
        return new_hand

    def print(self):
        print(f"{self.player.name}'s cards: ", end="")
        for card in self.cards:
            print(f"{card['face']}{card['suit']} ", end="")
        print(f"  Total: {self.value}")

    def play_hand(self):
        self.has_played = True
        if self.value == 21:
            print("BLACKJACK!")
            self.blackjack = True
            return
        command = None
        if self.cards[0]['face'] == self.cards[1]['face'] and self.player.money >= self.player.bet:
            # Ask for split
            print("Do you want to split?")
            split = input().upper()
            if split == 'Y':
                new_hand = self.split()
                self.play_hand()
                new_hand.play_hand()
                return

        while command != "S":
            self.print()
            if self.value > 21:
                print("Busted")
                break
            can_double = False
            prompt = ""
            if command == None and self.player.money >= self.player.bet:
                prompt = ", (D)ouble"
                can_double = True
            print(f"(H)it, (S)tay{prompt}")
            command = input().upper()
            if command == "H":
                self.player.table.deal_card(self)
            elif command == "D" and can_double:
                self.player.money -= self.player.bet
                self.bet += self.player.bet
                self.player.table.deal_card(self)
                self.print()
                break


class Player:
    def __init__(self, name='Anonymous', money=500):
        self.name = name
        self.money = money
        self.hands = []
        self.bet = 0
        self.table = None

    def split_hand(self, deck, hand):
        if len(self.hands):
            if self.money < self.bet:
                print("Player does not have enough money to split")
            else:
                self.money -= self.hands[0].bet
                self.hands.append(hand.split(deck))

        else:
            print("Player does not have a hand to split")

    def get_bet(self):
        self.bet = 0
        if self.money < 1:
            print(f"Sorry {self.name}. House wins again.")
            return 0
        while True:
            print(f"{self.name}, you have ${self.money}. Place your bet:")
            try:
                self.bet = int(input())
            except KeyboardInterrupt:
                raise KeyboardInterrupt()
            except:
                self.bet = 0
            if self.bet < 1 or self.bet > self.money:
                print(f"{self.name}, place a valid bet this time")
            else:
                break
        return self.bet

class Table:
    def __init__(self):
        self.dealer = Player('Dealer')
        self.deck = Deck()
        self.players = []

    def add_player(self, player):
        player.table = self
        self.players.append(player)
        print(f"{player.name} sits down with ${player.money}")

    def deal_card(self, hand, reveal=True):
        card = self.deck.get_card()
        hand.add_card(card)
        if reveal:
            print(f"{hand.player.name} gets a {card['face']}{card['suit']}")

    def deal(self):
        self.dealer.hands = [Hand(self.dealer)]
        for player in self.players:
            if player.bet > 0:
                player.hands = [Hand(player)]
            else:
                player.hands = []

        # Shuffle deck and deal first card
        print("Hold on to your seats, we're dealing")
        self.deck.shuffle()
        # Deal first card
        for player in self.players:
            if player.bet > 0:
                self.deal_card(player.hands[0])
        self.deal_card(self.dealer.hands[0])

        # Deal second card
        for player in self.players:
            if player.bet > 0:
                self.deal_card(player.hands[0])
        self.deal_card(self.dealer.hands[0], reveal=False)

        # Check for insurance
        if self.dealer.hands[0].cards[0]['face'] == 'A':
            print("Insurance available")
            # TODO

    def play(self):
        while True:
            bets = 0
            for player in self.players:
                bets += player.get_bet()
            if bets == 0:
                break;
            self.deal()
            if self.dealer.hands[0].value == 21:
                print("Dealer has BlackJack")
                self.dealer.hands[0].print()
            else:
                for player in self.players:
                    if len(player.hands):
                        player.hands[0].play_hand()
                # Handle Dealer
                dealer_hand = self.dealer.hands[0]
                dealer_hand.print()
                # Does the dealer even need to deal?
                valid_hands = False
                for player in self.players:
                    for hand in player.hands:
                        if hand.value <= 21:
                            valid_hands = True
                            break
                    if valid_hands:
                        break

                while dealer_hand.value < 17 and valid_hands:
                    self.deal_card(dealer_hand)
                # Handle Payouts
                if len(dealer_hand.cards) > 2:
                    dealer_hand.print()
                if dealer_hand.value > 21:
                    print("Dealer busted.")
                    dealer_hand.value = 0
                for player in self.players:
                    for hand in player.hands:
                        winnings = 0
                        if hand.blackjack:
                            winnings = hand.bet * 1.5
                        elif hand.value <= 21:
                            if hand.value > dealer_hand.value:
                                winnings = hand.bet
                        winnings = round(winnings)
                        if winnings:
                            print(f"{player.name} wins ${winnings}")
                            player.money += hand.bet + winnings
                        else:
                            print(f"Dealer rakes in ${hand.bet} of {player.name} chips")

def main():
    player_count = 0
    while player_count < 1:
        print('How many players?')
        try:
            player_count = int(input())
        except:
            player_count = 0
        if player_count < 1 or player_count > 4:
            print('Invalid player count. Try again.')
            player_count = 0

    table = Table()
    for i in range(0, player_count):
        print(f"Player {i+1}, enter your name")
        name = input()
        table.add_player(Player(name))

    try:
        table.play()
    except KeyboardInterrupt:
        print(f"\nCome back when you want to finish losing")

    print("The house always wins.")

if __name__ == '__main__':
    main()
