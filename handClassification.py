def classifyGesture(fingers_right, fingers_left):
    """
    fingers_right, fingers_left: 각 손의 손가락 상태 리스트 (ex: [1,0,1,0,0])
    return: 제스처 이름 (str)
    """
    total_right = sum(fingers_right)
    total_left = sum(fingers_left)
    
    # -------------------- 오른손 단독 제스처 --------------------
    if total_left == 0:
        if fingers_right == [1,1,0,0,0]:
            return 'draw'  # 기본 드로잉
        elif fingers_right == [1,1,1,0,0]:
            return 'erase_candidate'  # 지우개 모드
        elif fingers_right == [1,1,1,1,0]:
            return 'thin'   # 얇은 브러시/지우개
        elif fingers_right == [1,1,1,1,1]:
            return 'medium' # 중간 브러시/지우개
        elif fingers_right == [0,1,1,1,1]:
            return 'thick'  # 두꺼운 브러시/지우개

    # -------------------- 양손 제스처 --------------------
    if fingers_right == [1,0,0,0,0] and fingers_left == [0,0,0,0,0]:
        return 'palette'  # 색상 팔레트 진입

    if fingers_right == [0,1,1,1,1] and fingers_left == [1,0,0,0,0]:
        return 'save_full'  # 배경 포함 저장
    if fingers_right == [0,1,1,1,1] and fingers_left == [1,1,0,0,0]:
        return 'save_drawing'  # 그림만 저장

    if fingers_right == [0,1,1,1,1] and fingers_left == [1,1,1,1,1]:
        return 'easter_egg'  # 양손 다 핌 (아이언맨 이펙트)

    # -------------------- 특수 제스처 --------------------
    if fingers_right == [0,1,1,1,1] or fingers_left == [1,1,1,1,1]:
        # ⚠️ 쓸기 여부는 painting.py에서 프레임 간 위치 이동량으로 판단해야 함
        return 'clear_gesture_candidate'  # 후보자 — 실제 쓸기 감지는 별도 처리

    return 'none'  # 인식된 제스처 없음