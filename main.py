#!./.venv/bin/python3
import multiprocessing as mp
import platform

from src.fakesparkles import twitchchatplay

if __name__ == "__main__":
    # This is to prevent infinite bootloop
    if platform.platform().startswith("Windows"):
        mp.freeze_support()

    twitchchatplay.main()
