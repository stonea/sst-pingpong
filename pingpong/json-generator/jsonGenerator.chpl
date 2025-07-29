use IO;
use Sort;
use Set;
use List;
use Random;
use Time;

config const rankCount=1;
config const threadsPerRank=1;
config const sideLength=4;
config const timeToRun=200;
config const outputPrefix="configuration";
config const edgeDelay=50;
config const verbose = false;
config const printTimingInfo = true;

config const corners = false;
config const random = -1;
config const randomOverlap = -1;
config const wavefront = false;

config const numDims=2;

proc verifyConfigOptions() {
  const numPatterns = (corners == true) + (random >= 0) + 
                      (randomOverlap >= 0) + (wavefront == true);
  if numPatterns == 0 {
    halt("Must specify one of --corners, --random, --randomOverlap, or --wavefront");
  }
}

verifyConfigOptions();

var s: stopwatch;

var elementCount = sideLength ** numDims;
var elementsPerRank = elementCount / rankCount;
var elementsPerThread = elementsPerRank / threadsPerRank;

record ponger {
  var id: int, rank: int, thread: int, 
      north: int, south: int, east: int, west: int;

  proc toString(includeParams=true) {
    var fullString = """
    { 
      "name": "pong_PONGERID",
      "type": "pingpong.ponger"
      PARAMS
      PARTITION_INFO
    }""";
    var params=""",
    "params": {
      "ballsHeadingNorth": "NORTH",
      "ballsHeadingSouth": "SOUTH",
      "ballsHeadingWest": "WEST",
      "ballsHeadingEast": "EAST"
    }""";
    var partitionInfo = """,
    "partition": {
      "rank": RANK,
      "thread": THREAD
    }""";
    
    if includeParams {
      fullString = fullString.replace("PARAMS", params);
    } else {
      fullString = fullString.replace("PARAMS", "");
    }
    if rankCount == 1 {
      fullString = fullString.replace("PARTITION_INFO", "");
    } else {
      fullString = fullString.replace("PARTITION_INFO", partitionInfo);
    }
    var pairs = [("NORTH", north), ("SOUTH", south), ("WEST", west), 
                ("EAST", east), ("RANK", rank), ("THREAD", thread),
                ("PONGERID", id)];
    for (key, value) in pairs do
      fullString = fullString.replace(key, value:string);
    return fullString;
  }
}

record link {
  var id: int, pong1: int, pong2: int, leftPort: string, rightPort: string;

  proc toString() {
    var fullString=
    """{
      "name": "linkLINKID",
      "left": {
        "component": "pong_PONG1",
        "port": "LEFTPORTPort",
        "latency": "EDGEDELAYs"
        
      },
      "right": {
        "component": "pong_PONG2",
        "port": "RIGHTPORTPort",
        "latency": "EDGEDELAYs"
      }
    }""";

    var pairs = [("LINKID", id:string), ("PONG1", pong1:string),
                ("PONG2", pong2:string), ("LEFTPORT", leftPort:string),
                ("RIGHTPORT", rightPort:string), 
                ("EDGEDELAY", edgeDelay:string)];
    var formatted = fullString;
    for (key, value) in pairs do
      formatted = formatted.replace(key, value);
    return formatted;
  }
}

proc createPongers() {
  var pongers: [0..<elementCount] ponger;
  forall elementNum in 0..<elementCount {
    var rankNum = elementNum / elementsPerRank;
    var threadNum = (elementNum % elementsPerRank) / elementsPerThread;
    pongers[elementNum] = new ponger(elementNum, rankNum, threadNum, 0,0,0,0);
  }
  if random != -1 {
    var stream = new randomStream(int);
    var idxs = sample(0..<elementCount, random);

    for idx in idxs {
      var direction = stream.next(1, 2**numDims);
      if direction == 1 then pongers[idx].north = 1;
      if direction == 2 then pongers[idx].south = 1;
      if direction == 3 then pongers[idx].east = 1;
      if direction == 4 then pongers[idx].west = 1;
    }
  }
  if randomOverlap != -1 {
    var stream = new randomStream(int);
    for i in 1..randomOverlap {
      var idx = stream.next(0,elementCount-1);
      var direction = stream.next(1, 2**numDims);
      if direction == 1 then pongers[idx].north = 1;
      if direction == 2 then pongers[idx].south = 1;
      if direction == 3 then pongers[idx].east = 1;
      if direction == 4 then pongers[idx].west = 1;
    }
  }
  if corners {
    var nw = 0;
    var ne = sideLength - 1;
    var sw = sideLength * (sideLength - 1);
    var se = elementCount - 1;

    
    pongers[nw].south = 1;
    pongers[se].north = 1;
    if numDims == 2 {
      pongers[se].west = 1;
      pongers[nw].east = 1;
      pongers[ne].west = 1;
      pongers[ne].south = 1;
      pongers[sw].north = 1;
      pongers[sw].east = 1;
    }
    
    
  }
  if wavefront {
    forall i in 0..<sideLength {
      pongers[i].south = 1;
      if numDims == 2 {
        pongers[i * sideLength].east = 1;
        pongers[(i+1) * sideLength - 1].west = 1;
        pongers[sideLength * (sideLength - 1) + i].north = 1;
      }
      
    }
  }
  return pongers;
}

