import time
import numpy as np
import cv2

class IronManEffect:
    def __init__(self, canvas_width=1280, canvas_height=720, cooldown_sec=10, activation_time_sec=1):
        # Cooldown and activation timing
        self.cooldown = cooldown_sec
        self.activation_time = activation_time_sec
        self.last_activation_time = 0
        self.both_hands_start_time = None
        
        # Canvas size
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height

    def update(self, fingers_right, fingers_left, lmList_right, lmList_left, frame, imgCanvas):
        now = time.time()
        
        # Check if both hands are open (Iron Man trigger pose)
        both_hands_open = fingers_right == [0, 1, 1, 1, 1] and fingers_left == [1, 1, 1, 1, 1]

        # Track how long the gesture is held
        if both_hands_open:
            if self.both_hands_start_time is None:
                self.both_hands_start_time = now
        else:
            self.both_hands_start_time = None

        # Draw beam visuals on frame
        if both_hands_open:
            frame = self.draw_beam(frame, lmList_right)
            frame = self.draw_beam(frame, lmList_left)

        # Check if gesture held long enough and cooldown passed
        if self.both_hands_start_time:
            held_duration = now - self.both_hands_start_time
            cooldown_ready = now - self.last_activation_time > self.cooldown

            if held_duration >= self.activation_time and cooldown_ready:
                self.last_activation_time = now
                self.both_hands_start_time = None
                imgCanvas = np.zeros((self.canvas_height, self.canvas_width, 3), np.uint8)
                print("💥 Iron Man Beam Triggered — Canvas Cleared")
                return frame, imgCanvas, True

        return frame, imgCanvas, False

    def draw_beam(self, frame, lmList, color=(0, 255, 255)):
        if not lmList or len(lmList) < 10:
            return frame

        # Compute center point of the palm (between wrist and middle finger MCP)
        x0, y0 = lmList[0][1], lmList[0][2]
        x9, y9 = lmList[9][1], lmList[9][2]
        cx, cy = (x0 + x9) // 2, (y0 + y9) // 2

        # Compute normalized direction vector
        dx, dy = x9 - x0, y9 - y0
        norm = np.hypot(dx, dy)
        if norm == 0:
            return frame

        dx /= norm
        dy /= norm
        beam_length = 500
        ex = int(cx + dx * beam_length)
        ey = int(cy + dy * beam_length)

        # Main beam
        cv2.line(frame, (cx, cy), (ex, ey), color, 20)

        # Glow at the palm center
        glow_color = tuple(int(c * 0.6) for c in color)
        overlay = frame.copy()
        cv2.circle(overlay, (cx, cy), 60, glow_color, -1)
        cv2.circle(overlay, (cx, cy), 30, color, -1)
        frame = cv2.addWeighted(overlay, 0.4, frame, 0.6, 0)

        # Glow at the end of the beam
        glow_overlay = frame.copy()
        cv2.circle(glow_overlay, (ex, ey), 40, color, -1)
        frame = cv2.addWeighted(glow_overlay, 0.3, frame, 0.7, 0)

        return frame