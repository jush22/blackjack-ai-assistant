from functions import shuffle_deck, deal, play
from percent_engine import outcomes


JACK, QUEEN, KING,ACE = 10,10,10,11

deck = [2,3,4,5,6,7,8,9,10,JACK,QUEEN,KING,ACE] * 4

dealers_hand = [0,0]
users_hand = [0,0]




up_card = dealers_hand[0]
play(deck)


