# Pac-Man BFS

A Pac-Man style game built with Python and Pygame in which the ghost hunts the player using **Breadth-First Search (BFS)**. The maze is randomized on every run, so no two games are the same.

## Features

- Ghost chases Pac-Man along the shortest path, recalculated every move
- Randomized inner walls and cherry positions, validated so every maze is solvable
- Smooth tile-to-tile movement and animated Pac-Man mouth
- Sound effects and looping background music
- Score display, win / game over screens and instant restart
- Optional BFS path visualization (`pacman_bfs.py`)

## Getting Started

Requires Python 3.8+.

```bash
git clone https://github.com/SimranHundal17/pacman-bfs-game.git
cd pacman-bfs-game
pip install -r requirements.txt
python pacman.py
```

## Two Versions

| File | Purpose |
| --- | --- |
| `pacman.py` | The standard game. |
| `pacman_bfs.py` | Same game, but the ghost's current BFS path is drawn on the maze as cyan dots, so you can watch how the shortest route is calculated. Useful for learning and demos. |

```bash
python pacman_bfs.py
```

## Controls

| Key | Action |
| --- | --- |
| Arrow keys | Move Pac-Man |
| R | Restart with a new maze |
| Close window | Quit |

## How It Works

- **Maze:** a 2D grid (`█` wall, `.` floor, `o` cherry). Pac-Man and the ghost are `(row, col)` positions.
- **Pathfinding:** BFS explores the grid layer by layer, which guarantees the shortest path on a uniform-cost grid. The ghost runs it each time it is ready to move, then follows the first step of the path.
- **Maze validation:** after random walls are placed, a BFS flood-fill checks that every walkable tile is reachable; otherwise the maze is regenerated.

## Project Structure

```
pacman.py        # main game
pacman_bfs.py    # variant that visualizes the ghost's BFS path
assets/          # images and audio
requirements.txt
```

## Tech

Python 3, Pygame, `collections.deque`, `random`
