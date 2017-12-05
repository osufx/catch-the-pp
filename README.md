# Cythonized catch-the-pp
An osu ctb gamemode star/pp calculator made in Cython.  
Original repo: [catch-the-pp](https://github.com/osufx/catch-the-pp) by [Sunpy](https://github.com/EmilySunpy).  

## Changes
- Cythonized all files, functions, classes and methods (with static typing as well)
- Replaced `math.pow` with `**`, this gives _a bit_ of extra speed
- Minor code cleaning

## Performance
These are the execution times after running pp calculation (with beatmap parsing and difficulty calculation as well) on `reanimate.osu` 100 times  
Pure Python version: `Min: 0.7986021041870117 s, Max: 0.932903528213501 s, Avg: 0.8350819730758667 s`  
Cythonized version: `Min: 0.22933077812194824 s, Max: 0.25774192810058594 s, Avg: 0.23836223363876344 s`
