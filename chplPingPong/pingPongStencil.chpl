use List, Map, Random, IO.FormattedIO, StencilDist, Time;

config const N         = 10;
config const timeToRun = 200;
config const numDims   = 1;
config const edgeDelay = 50;
config const artificialWork = 0;
config const verbose   = false;

config const corners       = false;
config const random        = -1;
config const randomOverlap = -1;
config const wavefront     = false;

// ----------------------------------------------------------------------------

proc verifyConfigOptions() {
  const numPatterns =
    (corners == true) + (random >= 0) + (randomOverlap >= 0) + (wavefront == true);
  if(numPatterns == 0) {
    halt("Must specify one of --corners, --random, --randomOverlap, or --wavefront");
  }
}
verifyConfigOptions();

var numBalls = 0;
     if corners    then numBalls = 4;
else if random >=0 then numBalls = random;
else if randomOverlap >=0 then numBalls = randomOverlap;
else if wavefront then numBalls = N * 4;

// ----------------------------------------------------------------------------

extern {
  #include <stdint.h>

  static double conductArtificialWork(int64_t count) {
    static const double artificialWorkMultiplier = 1.23;
    volatile double artificialWorkValue = 1.1;
    for(int64_t i = 0; i < count; i++) {
      artificialWorkValue *= artificialWorkMultiplier;
    }
    return artificialWorkValue;
  }
}


record BallStatus {
  var ballsN, ballsS, ballsW, ballsE : int;
}

var stencilD = stencilDist.createDomain({0..<N, 0..<N}, fluff=(1,1));

var board1, board2 : [stencilD] BallStatus;

enum Direction { NORTH=0, SOUTH, WEST, EAST };

proc printBoards(board1, board2, highlightBoard) {
  proc dirStr(val, dir) {
         if val == 0 then return "_";
    else if val == 1 then return dir;
    else return val : string;
  }

  for y in 0..<N {
    write(if highlightBoard==0 then "[" else " ");

    for x in 0..<N {
      if x > 0 then write(" ");
      writef("(%s %s %s %s)",
        dirStr(board1[x,y].ballsN, "N"),
        dirStr(board1[x,y].ballsS, "S"),
        dirStr(board1[x,y].ballsW, "W"),
        dirStr(board1[x,y].ballsE, "E"));
    }

    write(if highlightBoard==0 then "]" else " ");
    writef("  ");
    write(if highlightBoard==1 then "[" else " ");
    for x in 0..<N {
      if x > 0 then write(" ");
      writef("(%s %s %s %s)",
        dirStr(board2[x,y].ballsN, "N"),
        dirStr(board2[x,y].ballsS, "S"),
        dirStr(board2[x,y].ballsW, "W"),
        dirStr(board2[x,y].ballsE, "E"));
    }
    write(if highlightBoard==1 then "]" else " ");

    writeln();
  }
}

proc addBall(x : int, y : int, d : Direction) {
  select d {
    when Direction.NORTH do board1[x,y].ballsN += 1;
    when Direction.SOUTH do board1[x,y].ballsS += 1;
    when Direction.WEST  do board1[x,y].ballsW += 1;
    when Direction.EAST  do board1[x,y].ballsE += 1;
  }
}

proc applyBorderBounceback(ref board) {
  forall i in 0..<N {
    board[i,0].ballsS += board[i,0].ballsN;
    board[i,0].ballsN = 0;

    board[i,N-1].ballsN += board[i,N-1].ballsS;
    board[i,N-1].ballsS = 0;

    board[0,i].ballsE += board[0,i].ballsW;
    board[0,i].ballsW = 0;

    board[N-1,i].ballsW += board[N-1,i].ballsE;
    board[N-1,i].ballsE = 0;
  }
}

