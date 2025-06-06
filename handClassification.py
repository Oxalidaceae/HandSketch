def classifyGesture(fingers_right, fingers_left, left_present=True):
    """
    fingers_right, fingers_left: List of finger states for each hand (e.g., [1,0,1,0,0])
    left_present: Whether the left hand is detected in the frame
    return: Name of the recognized gesture (str)
    """

    # Single-hand gestures (right hand only)
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

    # Two-hand gestures (both hands present)
    if left_present:
        if fingers_right == [1,0,0,0,0] and fingers_left == [0,0,0,0,0]:
            return 'palette'
        if fingers_right == [0,1,1,1,1] and fingers_left == [1,0,0,0,0]:
            return 'save_full'
        if fingers_right == [0,1,1,1,1] and fingers_left == [1,1,0,0,0]:
            return 'save_drawing'

    return 'none'