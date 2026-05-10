

show_cards = [2,3,4,5,6,7,8,9,10,11]
hole_cards = [2,3,4,5,6,7,8,9,10,11]

outcomes = {card: {17: 0, 18: 0, 19: 0, 20: 0, 21: 0, "Bust": 0} for card in hole_cards}

def dealer_percent_engine(up_card, hole_card_index, prev_sum, percentage, cards):

    hole_card = hole_cards[hole_card_index]

    current_path_cards = cards + [hole_card]

    sum = prev_sum + hole_card

    if sum > 21 and 11 in current_path_cards:
        sum -= 10
        current_path_cards[current_path_cards.index(11)] = 1

    if hole_card == 10:
        temp_percentage = 4/13
    else:
        temp_percentage = 1/13


    if sum < 17:
        for i in range(len(hole_cards)):
            dealer_percent_engine(up_card, i, sum, percentage * temp_percentage, current_path_cards)

    if sum > 21:
        outcomes[up_card]["Bust"] += percentage*temp_percentage
        return

    if sum >= 17:
        outcomes[up_card][sum] += percentage*temp_percentage
        return


def calculate_hit_chances(player_cards, dealer_upcard):
    total_hit_win_prob = 0
    for card in hole_cards:
        temp_cards = player_cards + [card]
        current_sum = sum(temp_cards)
        if card == 10:
            card_chance = 4/13
        else:
            card_chance = 1/13
        if current_sum > 21 and 11 in temp_cards:
            temp_cards[temp_cards.index(11)] = 1
            current_sum -= 10

        if current_sum > 21:
            temp_probability = 0

        elif current_sum == 21:
            temp_probability = 1 - outcomes[dealer_upcard][21]

        else:
            temp_probability, _ = get_best_move(temp_cards, dealer_upcard)

        total_hit_win_prob += temp_probability * card_chance

    return total_hit_win_prob




def get_best_move(player_cards, dealer_upcard):
    stand_win_rate = 0
    current_sum = sum(player_cards)
    temp_users_cards = player_cards
    hit_win_rate = calculate_hit_chances(player_cards, dealer_upcard)
    if current_sum <= 17:
        stand_win_rate = outcomes[dealer_upcard]["Bust"]
    else:
        for i in range(17, current_sum):
            stand_win_rate += outcomes[dealer_upcard][i]
        stand_win_rate += outcomes[dealer_upcard]["Bust"]
    if hit_win_rate > stand_win_rate:
        return hit_win_rate, "hit"
    else:
        return stand_win_rate, "stand"






for up in hole_cards:
    for i in range(len(hole_cards)):
        dealer_percent_engine(up, i, up, 1.0, [up])