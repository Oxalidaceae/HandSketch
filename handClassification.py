def classifyGesture(fingers_right, fingers_left, left_present=True):
    """
    fingers_right, fingers_left: 각 손의 손가락 상태 리스트 (ex: [1,0,1,0,0])
    left_present: 왼손이 실제 화면에 감지되었는지 여부
    return: 제스처 이름 (str)
    """
    total_right = sum(fingers_right)
    total_left = sum(fingers_left)

    # -------------------- 오른손 단독 제스처 --------------------
    if not left_present:
        if fingers_right == [1,1,0,0,0]:
            return 'draw'
        elif fingers_right == [1,1,1,0,0]:
            return 'erase_candidate'
        elif fingers_right == [1,1,1,1,0]:
            return 'thin'
        elif fingers_right == [1,1,1,1,1]:
            return 'medium'
        elif fingers_right == [0,1,1,1,1]:
            return 'thick'

    # -------------------- 양손 제스처 --------------------
    if left_present:
        if fingers_right == [1,0,0,0,0] and fingers_left == [0,0,0,0,0]:
            return 'palette'
        if fingers_right == [0,1,1,1,1] and fingers_left == [1,0,0,0,0]:
            return 'save_full'
        if fingers_right == [0,1,1,1,1] and fingers_left == [1,1,0,0,0]:
            return 'save_drawing'
        if fingers_right == [0,1,1,1,1] and fingers_left == [1,1,1,1,1]:
            return 'easter_egg'

    # -------------------- 특수 제스처 --------------------
    if (fingers_right == [0,1,1,1,1]) or (left_present and fingers_left == [1,1,1,1,1]):
        return 'clear_gesture_candidate'

    return 'none'