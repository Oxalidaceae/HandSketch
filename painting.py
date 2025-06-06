import cv2 as cv
import numpy as np
import handTracking as htm
import handClassification as hcf
import ironMan as im
import time

# Brush & canvas settings
eraserThickness = 25
brushThickness = 25
canvasWidth = 1280
canvasHeight = 720

# Save timers and drawing state
save_timer = None
save_start_time = None
save_countdown_position = (1100, 700)
last_drawing_save_time = 0

# Drawing mode & state
drawColor = (255, 255, 255)
xp, yp = 0, 0
mode = "draw"
palette_mode = False

# Blank canvas for drawing
imgCanvas = np.zeros((canvasHeight, canvasWidth, 3), np.uint8)

# Camera setup
cap = cv.VideoCapture(0)
cap.set(3, canvasWidth)
cap.set(4, canvasHeight)

# Hand tracker and Iron Man effect
detector = htm.handDetector(detectionCon=0.65, maxHands=2)
iron_effect = im.IronManEffect(canvas_width=canvasWidth, canvas_height=canvasHeight)

# Color palette rectangles: ((BGR color), (x1, y1, x2, y2))
colors = [
    ((0, 0, 255), (20, 20, 100, 100)),
    ((0, 165, 255), (120, 20, 200, 100)),
    ((0, 255, 255), (220, 20, 300, 100)),
    ((0, 255, 0), (320, 20, 400, 100)),
    ((255, 151, 0), (420, 20, 500, 100)),
    ((153, 0, 0), (520, 20, 600, 100)),
    ((255, 0, 127), (620, 20, 700, 100)),
    ((255, 0, 255), (720, 20, 800, 100)),
    ((255, 255, 255), (820, 20, 900, 100))
]

quit_button_area = (20, 120, 120, 170)

