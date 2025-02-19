use IO;
use Sort;
use Set;
use List;
use Random;

config const rankCount=1;
config const threadsPerRank=1;
config const sideLength=4;
config const messageCount=4;
config const timeToRun=1000;
config const outputPrefix="configuration";

var elementCount = sideLength * sideLength;
var elementsPerRank = elementCount / rankCount;
var elementsPerThread = elementsPerRank / threadsPerRank;

record ponger {
  var id: int, rank: int, thread: int, 
      north: int, south: int, east: int, west: int;

  proc toString() {
    var fullString = 
"{ \
    \"name\": \"pong_PONGERID\",\
    \"type\": \"pingpong.ponger\",\
    \"params\": {\
      \"ballsHeadingNorth\": \"NORTH\",\
      \"ballsHeadingSouth\": \"SOUTH\",\
      \"ballsHeadingWest\": \"WEST\",\
      \"ballsHeadingEast\": \"EAST\"\
    },\
    \"partition\": {\
      \"rank\": RANK,\
      \"thread\": THREAD\
    }\
}";
  
    var formatted = fullString.replace("PONGERID", id:string);
    var pairs = [("NORTH", north), ("SOUTH", south), ("WEST", west), 
                ("EAST", east), ("RANK", rank), ("THREAD", thread),
                ("PONGERID", id)];
    for (key, value) in pairs do
      formatted = formatted.replace(key, value:string);
    return formatted;
  }
}
proc pongerString(pongerId, rank, thread, north, south, east, west) {
  var p = new ponger(pongerId, rank, thread, north, south, east, west);
  return p.toString();
}

record link {
  var id: int, pong1: int, pong2: int, leftPort: string, rightPort: string;

  proc toString() {
      var fullString=
"{\
  \"name\": \"linkLINKID\",\
    \"left\": {\
      \"component\": \"pong_PONG1\",\
      \"port\": \"LEFTPORTPort\",\
      \"latency\": \"50s\"\
    },\
    \"right\": {\
      \"component\": \"pong_PONG2\",\
      \"port\": \"RIGHTPORTPort\",\
      \"latency\": \"50s\"\
    }\
}";
    var pairs = [("LINKID", id:string), ("PONG1", pong1:string),
                ("PONG2", pong2:string), ("LEFTPORT", leftPort:string),
                ("RIGHTPORT", rightPort:string)];
    var formatted = fullString;
    for (key, value) in pairs do
      formatted = formatted.replace(key, value);
    return formatted;
  }
}

writeln("Selecting message locations...");
var messageLocations: [0..<elementCount] bool;
messageLocations[0..<messageCount] = true;
shuffle(messageLocations);

writeln("Creating pongers...");
stdout.flush();
var pongers: [0..<elementCount] ponger;
forall elementNum in 0..<elementCount {
  var messageInputs: [0..<4] int = 0;
  if messageLocations[elementNum] {
    messageInputs[1] = 1;
    shuffle(messageInputs);
  }
  var rankNum = elementNum / elementsPerRank;
  var threadNum = (elementNum % rankCount) / elementsPerThread;
  pongers[elementNum] = new ponger(elementNum, rankNum, threadNum, 
    messageInputs[0], messageInputs[1], messageInputs[2], messageInputs[3]);
}


writeln("Creating links...");
stdout.flush();
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

proc writeRankJson(rankNum) {
  var elementStrings: set(string);
  var linkStrings: set(string);
  for p in pongers {
    if p.rank == rankNum {
      elementStrings.add(p.toString());
    }
  }
  for l in links {
    if pongers[l.pong1].rank == rankNum || 
       pongers[l.pong2].rank == rankNum {
      linkStrings.add(l.toString());
      elementStrings.add(pongers[l.pong1].toString());
      elementStrings.add(pongers[l.pong2].toString());
    }
  }
  //Add the sim object just to the first rank
  if rankNum == 0 {
    var simString = 
"""{
  "name": "sim",
  "type": "pingpong.simulator",
  "params": {
    "timeToRun": "TIMETORUN",
    "verbose": "False",
    "artificialWork": "0"
  },
  "partition": {
    "rank": 0,
    "thread": 0
  }
}""";
    simString = simString.replace("TIMETORUN", timeToRun:string);
    elementStrings.add(simString);
  }

  var programOptions = """
"program_options": {
  "verbose": "0",
  "stop-at": "0 ns",
  "print-timing-info": "true",
  "heartbeat-sim-period": "",
  "heartbeat-wall-period": "0",
  "timebase": "1 ps",
  "partitioner": "sst.linear",
  "timeVortex": "sst.timevortex.priority_queue",
  "interthread-links": "false",
  "output-prefix-core": "@x SST Core: ",
  "checkpoint-sim-period": "",
  "checkpoint-wall-period": "0"
}""";


  var compArray = elementStrings.toArray();
  sort(compArray);
  var componentString = "\"components\": [" + ",\n".join(compArray) + "]";

  var linkArray = linkStrings.toArray();
  sort(linkArray);
  var linkString = "\"links\": [" + ",\n".join(linkArray) + "]";


  var fullString = "{" + 
    ",\n".join(programOptions, componentString, linkString) + "\n}";

  var filename = outputPrefix+rankNum:string + ".json";

  var f = openWriter(filename);
  f.write(fullString);
  f.close();
}
writeln("Writing json output..");
stdout.flush();
forall i in 0..<rankCount {
  writeRankJson(i);
}