s.restart();
var pongers: [0..<elementCount] ponger = createPongers();
s.stop();
writeln("Creating pongers: ", s.elapsed(), " seconds");

proc createLinks2D() {
  var grid: [0..<sideLength, 0..<sideLength] int;
  for (i,j) in grid.domain do grid[i,j] = i*sideLength + j;

  var linkNum = 0;
  var links: list(link);
  for (i,j) in grid.domain {
    if (i+1) % sideLength != 0 {
      var l = new link(linkNum, grid(i,j), grid(i+1,j), "south", "north");
      linkNum += 1;
      links.pushBack(l);
    } 
    if (j+1) % sideLength != 0 {
      var l = new link(linkNum, grid(i,j), grid(i,j+1), "east", "west");
      linkNum += 1;
      links.pushBack(l);
    }
  }
  return links;
}


proc createLinks1D() {
  var grid: [0..<sideLength] int;
  for i in grid.domain do grid[i] = i;

  var linkNum = 0;
  var links: list(link);
  for i in grid.domain {
    if (i+1) % sideLength != 0 {
      var l = new link(linkNum, grid[i], grid[i+1], "south", "north");
      linkNum += 1;
      links.pushBack(l);
    } 
  }
  return links;
}

s.restart();
var links: list(link);
if numDims == 1 {
  links = createLinks1D();
} else {
  links = createLinks2D();
} 
s.stop();
writeln("Creating links: ", s.elapsed(), " seconds");

proc writeRankJson(rankNum) {
  var s: stopwatch;
  var elementStrings: set(string);
  var linkStrings: set(string);

  s.restart();
  for p in pongers {
    if p.rank == rankNum {
      elementStrings.add(p.toString());
    }
  }
  s.stop();
  writeln("Adding pongers: ", s.elapsed(), " seconds");

  s.restart();
  for l in links {
    if pongers[l.pong1].rank == rankNum || 
       pongers[l.pong2].rank == rankNum {
      linkStrings.add(l.toString());
      if pongers[l.pong1].rank != rankNum {
        elementStrings.add(pongers[l.pong1].toString(includeParams=false));
      } 
      if pongers[l.pong2].rank != rankNum {
        elementStrings.add(pongers[l.pong2].toString(includeParams=false));
      }
    }
  }
  s.stop();
  writeln("Adding links: ", s.elapsed(), " seconds");
  //Add the sim object just to the first rank
  if rankNum == 0 {
    var simString = 
"""{
  "name": "sim",
  "type": "pingpong.simulator",
  "params": {
    "timeToRun": "TIMETORUN",
    "verbose": "VERBOSE",
    "artificialWork": "0"
  }""";
    if rankCount == 1 {
      simString = simString + "}";
    } else {
      simString = simString + """,
  "partition": {
    "rank": 0,
    "thread": 0
  }
  """ + "}";
    }

    simString = simString.replace("TIMETORUN", timeToRun:string);
    
    simString = simString.replace("VERBOSE", if verbose then "True" else "False");
    elementStrings.add(simString);
  }

  var programOptions = """
"program_options": {
  "verbose": "0",
  "stop-at": "0 ns",
  "print-timing-info": "PRINTTIMINGINFO",
  "heartbeat-sim-period": "",
  "heartbeat-wall-period": "0",
  "timebase": "1 ps",
  "partitioner": "PARTITIONER",
  "timeVortex": "sst.timevortex.priority_queue",
  "interthread-links": "false",
  "output-prefix-core": "@x SST Core: ",
  "checkpoint-sim-period": "",
  "checkpoint-wall-period": "0"
}""";
  var partitioner: string;
  if rankCount == 1 && threadsPerRank == 1 {
    partitioner = "sst.single";
  } else {
    partitioner = "sst.linear";
  }
  programOptions = programOptions.replace("PARTITIONER", partitioner);
  programOptions = programOptions.replace("PRINTTIMINGINFO", (printTimingInfo:int):string);


  var compArray = elementStrings.toArray();
  sort(compArray);
  var componentString = "\"components\": [" + ",\n".join(compArray) + "]";

  var linkArray = linkStrings.toArray();
  sort(linkArray);
  var linkString = "\"links\": [" + ",\n".join(linkArray) + "]";


  var fullString = "{" + 
    ",\n".join(programOptions, componentString, linkString) + "\n}";


  var filename: string;
  if rankCount == 1 {
    filename = outputPrefix + ".json";
  } else {
    filename = outputPrefix + rankNum:string + ".json";
  }
  var f = openWriter(filename);
  f.write(fullString);
  f.close();
}


s.restart();
forall i in 0..<rankCount {
  writeRankJson(i);
}
s.stop();
writeln("Writing JSON: ", s.elapsed(), " seconds");