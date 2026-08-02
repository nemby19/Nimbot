FILE_NAME = "last_video.txt"
LIVE_FILE = "last_live.txt"


def load_last_video():
    try:
        with open(FILE_NAME, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None


def save_last_video(video_id):
    with open(FILE_NAME, "w") as file:
        file.write(video_id)


def load_last_live():
    try:
        with open(LIVE_FILE, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return None


def save_last_live(video_id):
    with open(LIVE_FILE, "w") as file:
        file.write(video_id)