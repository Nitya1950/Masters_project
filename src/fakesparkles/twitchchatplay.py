#!./.venv/bin/python3
import concurrent.futures as cf
import contextlib
import functools
import pprint
import time
from typing import NoReturn
from twitchirc_drgreengiant import offlineirc, twitchirc
import config
import environment
import errorcodes
import gui
import twitchactions

VERSION = environment.getenv("VERSION", "0.0.0dev")

MAX_QUEUE_LENGTH = 20
MAX_WORKERS = 100
MESSAGE_RATE = 0.5
last_time = time.time()
message_queue = []
thread_pool = cf.ThreadPoolExecutor(max_workers=MAX_WORKERS)
active_tasks = []

def done_callback(future: cf.Future, msg: twitchirc.TwitchMessage, tag: str) -> None:
    """Callback for when a command is done"""
    result: errorcodes.ErrorSet = future.result()

    if errorcodes.success(result):
        print(f"Done \'{tag}\' from {msg.username}")
    else:
        print(f"Failed \'{tag}\' from {msg.username} ({result=})")


def make_commands_str(myconfig: config.Config) -> str:
    """Make a command string to paste into chat"""
    ret = pprint.pformat([value.twitch.command[0] for value in myconfig.config.values()], compact=True)
    return ret.replace("'", "").replace("[", "").replace("]", "")


def preamble(myconfig: config.Config) -> str:
    """Make the preamble"""
    return f"""\n\t\t---  ---\n
#\tTwitch chat plays with
#\tcommands, for live game streams.


Valid commands are:
{make_commands_str(myconfig)}

Channels set in config.toml:
{', '.join(myconfig.channel)}
"""


def channel_connected(myconfig: config.Config) -> None:
    """Channel connecting to the program"""
    return f"""Connected to Twitch channel{'s' if len(myconfig.channel) > 1 else ''}: {', '.join(myconfig.channel)}\n
    Superuser{'s' if len(myconfig.superusers) > 1 else ''}: {', '.join(myconfig.superusers)}\n
    """


def get_action_from_message(myconfig: config.Config, msg: twitchirc.TwitchMessage) -> tuple[twitchactions.TwitchAction, str] | None:
    """Get the action from a message

    Args:
        myconfig (config.Config): The loaded configuration
        msg (twitchirc.TwitchMessage): The incoming Twitch message

    Returns:
        tuple[twitchactions.TwitchAction, str] | None: A tuple containing the Twitch action to take and the tag of the command, or None if no action should be taken

    Raises:
        ValueError: If the incoming message contains an invalid command
    """
    tag = myconfig.find_tag_by_command(msg.payload.lower().removeprefix(myconfig.superuser_prefix))
    sudo: bool = msg.payload.strip().lower().startswith(myconfig.superuser_prefix) and msg.username.strip().lower() in myconfig.superusers

    if not tag:
        if msg.username.strip().lower() in myconfig.bots:
            tag = "random"
            sudo = False
        else:
            return None
    elif tag == "random" and not sudo:
        return None

    if not myconfig.enabled:
        print(f"Commands disabled!  Ignoring \'{tag}\' from {msg.username}")
        return None

    if config.check_blocklist(msg.username, abort=False, silent=True):
        return None

    print(f"Running {'superuser ' if sudo else ''}\'{tag}\' from {msg.username}{' in channel ' + msg.channel if len(myconfig.channel) > 1 else ''}")

    return functools.partial(myconfig.actions[tag].run, force=sudo), tag


def main() -> NoReturn:
    """
    Main function of the program.

    This function initializes the program by loading the configuration file, creating the GUI, and starting the main loop.

    Args:
        None

    Returns:
        None

    Raises:
        SystemExit: If the GUI is closed, this exception is raised to exit the program.
    """
    myconfig = config.Config.load(VERSION)
    myconfig.save(backup_old=True)

    print(preamble(myconfig))

    with contextlib.ExitStack() as stack:
        executor = stack.enter_context(cf.ThreadPoolExecutor(max_workers=1))
        irc = None
        if config.OFFLINE:
            print("OFFLINE MODE")
            irc = stack.enter_context(offlineirc.OfflineIrc(myconfig.channel, username="fakesparkles"))
        else:
            irc = stack.enter_context(twitchirc.TwitchIrc(myconfig.channel))

        print(channel_connected(myconfig))

        mygui, exit_event, redraw_gui = gui.make_gui(myconfig)

        while True:
            redraw_gui()  # Needed in order to click on buttons

            if exit_event.is_set():
                print("GUI closed, exiting...")
                raise SystemExit

            msg = irc.get_message(irc)

            if not msg:
                continue

            config.check_blocklist(myconfig.channel)
            config.check_blocklist(msg.channel)

            if actiontag := get_action_from_message(myconfig, msg):
                action, tag = actiontag
                executor.submit(action).add_done_callback(
                    functools.partial(done_callback, msg=msg, tag=tag)
                )


if __name__ == "__main__":
    main()
