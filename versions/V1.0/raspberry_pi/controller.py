def get_frame_center(frame):
    """
    获取图像中心点

    输入:
        frame -> 当前图像帧

    输出:
        (cx, cy)
    """
    height, width = frame.shape[:2]
    cx = width // 2
    cy = height // 2
    return (cx, cy)


def compute_error(frame_center, target_center):
    """
    计算目标相对图像中心的偏差

    输入:
        frame_center  -> (cx, cy)
        target_center -> (tx, ty)

    输出:
        dx, dy
    """
    cx, cy = frame_center
    tx, ty = target_center

    dx = tx - cx
    dy = ty - cy

    return dx, dy


def map_single_axis(error, deadzone, th_small, th_medium, step_small, step_medium, step_large):
    """
    单轴误差映射函数

    输入:
        error      -> 当前轴误差
        deadzone   -> 死区
        th_small   -> 小误差阈值
        th_medium  -> 中误差阈值
        step_small -> 小步长
        step_medium-> 中步长
        step_large -> 大步长

    输出:
        delta
    """
    abs_error = abs(error)

    # 死区内不动
    if abs_error < deadzone:
        return 0

    # 根据误差大小分级
    if abs_error < th_small:
        step = step_small
    elif abs_error < th_medium:
        step = step_medium
    else:
        step = step_large

    # 保留方向
    if error > 0:
        return step
    else:
        return -step


def map_error_to_increment(dx, dy, config):
    """
    将图像误差 dx, dy 映射成 pan_delta, tilt_delta

    输入:
        dx
        dy
        config -> 参数字典

    输出:
        pan_delta, tilt_delta
    """
    pan_delta = map_single_axis(
        error=dx,
        deadzone=config["DEADZONE_X"],
        th_small=config["THRESHOLD_X_SMALL"],
        th_medium=config["THRESHOLD_X_MEDIUM"],
        step_small=config["STEP_SMALL"],
        step_medium=config["STEP_MEDIUM"],
        step_large=config["STEP_LARGE"]
    )

    tilt_delta = map_single_axis(
        error=dy,
        deadzone=config["DEADZONE_Y"],
        th_small=config["THRESHOLD_Y_SMALL"],
        th_medium=config["THRESHOLD_Y_MEDIUM"],
        step_small=config["STEP_SMALL"],
        step_medium=config["STEP_MEDIUM"],
        step_large=config["STEP_LARGE"]
    )

    return pan_delta, tilt_delta


def build_command(pan_delta, tilt_delta):
    """
    构造 V0.4/V0.5 协议字符串

    输出示例:
        +10,-4
        0,+20
        -8,0
    """
    return f"{pan_delta:+d},{tilt_delta:+d}"


def compute_command(frame, target_center, config):
    """
    一站式计算:
    frame + target_center -> dx, dy -> pan_delta, tilt_delta -> command

    输出:
        {
            "frame_center": (cx, cy),
            "dx": dx,
            "dy": dy,
            "pan_delta": pan_delta,
            "tilt_delta": tilt_delta,
            "command": command
        }
    """
    frame_center = get_frame_center(frame)
    dx, dy = compute_error(frame_center, target_center)
    pan_delta, tilt_delta = map_error_to_increment(dx, dy, config)
    command = build_command(pan_delta, tilt_delta)

    return {
        "frame_center": frame_center,
        "dx": dx,
        "dy": dy,
        "pan_delta": pan_delta,
        "tilt_delta": tilt_delta,
        "command": command
    }
