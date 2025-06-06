import cv2 as cv
import mediapipe as mp
import math

class handDetector():
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        # Initialization parameters
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.trackCon = trackCon

        # Mediapipe hand detection setup
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            static_image_mode=self.mode,
            max_num_hands=self.maxHands,
            min_detection_confidence=self.detectionCon,
            min_tracking_confidence=self.trackCon
        )
        self.mpDraw = mp.solutions.drawing_utils
        
        # Landmark tip indices for thumb and fingers
        self.tipIds = [4, 8, 12, 16, 20]

    def findHands(self, img, draw=True):
        # Convert BGR to RGB and process with Mediapipe
        imgRGB = cv.cvtColor(img, cv.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        # Draw hand landmarks if detected
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms, self.mpHands.HAND_CONNECTIONS)
        return img

    def findPositions(self, img, draw=True):
        # Reset lists
        self.lmLists = []
        self.bboxes = []
        self.handedness = []

        if self.results.multi_hand_landmarks:
            for idx, handLms in enumerate(self.results.multi_hand_landmarks):
                xList, yList, lmList = [], [], []
                for id, lm in enumerate(handLms.landmark):
                    h, w, _ = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    xList.append(cx)
                    yList.append(cy)
                    lmList.append([id, cx, cy])
                    if draw:
                        cv.circle(img, (cx, cy), 5, (255, 0, 255), cv.FILLED)
                if xList and yList:
                    # Compute bounding box for the hand
                    xmin, xmax = min(xList), max(xList)
                    ymin, ymax = min(yList), max(yList)
                    bbox = (xmin, ymin, xmax, ymax)
                    if draw:
                        cv.rectangle(img, (xmin - 20, ymin - 20), (xmax + 20, ymax + 20), (0, 255, 0), 2)
                    self.lmLists.append(lmList)
                    self.bboxes.append(bbox)

                    # Identify hand as "Left" or "Right"
                    label = self.results.multi_handedness[idx].classification[0].label
                    self.handedness.append(label)

        return self.lmLists, self.bboxes, self.handedness

    def fingersUp(self, lmList):
        # Determine which fingers are up
        fingers = []
        
        # Thumb: check x-axis (for right hand)
        if lmList[self.tipIds[0]][1] > lmList[self.tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
            
        # Other fingers: check y-axis
        for id in range(1, 5):
            if lmList[self.tipIds[id]][2] < lmList[self.tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        return fingers

    def findDistance(self, p1, p2, img, lmList, draw=True, r=15, t=3):
        # Get coordinates of two points
        x1, y1 = lmList[p1][1:]
        x2, y2 = lmList[p2][1:]
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

        if draw:
            # Draw line and circles between points
            cv.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
            cv.circle(img, (x1, y1), r, (255, 0, 255), cv.FILLED)
            cv.circle(img, (x2, y2), r, (255, 0, 255), cv.FILLED)
            cv.circle(img, (cx, cy), r, (0, 0, 255), cv.FILLED)

        # Return Euclidean distance and midpoint
        length = math.hypot(x2 - x1, y2 - y1)
        return length, img, [x1, y1, x2, y2, cx, cy]