proc runSim() {
  proc doIter(const ref board, ref nextBoard) {
    forall (x,y) in stencilD {
      if y == N-1 then nextBoard[x,y].ballsN = 0;
      else             nextBoard[x,y].ballsN = board[x,y+1].ballsN;

      if y == 0   then nextBoard[x,y].ballsS = 0;
      else             nextBoard[x,y].ballsS = board[x,y-1].ballsS;

      if x == 0   then nextBoard[x,y].ballsE = 0;
      else             nextBoard[x,y].ballsE = board[x-1,y].ballsE; 

      if x == N-1 then nextBoard[x,y].ballsW = 0;
      else             nextBoard[x,y].ballsW = board[x+1,y].ballsW; 

      // apply bounceback
      if y == 0 { // north border
        nextBoard[x,y].ballsS += nextBoard[x,y].ballsN;
        nextBoard[x,y].ballsN = 0;
      }
      if y == N-1 { // south border
        nextBoard[x,y].ballsN += nextBoard[x,y].ballsS;
        nextBoard[x,y].ballsS = 0;
      }
      if x == 0 { // west border
        nextBoard[x,y].ballsE += nextBoard[x,y].ballsW;
        nextBoard[x,y].ballsW = 0;
      }
      if x == N-1 { // east border
        nextBoard[x,y].ballsW += nextBoard[x,y].ballsE;
        nextBoard[x,y].ballsE = 0;
      }

      for 0..<(board[x,y].ballsN + board[x,y].ballsS + board[x,y].ballsW + board[x,y].ballsE) do
        conductArtificialWork(artificialWork);
    }
    nextBoard.updateFluff();
  }

  if verbose {
    writeln("Before simulation:");
    printBoards(board1, board2, 0);
  }

  var steps = 0;
  board1.updateFluff();
  for ts in 0..<timeToRun by edgeDelay {
    if(steps % 2 == 0) then doIter(board1, board2);
    else doIter(board2, board1);

    if verbose {
      writeln();
      writeln("After time=", ts, ":");
      printBoards(board1, board2, (steps+1) % 2);
    }

    steps += 1;
  }
}

// ----------------------------------------------------------------------------

// Assign balls
if corners {
  addBall(0,0,Direction.EAST);
  addBall(N-1,0,Direction.WEST);
  if numDims > 1 {
    addBall(0,N-1,Direction.EAST);
    addBall(N-1,N-1,Direction.WEST);
    addBall(0,0,Direction.SOUTH);
    addBall(N-1,0,Direction.SOUTH);
    addBall(0,N-1,Direction.NORTH);
    addBall(N-1,N-1,Direction.NORTH);
  }
} else if random >= 0 {
  var rs = new randomStream(int);
  for r in sample(0..<(N * N), numBalls) {
    const x = r % N;
    const y = r / N;
    const direction = rs.next(0, 3);
         if direction == 0 then addBall(x,y,Direction.NORTH);
    else if direction == 1 then addBall(x,y,Direction.SOUTH);
    else if direction == 2 then addBall(x,y,Direction.WEST);
    else if direction == 3 then addBall(x,y,Direction.EAST);
  }
  applyBorderBounceback(board1);
} else if randomOverlap >= 0 {
  var rs = new randomStream(int);
  for 0..<numBalls {
    const r = rs.next(0, N*N -1);
    const x = r % N;
    const y = r / N;
    const direction = rs.next(0, 3);
         if direction == 0 then addBall(x,y,Direction.NORTH);
    else if direction == 1 then addBall(x,y,Direction.SOUTH);
    else if direction == 2 then addBall(x,y,Direction.WEST);
    else if direction == 3 then addBall(x,y,Direction.EAST);
  }
  applyBorderBounceback(board1);
} else if wavefront >= 0 {
  for i in 0..<N {
    addBall(i,0,Direction.SOUTH);
    addBall(0,i,Direction.EAST);
    addBall(N-1,i,Direction.WEST);
    addBall(i,N-1,Direction.NORTH);
  }
} else {
  halt("Unrecognized ball placement configuration");
}

var timer : stopwatch;
timer.start();
runSim();
timer.stop();
writeln("Time to run: ", timer.elapsed());
