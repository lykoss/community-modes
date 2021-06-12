# Lykos community modes
This repository contains unofficial game modes made by the lykos community.

## Using these modes
To use these modes in your own bot, download the mode files you want and put them
into the `gamemodes/` directory of your bot (**NOT** `src/gamemodes`). Then, copy
`gamemodes/__init__.py.example` to `gamemodes/__init__.py` so your bot loads them.

At this time, community mode files will not be updated when you run the `!update`
command; we're working on how best to make that happen.

## File descriptions
The following files are available in this repository:

- classicfire.py: A twist on default reflecting changes made in April Fools 2020.
- shootout.py: Everyone has a gun, try to be the last one standing! For 2+ players.
- totemfire.py: 3 unique modes each with lots of crazed shamans and lots of totems.

## Contributing
If you would like to contribute modes to this repository, please adhere to the
following guidelines:

- Mode files should be self-contained, including any messages and metadata keys
  they may need to add. See existing files for an example.
- Test your mode before submitting on the latest version of the bot to ensure it
  works correctly. Remember that the bot supports Python 3.7 and later, so your
  mode should as well.
- Add an entry into the "File descriptions" section of this README describing your
  mode.
- Try to choose distinctive mode names that do not override built-in modes or other
  modes present in this repository.
