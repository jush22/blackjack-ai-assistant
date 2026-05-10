import cv2
import numpy as np
import mss

from ultralytics import YOLO
from percent_engine import *

def card_to_int(card_string):
    # Face cards are worth 10
    if card_string in ['J', 'Q', 'K', 'Jack', 'Queen', 'King']:
        return 10
    # Aces are usually calculated as 11 to start
    elif card_string in ['A', 'Ace']:
        return 11
    # Everything else (2 through 10) converts cleanly to an integer
    else:
        return int(card_string)


model = YOLO("best.pt")

Y_coordinate = 650
left_X_coordinate = 700
right_X_coordinate = 900
# 2. Define the Region of Interest (ROI)
# You don't want to scan your whole monitor, just the Blackjack table.
# You will need to tweak these numbers to fit exactly where the video plays on your screen.
print("Starting live vision... Press 'q' in the video window to quit.")

previous_card_count = 0
hand_is_over = False
empty_frame_counter = 0
# 3. Start the high-speed capture loop
with mss.mss() as sct:
    monitor = sct.monitors[1]
    while True:
        # Grab the specified area of the screen
        screenshot = np.array(sct.grab(monitor))

        # Convert mss format (BGRA) to OpenCV format (BGR)
        frame = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

        # 4. Run YOLO inference on the current frame
        # verbose=False stops it from spamming your terminal with text every millisecond
        results = model(frame, verbose=False)

        # 5. Extract the data and get X/Y coordinates
        dealer_cards = []
        my_hand = []
        my_cards = []
        # We need a threshold to decide what is "Top" (Dealer) and "Bottom" (Players)
        # You will need to tweak this number based on your specific screen capture

        for box in results[0].boxes:
            class_name = model.names[int(box.cls[0])]  # e.g., "10Hearts"
            left_x_coord = box.xyxy[0][0].item()  # Left edge of the box
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

        if len(results[0].boxes) == 0:
            empty_frame_counter += 1

        else:
            empty_frame_counter = 0


        if not hand_is_over and len(dealer_hand) >= 1 and len(my_hand) >= 2:
            if len(my_hand) > previous_card_count:
                dealer_upcard = dealer_hand[0]
                _, best_move = get_best_move(my_hand, dealer_upcard)

                print(f"Current Hand: {my_hand} | Dealer Shows: {dealer_upcard}")
                print(f"RECOMMENDED MOVE: {best_move}")

                # Lock the trigger until the next card is dealt
                previous_card_count = len(my_hand)

                # If the AI says to STAND or DOUBLE, the turn is over
                if best_move == "STAND":
                    hand_is_over = True

        # ... your existing sorting code ...
        my_cards.sort(key=lambda c: c["x"])
        my_hand = [c["card"] for c in my_cards]
        dealer_hand = [c["card"] for c in dealer_cards]





        if len(results[0].boxes) == 0:
            empty_frame_counter += 1

        # .plot() automatically draws the bounding boxes and labels on the frame
        annotated_frame = results[0].plot(conf=False)
        cv2.imshow("Stake Blackjack Vision", annotated_frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            previous_card_count = 0
            hand_is_over = False
            dealer_cards = []
            my_hand = []
            my_cards = []
            print("Table cleared. Waiting for the next hand...")

cv2.destroyAllWindows()