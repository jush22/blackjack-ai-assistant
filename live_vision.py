import cv2
import numpy as np
import mss

from ultralytics import YOLO
from percent_engine import *

PANEL_W, PANEL_H = 380, 230

def card_to_int(card_string):
    if card_string in ['J', 'Q', 'K', 'Jack', 'Queen', 'King']:
        return 10
    elif card_string in ['A', 'Ace']:
        return 11
    else:
        return int(card_string)


def draw_overlay(frame, recommendation, player_hand, dealer_upcard,
                 hand_is_over, stand, win, waiting, mouse_xy):
    h, w = frame.shape[:2]
    px = w // 2 - PANEL_W // 2
    py = 10

    overlay = frame.copy()
    cv2.rectangle(overlay, (px, py), (px + PANEL_W, py + PANEL_H), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)
    cv2.rectangle(frame, (px, py), (px + PANEL_W, py + PANEL_H), (80, 80, 80), 2)

    # Status text
    if waiting:
        cv2.putText(frame, "Waiting for cards...", (px + 14, py + 55),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (180, 180, 180), 2)
    elif win:
        cv2.putText(frame, "YOU WIN!", (px + 60, py + 62),
                    cv2.FONT_HERSHEY_DUPLEX, 1.6, (80, 220, 80), 2)
    elif stand:
        cv2.putText(frame, "STAND!", (px + 60, py + 62),
                    cv2.FONT_HERSHEY_DUPLEX, 1.6, (0, 120, 255), 2)
    elif hand_is_over:
        cv2.putText(frame, "BUST!", (px + 90, py + 62),
                    cv2.FONT_HERSHEY_DUPLEX, 1.6, (50, 50, 255), 2)
    elif recommendation:
        color = (0, 220, 60) if recommendation == "HIT" else (0, 120, 255)
        cv2.putText(frame, recommendation, (px + 90, py + 72),
                    cv2.FONT_HERSHEY_DUPLEX, 2.4, color, 3)

    if player_hand:
        cv2.putText(frame, f"You: {player_hand}", (px + 14, py + 115),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (220, 220, 220), 1)
    if dealer_upcard is not None:
        cv2.putText(frame, f"Dealer shows: {dealer_upcard}", (px + 14, py + 143),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.65, (220, 220, 220), 1)

    # Buttons
    mx, my = mouse_xy
    btn_restart = (px + 10,       py + 185, px + 175,      py + 220)
    btn_stop    = (px + 185,      py + 185, px + PANEL_W - 10, py + 220)

    def is_hover(btn):
        return btn[0] <= mx <= btn[2] and btn[1] <= my <= btn[3]

    r_color = (0, 210, 90) if is_hover(btn_restart) else (0, 160, 60)
    cv2.rectangle(frame, (btn_restart[0], btn_restart[1]),
                  (btn_restart[2], btn_restart[3]), r_color, -1)
    cv2.rectangle(frame, (btn_restart[0], btn_restart[1]),
                  (btn_restart[2], btn_restart[3]), (255, 255, 255), 1)
    cv2.putText(frame, "New Hand", (btn_restart[0] + 14, btn_restart[1] + 26),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 0), 2)

    s_color = (60, 60, 220) if is_hover(btn_stop) else (40, 40, 170)
    cv2.rectangle(frame, (btn_stop[0], btn_stop[1]),
                  (btn_stop[2], btn_stop[3]), s_color, -1)
    cv2.rectangle(frame, (btn_stop[0], btn_stop[1]),
                  (btn_stop[2], btn_stop[3]), (255, 255, 255), 1)
    cv2.putText(frame, "Stop", (btn_stop[0] + 30, btn_stop[1] + 26),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, (255, 255, 255), 2)

    # Return button rects so the main loop can hit-test clicks
    return btn_restart, btn_stop


model = YOLO("best.pt")

Y_coordinate = 650
left_X_coordinate = 700
right_X_coordinate = 900

print("Starting live vision...")

previous_card_count = 0
hand_is_over = False
stand = False
win = False
waiting = True
current_recommendation = None
current_player_hand = []
current_dealer_upcard = None

mouse_state = {"x": 0, "y": 0, "clicked": None, "btn_restart": None, "btn_stop": None}

def mouse_callback(event, x, y, flags, param):
    mouse_state["x"] = x
    mouse_state["y"] = y
    if event == cv2.EVENT_LBUTTONDOWN:
        br = mouse_state["btn_restart"]
        bs = mouse_state["btn_stop"]
        if br and br[0] <= x <= br[2] and br[1] <= y <= br[3]:
            mouse_state["clicked"] = "restart"
        elif bs and bs[0] <= x <= bs[2] and bs[1] <= y <= bs[3]:
            mouse_state["clicked"] = "stop"

cv2.namedWindow("Stake Blackjack Vision")
cv2.setMouseCallback("Stake Blackjack Vision", mouse_callback)

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

        if sum(my_hand) > 21:
            if 11 in my_hand:
                my_hand[my_hand.index(11)] = 1
            else:
                hand_is_over = True

        if sum(my_hand) == 21:
            win = True

        if not hand_is_over and len(dealer_hand) >= 1 and len(my_hand) >= 2:
            if len(my_hand) > previous_card_count:
                dealer_upcard = dealer_hand[0]
                _, best_move = get_best_move(my_hand, dealer_upcard)

                current_recommendation = best_move
                current_player_hand = my_hand[:]
                current_dealer_upcard = dealer_upcard
                waiting = False

                previous_card_count = len(my_hand)

                if best_move == "STAND":
                    stand = True
                else:
                    stand = False

        annotated_frame = results[0].plot(conf=False)
        btn_restart, btn_stop = draw_overlay(
            annotated_frame, current_recommendation,
            current_player_hand, current_dealer_upcard,
            hand_is_over, stand, win, waiting,
            (mouse_state["x"], mouse_state["y"]))
        mouse_state["btn_restart"] = btn_restart
        mouse_state["btn_stop"] = btn_stop

        cv2.imshow("Stake Blackjack Vision", annotated_frame)

        # Handle button clicks
        if mouse_state["clicked"] == "restart":
            mouse_state["clicked"] = None
            previous_card_count = 0
            hand_is_over = False
            stand = False
            win = False
            waiting = True
            current_recommendation = None
            current_player_hand = []
            current_dealer_upcard = None
        elif mouse_state["clicked"] == "stop":
            break

        cv2.waitKey(1)

cv2.destroyAllWindows()
