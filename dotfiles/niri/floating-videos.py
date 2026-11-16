#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import time

# Default offsets (px)
OFFSET_TOP = 16
OFFSET_BOTTOM = 52
OFFSET_LEFT = 17
OFFSET_RIGHT = 17

# Only for video pip
VIDEO_TITLE_RE = re.compile(r"(picture[- ]in[- ]picture|картинка в картинке)", re.IGNORECASE)
VIDEO_APP_RE = re.compile(r"^(mpv)$", re.IGNORECASE)

# {win_id: slot}
window_slots = {}

def parse_args():
    parser = argparse.ArgumentParser(description="Niri PiP window manager")
    parser.add_argument("-t", "--top", type=int, default=OFFSET_TOP, help="Top offset in px")
    parser.add_argument("-b", "--bottom", type=int, default=OFFSET_BOTTOM, help="Bottom offset in px")
    parser.add_argument("-l", "--left", type=int, default=OFFSET_LEFT, help="Left offset in px")
    parser.add_argument("-r", "--right", type=int, default=OFFSET_RIGHT, help="Right offset in px")
    return parser.parse_args()

def is_video_pip(win):
    if not win or not win.get("is_floating"):
        return False
    title = win.get("title") or ""
    app_id = win.get("app_id") or ""
    return bool(VIDEO_TITLE_RE.search(title) or VIDEO_APP_RE.match(app_id))

def niri_json(cmd):
    res = subprocess.run(["niri", "msg", "-j", cmd], capture_output=True, text=True)
    return json.loads(res.stdout) if res.returncode == 0 else None

def get_free_slot(ws_id, all_windows, allow_middle):
    # Slots order: 0:BR, 1:MR, 2:TR, 3:BL, 4:ML, 5:TL
    available_slots = [0, 1, 2, 3, 4, 5] if allow_middle else [0, 2, 3, 5]

    active_ids = {
        w.get("id") for w in all_windows
        if w.get("workspace_id") == ws_id and is_video_pip(w)
    }

    # Clean closed or moved windows
    for wid in list(window_slots.keys()):
        if wid not in active_ids:
            del window_slots[wid]

    # Count occupancy per slot for wrap-around
    counts = {s: 0 for s in available_slots}
    for slot in window_slots.values():
        if slot in counts:
            counts[slot] += 1

    # Pick least occupied slot in order
    min_count = min(counts.values())
    for s in available_slots:
        if counts[s] == min_count:
            return s
    return 0

def main():
    args = parse_args()

    proc = subprocess.Popen(
        ["niri", "msg", "-j", "event-stream"],
        stdout=subprocess.PIPE,
        text=True,
        bufsize=1
    )

    for line in proc.stdout:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue

        # Mem free
        if "WindowClosed" in event:
            window_slots.pop(event["WindowClosed"].get("id"), None)
            continue

        # Awake only on events
        win_event = event.get("WindowOpenedOrChanged")
        if not win_event:
            continue

        win = win_event.get("window", {})
        win_id = win.get("id")

        if not is_video_pip(win) or win_id in window_slots:
            continue

        # Wait for final size
        time.sleep(0.08)

        all_windows = niri_json("windows") or []
        fresh_win = next((w for w in all_windows if w.get("id") == win_id), win)
        ws_id = fresh_win.get("workspace_id")

        output = niri_json("focused-output")
        if not output:
            continue

        screen_w = output["logical"]["width"]
        screen_h = output["logical"]["height"]
        win_size = fresh_win.get("layout", {}).get("window_size") or [400, 225]
        win_w, win_h = win_size[0], win_size[1]

        # Check if 3 windows fit vertically with gaps
        usable_h = screen_h - args.top - args.bottom
        min_gap = 10
        allow_middle = usable_h >= (win_h * 3 + min_gap * 2)

        slot = get_free_slot(ws_id, all_windows, allow_middle)
        window_slots[win_id] = slot

        # Calculate coordinates
        x_right = screen_w - win_w - args.right
        x_left = args.left
        y_bottom = screen_h - win_h - args.bottom
        y_top = args.top
        y_middle = args.top + (usable_h - win_h) / 2

        if slot == 0:
            x, y = x_right, y_bottom   # 1st: bottom-right
        elif slot == 1:
            x, y = x_right, y_middle   # 2nd: middle-right
        elif slot == 2:
            x, y = x_right, y_top      # 3rd: top-right
        elif slot == 3:
            x, y = x_left, y_bottom    # 4th: bottom-left
        elif slot == 4:
            x, y = x_left, y_middle    # 5th: middle-left
        else:
            x, y = x_left, y_top       # 6th: top-left

        # Clamp to screen bounds
        x = max(0, min(x, screen_w - win_w))
        y = max(0, min(y, screen_h - win_h))

        subprocess.run([
            "niri", "msg", "action", "move-floating-window",
            "--id", str(win_id), "-x", str(int(x)), "-y", str(int(y))
        ])

if __name__ == "__main__":
    main()
