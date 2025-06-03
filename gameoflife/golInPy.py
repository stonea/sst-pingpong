#!/usr/bin/env python3

# Conway's game-of-life
# Rules from: https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life

N = 10

def isCellAlive(board, row, col):
  if row >= 0 and row < N and col >= 0 and col < N:
    return board[row][col] == '#'
  return False

def neighbors(board, row, col):
  neighs = [(-1,-1), (-1, 0), (-1, 1),
            ( 0,-1),          ( 0, 1),
            ( 1,-1), ( 1, 0), ( 1, 1)]
  res = 0
  for neigh in neighs:
    if isCellAlive(board, row + neigh[0], col + neigh[1]):
      res += 1

  return res

board = \
  [ "..........",
    ".#........",
    ".##.......",
    ".#.#......",
    "#..##...#.",
    ".#.##.#...",
    "..###.....",
    "..####....",
    "..##......",
    ".........."]

for times in range(0,2):
  nextBoard = []
  for row in range(0,len(board)):
    nextLine = ""
    for col in range(0,len(board[row])):
      numNeighbors = neighbors(board, row, col) 
      if isCellAlive(board, row, col):
        # Any live cell with fewer than two live neighbours dies, as if by underpopulation.
        if numNeighbors < 2:
          nextLine += '.'
        # Any live cell with two or three live neighbours lives on to the next generation.
        elif numNeighbors == 2 or numNeighbors == 3:
          nextLine += '#'
        # Any live cell with more than three live neighbours dies, as if by overpopulation.
        else:
          nextLine += '.'
      else:
        # Any dead cell with exactly three live neighbours becomes a live cell, as if by reproduction.
        if numNeighbors == 3:
          nextLine += '#'
        else:
          nextLine += '.'
    nextBoard.append(nextLine)

  for line in nextBoard:
    print(line)
  print()

  board = nextBoard

