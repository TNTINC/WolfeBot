# WolfeBot
A telegram bot capable of sending truly awe inspiring quantities of random yiff. Also it can roleplay (sort of).
The master branch is hosted with the username @WolfeLegacyBot, and the dev branch is occasionaly live under @WolfeLegacyBBot.

The bot runs in python 3.5+ and works with the [aiotg](https://github.com/szastupov/aiotg) telegram bot framework.
## Dependencies
* aiotg
* colorama
* pillow
* markovify
## Some quick documentation
The main function of the bot (or at least the most frequently used) is the `/yiff` command. It's triggered whenever Wolfe gets a message matching the regex `/^(\/*)yiff/`. It then queries it's local sql daatabase for a random image and sends it. This database is built with `mediarefresh.py`,  which scans every subdirectory of `./res` for images.
> Note that it will try to find the image in telegram's cache before uploading it. This saves on bandwidth and makes the bot faster.

Replying to an image with `/fullsize` will make wolfe send said image again, uncompressed.
---
This is under heavy development at the moment, and isn't considered stable. Just FYI.