while True:
    success, img = cap.read()
    if not success:
        print("⚠️ Can't read frame.")
        continue

    img = cv.flip(img, 1)
    img = detector.findHands(img)
    lmLists, _, handedness_list = detector.findPositions(img, draw=False)

    # Finger status and landmarks
    fingers_right, fingers_left = [0]*5, [0]*5
    lmList_right, lmList_left = [], []
    lmDict = {}

    # Separate left and right hands
    for lmList, handLabel in zip(lmLists, handedness_list):
        if handLabel == "Right":
            fingers_right = detector.fingersUp(lmList)
            lmList_right = lmList
        elif handLabel == "Left":
            fingers_left = detector.fingersUp(lmList)
            lmList_left = lmList

    left_present = len(lmList_left) > 0
    gesture = hcf.classifyGesture(fingers_right, fingers_left, left_present=left_present)

    # Check Iron Man beam trigger every frame
    img, imgCanvas, _ = iron_effect.update(
        fingers_right, fingers_left,
        lmList_right, lmList_left,
        img, imgCanvas
    )

    # Handle drawing modes
    if not palette_mode:
        if gesture == 'erase_candidate' and lmList_right:
            length, _, _ = detector.findDistance(8, 12, img, lmList_right, draw=False)
            if length < 100:
                mode = "erase"
                print("🧽 Erase Mode")
            else:
                mode = "draw"
                print("✏️ Drawing Mode")
        elif gesture == "draw":
            mode = "draw"
            print("✏️ Drawing Mode")
        elif gesture == "thin":
            brushThickness = eraserThickness = 10
            print("Thin Brush")
        elif gesture == "medium":
            brushThickness = eraserThickness = 25
            print("Medium Brush")
        elif gesture == "thick":
            brushThickness = eraserThickness = 45
            print("Thick Brush")
        elif gesture == "palette":
            palette_mode = True
            print("🎨 Color Select Mode")
        elif gesture == "save_full":
            if save_timer is None:
                save_start_time = time.time()
                save_timer = True
                print("🖼️ Save full canvas (3s later)")
        elif gesture == "save_drawing":
            now = time.time()
            if now - last_drawing_save_time >= 5:
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                random_id = np.random.randint(1000, 9999)
                save_path = f"drawing_only_{timestamp}_{random_id}.png"
                cv.imwrite(save_path, imgCanvas)
                print(f"🖌️ Save only drawing: {save_path}")
                last_drawing_save_time = now
            else:
                remaining = 5 - (now - last_drawing_save_time)
                print(f"⏳ Saving cooltime: {remaining:.1f}seconds left")

    # Handle drawing and erasing
    if mode in ["draw", "erase"] and not palette_mode and lmList_right:
        lmDict = {id: (x, y) for id, x, y in lmList_right}
        if 8 in lmDict and 12 in lmDict:
            x1, y1 = lmDict[8]
            if fingers_right[1] and not fingers_right[2] or mode == "erase":
                thickness = eraserThickness if mode == "erase" else brushThickness
                color = (0, 0, 0) if mode == "erase" else drawColor

                cv.circle(img, (x1, y1), thickness // 2, (0, 0, 0), cv.FILLED)

                if xp == 0 and yp == 0:
                    xp, yp = x1, y1

                # Draw lines on both the original and canvas
                cv.line(img, (xp, yp), (x1, y1), color, thickness)
                cv.line(imgCanvas, (xp, yp), (x1, y1), color, thickness)

                xp, yp = x1, y1
            else:
                xp, yp = 0, 0
        else:
            xp, yp = 0, 0
    else:
        xp, yp = 0, 0

    if mode in ["draw", "erase"] and not palette_mode and lmList_right:
        if 8 in lmDict:
            x1, y1 = lmDict[8]
            thickness = eraserThickness if mode == "erase" else brushThickness
            cv.circle(img, (x1, y1), thickness // 2, (0, 0, 0), cv.FILLED)

    # Combine canvas with webcam frame
    imgGray = cv.cvtColor(imgCanvas, cv.COLOR_BGR2GRAY)
    _, mask = cv.threshold(imgGray, 10, 255, cv.THRESH_BINARY)
    mask_inv = cv.bitwise_not(mask)

    mask_colored = cv.cvtColor(mask, cv.COLOR_GRAY2BGR)
    mask_inv_colored = cv.cvtColor(mask_inv, cv.COLOR_GRAY2BGR)

    img_bg = cv.bitwise_and(img, mask_inv_colored)
    img_fg = cv.bitwise_and(imgCanvas, mask_colored)
    imgResult = cv.add(img_bg, img_fg)

    # Handle countdown for full canvas save
    if save_timer:
        elapsed = time.time() - save_start_time
        if elapsed < 3:
            remaining = max(0, 3 - elapsed)
            cv.putText(imgResult, f"{remaining:.1f}", save_countdown_position,
                    cv.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)
        else:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            random_id = np.random.randint(1000, 9999)
            save_path = f"canvas_full_{timestamp}_{random_id}.png"
            cv.imwrite(save_path, imgResult)
            print(f"💾 Full canvas saved: {save_path}")
            save_timer = None

    # Handle color selection UI
    if palette_mode and lmList_right:
        x1, y1 = lmList_right[8][1], lmList_right[8][2]

        for color_val, (x1_box, y1_box, x2_box, y2_box) in colors:
            cv.rectangle(imgResult, (x1_box, y1_box), (x2_box, y2_box), color_val, cv.FILLED)
            if x1_box < x1 < x2_box and y1_box < y1 < y2_box:
                drawColor = color_val
                print("🎨 Color changed:", color_val)

        # Quit color selection mode
        x1_q, y1_q, x2_q, y2_q = quit_button_area
        cv.rectangle(imgResult, (x1_q, y1_q), (x2_q, y2_q), (200, 0, 0), cv.FILLED)
        cv.putText(imgResult, "QUIT", (x1_q + 10, y2_q - 15), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        if x1_q < x1 < x2_q and y1_q < y1 < y2_q:
            palette_mode = False
            print("❎ Exit color select mode")

    # Show result
    cv.imshow("Canvas", imgCanvas)
    cv.imshow("Image", imgResult)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()