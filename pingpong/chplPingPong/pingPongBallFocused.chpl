use List, Map, Random, IO.FormattedIO, BlockDist, Time;

config const N         = 10;
config const timeToRun = 200;
config const numDims   = 2;
config const edgeDelay = 50;
config const artificialWork = 0;
config const verbose   = false;

config const corners       = false;
config const random        = -1;
config const randomOverlap = -1;
config const wavefront     = false;

config const algorithm = 0;

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

enum Direction {
  NORTH, SOUTH, WEST, EAST
}

record Ball {
  var x, y : int;
  var direction : Direction;
}
var nBallsSet = 0;

// ----------------------------------------------------------------------------

var ballsD = blockDist.createDomain({0..<numBalls});
var balls : [ballsD] Ball;

proc addBall(x : int, y : int, d : Direction) {
  if verbose then
    writef("%3i %3i %s\n", x, y, d : string);
  balls[nBallsSet] = new Ball(x,y,d);
  nBallsSet += 1;
}

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

proc runSim() {
  select algorithm {
    when 0 do runNaiveSim();
    when 1 do runLessNaiveSim();
    when 2 do runQuestionableSim();
    otherwise do halt("Invalid algorithm choose between 0-2");
  }
}

proc runNaiveSim() {
  for i in 0..<timeToRun by edgeDelay {
    forall b in balls {
      conductArtificialWork(artificialWork);
      select b.direction {
        when Direction.NORTH do if b.y > 1 then b.y -= 1; else { b.y += 1; b.direction = Direction.SOUTH; }
        when Direction.SOUTH do if b.y < N then b.y += 1; else { b.y -= 1; b.direction = Direction.NORTH; }
        when Direction.WEST  do if b.x > 1 then b.x -= 1; else { b.x += 1; b.direction = Direction.EAST;  }
        when Direction.EAST  do if b.x < N then b.x += 1; else { b.x -= 1; b.direction = Direction.WEST;  }
      }
    }
  }
}

proc runLessNaiveSim() {
  forall b in balls {
    conductArtificialWork(artificialWork);
    for i in 0..<timeToRun by edgeDelay {
      select b.direction {
        when Direction.NORTH do if b.y > 1 then b.y -= 1; else { b.y += 1; b.direction = Direction.SOUTH; }
        when Direction.SOUTH do if b.y < N then b.y += 1; else { b.y -= 1; b.direction = Direction.NORTH; }
        when Direction.WEST  do if b.x > 1 then b.x -= 1; else { b.x += 1; b.direction = Direction.EAST;  }
        when Direction.EAST  do if b.x < N then b.x += 1; else { b.x -= 1; b.direction = Direction.WEST;  }
      }
    }
  }
}

proc runQuestionableSim() {
  coforall loc in Locales do on loc {
    ref local_balls = balls.localSlice(balls.localSubdomain());

    forall b in local_balls {
      for i in 0..<timeToRun by edgeDelay {
        conductArtificialWork(artificialWork);
        select b.direction {
          when Direction.NORTH do if b.y > 1 then b.y -= 1; else { b.y += 1; b.direction = Direction.SOUTH; }
          when Direction.SOUTH do if b.y < N then b.y += 1; else { b.y -= 1; b.direction = Direction.NORTH; }
          when Direction.WEST  do if b.x > 1 then b.x -= 1; else { b.x += 1; b.direction = Direction.EAST;  }
          when Direction.EAST  do if b.x < N then b.x += 1; else { b.x -= 1; b.direction = Direction.WEST;  }
        }
      }
    }
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
