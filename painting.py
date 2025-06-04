import cv2 as cv
import numpy as np
import handTracking as htm
import handClassification as hcf
import ironMan as im

# 설정
eraserThickness = 25
brushThickness = 25
eraserThickness = 100
canvasWidth = 1280
canvasHeight = 720

drawColor = (255, 255, 255)
xp, yp = 0, 0
mode = "draw"
palette_mode = False

imgCanvas = np.zeros((canvasHeight, canvasWidth, 3), np.uint8)

cap = cv.VideoCapture(0)
cap.set(3, canvasWidth)
cap.set(4, canvasHeight)

detector = htm.handDetector(detectionCon=0.65, maxHands=2)

frame_count = 0

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
        print("⚠️ 프레임을 읽지 못했습니다.")
        continue

    img = cv.flip(img, 1)
    img = detector.findHands(img)
    lmLists, _, handedness_list = detector.findPositions(img, draw=False)

    fingers_right, fingers_left = [0]*5, [0]*5
    lmList_right, lmList_left = [], []
    lmDict = {}

    for lmList, handLabel in zip(lmLists, handedness_list):
        if handLabel == "Right":
            fingers_right = detector.fingersUp(lmList)
            lmList_right = lmList
        elif handLabel == "Left":
            fingers_left = detector.fingersUp(lmList)
            lmList_left = lmList

    left_present = len(lmList_left) > 0
    gesture = hcf.classifyGesture(fingers_right, fingers_left, left_present=left_present)

    if not palette_mode:
        if gesture == 'erase_candidate' and lmList_right:
            length, _, _ = detector.findDistance(8, 12, img, lmList_right, draw=False)
            if length < 100:
                mode = "erase"
                print("🧽 지우개 모드")
            else:
                mode = "draw"
                print("✏️ 드로잉 모드")
        elif gesture == "draw":
            mode = "draw"
            print("✏️ 드로잉 모드")
        elif gesture == "thin":
            brushThickness = eraserThickness = 10
            print("얇은 브러시")
        elif gesture == "medium":
            brushThickness = eraserThickness = 25
            print("중간 브러시")
        elif gesture == "thick":
            brushThickness = eraserThickness = 45
            print("두꺼운 브러시")
        elif gesture == "palette":
            palette_mode = True
            print("🎨 색상 선택 모드 진입")
        elif gesture == "save_full":
            print("전체 저장 (배경 포함) - 1초 후 저장")
            #구현
        elif gesture == "save_drawing":
            print("드로잉만 저장")
            #구현
        elif gesture == "easter_egg":
            print("🪄 아이언맨 모드 발동")
            #구현

    if palette_mode and lmList_right:
        x1, y1 = lmList_right[8][1], lmList_right[8][2]

        for color_val, (x1_box, y1_box, x2_box, y2_box) in colors:
            cv.rectangle(img, (x1_box, y1_box), (x2_box, y2_box), color_val, cv.FILLED)
            if x1_box < x1 < x2_box and y1_box < y1 < y2_box:
                drawColor = color_val
                print("🎨 색상 변경:", color_val)

        x1_q, y1_q, x2_q, y2_q = quit_button_area
        cv.rectangle(img, (x1_q, y1_q), (x2_q, y2_q), (200, 0, 0), cv.FILLED)
        cv.putText(img, "QUIT", (x1_q + 10, y2_q - 15), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        if x1_q < x1 < x2_q and y1_q < y1 < y2_q:
            palette_mode = False
            print("❎ 색상 선택 모드 종료")

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

    cv.putText(img, f"Right: {fingers_right}", (10, 50), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
    cv.putText(img, f"Left:  {fingers_left}", (10, 80), cv.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

    frame_count += 1
    if frame_count % 10 == 0:
        print(f"[frame {frame_count}] 오른손: {fingers_right}, 왼손: {fingers_left}, 제스처: {gesture}")

    # 마스크 기반으로 완전한 덮어쓰기
    imgGray = cv.cvtColor(imgCanvas, cv.COLOR_BGR2GRAY)
    _, mask = cv.threshold(imgGray, 10, 255, cv.THRESH_BINARY)
    mask_inv = cv.bitwise_not(mask)

    mask_colored = cv.cvtColor(mask, cv.COLOR_GRAY2BGR)
    mask_inv_colored = cv.cvtColor(mask_inv, cv.COLOR_GRAY2BGR)

    # 원본 이미지에서 드로잉 부분 제거
    img_bg = cv.bitwise_and(img, mask_inv_colored)

    # 캔버스에서 드로잉 부분만 추출
    img_fg = cv.bitwise_and(imgCanvas, mask_colored)

    # 둘을 합성
    imgResult = cv.add(img_bg, img_fg)

    cv.imshow("Canvas", imgCanvas)
    cv.imshow("Image", imgResult)

    if cv.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv.destroyAllWindows()