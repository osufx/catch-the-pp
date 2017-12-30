# Cythonized catch-the-pp
An osu ctb gamemode star/pp calculator made in Cython.  
Original repo: [catch-the-pp](https://github.com/osufx/catch-the-pp) by [Sunpy](https://github.com/EmilySunpy).  
*Note: This repo is meant to be used as a Python package, not as a standalone program!*

## Changes
- Cythonized all files, functions, classes and methods (with static typing as well)
- Replaced `math.pow` with `**`, this gives _a bit_ of extra speed
- Replaced imports
- Minor code cleaning

## Performance
These are the execution times after running pp calculation (with beatmap parsing and difficulty calculation as well) on `reanimate.osu` 100 times  
Pure Python version: `Min: 0.7986021041870117 s, Max: 0.932903528213501 s, Avg: 0.8350819730758667 s`  
Cythonized version: `Min: 0.22933077812194824 s, Max: 0.25774192810058594 s, Avg: 0.23836223363876344 s`


## Compiling & Usage
```
$ git clone ... catch_the_pp
$ cd catch_the_pp
$ python3.6 setup.py build_ext --inplace
...
$ cd ..
$ python3.6 -m catch_the_pp.sample
Calculation:
Stars: 1.9046727418899536, PP: 42.187660217285156, MaxCombo: 1286
$ python3.6
>>> from catch_the_pp.osu_parser.beatmap import Beatmap
>>> from catch_the_pp.osu.ctb.difficulty import Difficulty
>>> from catch_the_pp.ppCalc import calculate_pp
>>> beatmap = Beatmap("catch_the_pp/test.osu")
>>> difficulty = Difficulty(beatmap=beatmap, mods=0)
>>> difficulty.star_rating
1.9046727418899536
>>> calculate_pp(diff=difficulty, accuracy=1, combo=beatmap.max_combo, miss=0)
42.187660217285156
```
> Note: You must clone the repo in a folder that has no dashes in its name, because Python modules cannot have dashes in their name! In this example, `catch_the_pp` was used.