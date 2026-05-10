import random as rnd
from percent_engine import *


def shuffle_deck(deck):
    rnd.shuffle(deck)

def deal(deck, users_hand, dealers_hand):
    users_hand[0] = rnd.choice(deck)
    users_hand[1] = rnd.choice(deck)
    dealers_hand[0] = rnd.choice(deck)
    dealers_hand[1] = rnd.choice(deck)



def play(deck):
    dealers_hand = []
    users_hand = list(map(int, input("enter your cards: ").split()))
    dealers_first_card = int(input("enter the dealers first card: "))
    dealers_hand.append(dealers_first_card)

    users_sum = sum(users_hand)

    if 11 in users_hand and users_sum > 21:
        users_hand[users_hand.index(11)] = 1

    users_sum = sum(users_hand)

    while users_sum < 21:
        hit = False

        best_rate, best_action = get_best_move(users_hand, dealers_hand[0])
        print(f"The recommended action is {best_action.upper()} (expected win rate is: {best_rate * 100:.2f}%)")
        hit = int(input("1 for HIT or 0 for STAND: "))

        if hit:
            new_card = int(input("enter you new card:"))
            users_hand.append(new_card)
            users_sum = sum(users_hand)
            if 11 in users_hand and users_sum > 21:
                users_hand[users_hand.index(11)] = 1

            users_sum = sum(users_hand)
            print("your cards are now:", users_hand, "and the sum is:", users_sum)

        elif not hit:
            break

    if users_sum > 21:
        print("you lose, you got:", users_sum)
        return

    elif users_sum == 21:
        print("you win, you got:", users_sum)
        return

    dealers_new_card = int(input("enter the dealer second card: "))
    dealers_hand.append(dealers_new_card)
    dealers_sum = sum(dealers_hand)
    print("dealers second card was:", dealers_new_card)

    while dealers_sum < 17:
        dealers_new_card = int(input("enter the dealer second card: "))
        dealers_hand.append(dealers_new_card)
        dealers_hand.append(rnd.choice(deck))
        dealers_sum = sum(dealers_hand)
        if 11 in dealers_hand and dealers_sum > 21:
            dealers_hand[dealers_hand.index(11)] = 1
        dealers_sum = sum(dealers_hand)


    if dealers_sum == 21:
        print("you lose, the dealer got:", dealers_sum)
        return
    elif dealers_sum > 21:
        print("you win, the dealer got:", dealers_sum)
        return

    if dealers_sum > users_sum:
        print("you lose, the dealer got:", dealers_sum, "\nand you got:", users_sum)
        return

    elif dealers_sum == users_sum:
        print("it's a tie, you both got:", users_sum)
        return

    else:
        print("you win, the dealer got:", dealers_sum, "\nand you got:", users_sum)
        return


