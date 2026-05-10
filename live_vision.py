import cv2
import numpy as np
import mss

from ultralytics import YOLO
from percent_engine import *

def card_to_int(card_string):
    if card_string in ['J', 'Q', 'K', 'Jack', 'Queen', 'King']:
        return 10
    elif card_string in ['A', 'Ace']:
        return 11
    else:
        return int(card_string)


def draw_overlay(frame, recommendation, player_hand, dealer_upcard, hand_is_over, stand, win):
    h, w = frame.shape[:2]

    # Semi-transparent dark panel in top-left
    panel_w, panel_h = 420, 160
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (10 + panel_w, 10 + panel_h), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.55, frame, 0.45, 0, frame)

    if win:
        cv2.putText(frame, "YOU WIN!", (20, 60),
                    cv2.FONT_HERSHEY_DUPLEX, 1.4, (100, 100, 255), 2)
        cv2.putText(frame, "Press R for next hand", (20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)

    elif stand:
        cv2.putText(frame, "STAND!", (20, 60),
                    cv2.FONT_HERSHEY_DUPLEX, 1.4, (100, 100, 255), 2)
        cv2.putText(frame, "Press R for next hand", (20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)

    elif hand_is_over:
        cv2.putText(frame, "HAND OVER, LOST!", (20, 60),
                    cv2.FONT_HERSHEY_DUPLEX, 1.4, (100, 100, 255), 2)
        cv2.putText(frame, "Press R for next hand", (20, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)

    elif recommendation:
        color = (0, 255, 80) if recommendation == "HIT" else (0, 120, 255)
        cv2.putText(frame, recommendation, (20, 75),
                    cv2.FONT_HERSHEY_DUPLEX, 2.2, color, 3)

    if player_hand:
        hand_str = f"You: {player_hand}"
        cv2.putText(frame, hand_str, (20, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (220, 220, 220), 1)
    if dealer_upcard is not None:
        cv2.putText(frame, f"Dealer shows: {dealer_upcard}", (20, 148),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (220, 220, 220), 1)

    # Dim the whole panel area if hand is over
    return frame


model = YOLO("best.pt")

Y_coordinate = 650
left_X_coordinate = 700
right_X_coordinate = 900

print("Starting live vision... Press 'q' to quit, 'r' to reset hand.")

previous_card_count = 0
hand_is_over = False
stand = False
win = False
current_recommendation = None
current_player_hand = []
current_dealer_upcard = None

with mss.mss() as sct:
    monitor = sct.monitors[1]
    while True:
        screenshot = np.array(sct.grab(monitor))
        frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

        results = model(frame, verbose=False)

        dealer_cards = []
        my_cards = []

        for box in results[0].boxes:
            class_name = model.names[int(box.cls[0])]
            left_x_coord = box.xyxy[0][0].item()
            right_x_coord = box.xyxy[0][2].item()
            y_coord = box.xyxy[0][1].item()

            card_data = {"card": class_name, "x": left_x_coord}

            if y_coord < Y_coordinate:
                dealer_cards.append(card_data)
            else:
                if left_x_coord > left_X_coordinate and right_x_coord < right_X_coordinate:
                    my_cards.append(card_data)

        my_cards.sort(key=lambda c: c["x"])
        my_hand = [card_to_int(c["card"]) for c in my_cards]
        dealer_hand = [card_to_int(c["card"]) for c in dealer_cards]

        if (sum(my_hand) > 21):
            if 11 in my_hand:
                my_hand[my_hand.index(11)] = 1
            else:
                hand_is_over = True

        if (sum(my_hand) == 21):
            win = True


        if not hand_is_over and len(dealer_hand) >= 1 and len(my_hand) >= 2:
            if len(my_hand) > previous_card_count:
                dealer_upcard = dealer_hand[0]
                _, best_move = get_best_move(my_hand, dealer_upcard)

                current_recommendation = best_move
                current_player_hand = my_hand[:]
                current_dealer_upcard = dealer_upcard

                previous_card_count = len(my_hand)

                if best_move == "STAND":
                    stand = True
                else:
                    stand = False

        annotated_frame = results[0].plot(conf=False)
        draw_overlay(annotated_frame, current_recommendation,
                     current_player_hand, current_dealer_upcard, hand_is_over, stand, win)

        cv2.imshow("Stake Blackjack Vision", annotated_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            previous_card_count = 0
            hand_is_over = False
            current_recommendation = None
            current_player_hand = []
            current_dealer_upcard = None

cv2.destroyAllWindows()
