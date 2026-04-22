# app/services/xp_service.py


def calculate_xp(action: str):
    base = {
        "flow_run": 5,
        "content_generated": 10,
        "export": 8,
        "flow_created": 20,
    }
    return base.get(action, 0)


def level_up_threshold(level: int):
    return int(100 * (level**1.5))


async def process_xp_event(event):
    user = get_user(event.user_id)

    xp_gain = calculate_xp(event.action)

    user["xp"] += xp_gain

    leveled_up = False

    # level up loop (handles multiple levels)
    while user["xp"] >= user["next_level_xp"]:
        user["xp"] -= user["next_level_xp"]
        user["level"] += 1
        user["next_level_xp"] = level_up_threshold(user["level"])
        leveled_up = True

    save_user(user)

    return {
        "xp_gained": xp_gain,
        "xp": user["xp"],
        "level": user["level"],
        "next_level_xp": user["next_level_xp"],
        "leveled_up": leveled_up,
    }
