# Crowdsourced Gaming on Twitch

Taking inspiration from the many other "TwitchPlays" style programmes, this software application has been specifically created to be an easy to use for the gaming community. This project delves into enhancing the interactive dynamics of Twitch live streams by enabling viewers to actively influence gameplay. Utilizing Python, the project integrates Twitch API functionalities to facilitate real-time interaction between chat participants and gameplay actions. 


## 🔮 How it works

This project works by talking directly to the operating system *as if* it were a mouse or keyboard plugged into your machine. The twitch username should be updated to your own to connect it and read your channel chat messgaes for input. Just open up the gui application and setup the keybinds for different controls of the gameplay and let it run with your livestream! You'll enable your live audience to interact with your game using the keybinds you setup to them and increase viewer engagement.

*Note: This code does not modify any game code nor any files on your computer. It has been tested in Windows.*

## 🫧 Installations
The following python packages need to be installed using pip.

```bash
pip install config
pip install pynput
pip install keyboard
pip install twitchirc
```
## 💟 Contributing and Thanks


> - Wituz's "Twitch Plays" tutorial: <http://www.wituz.com/make-your-own-twitch-plays-stream.html>
> - PythonProgramming's "Python Plays GTA V" tutorial: <https://pythonprogramming.net/direct-input-game-python-plays-gta-v/>
> - DDarknut's message queue and updates to the Twitch networking code
