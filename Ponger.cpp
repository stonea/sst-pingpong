#include <sst/core/sst_config.h>
#include <sst/core/interfaces/stringEvent.h>
#include "Ponger.h"
#include "GlobalParams.h"

using SST::Interfaces::StringEvent;

class BallEvent : public SST::Event {
  public:
    BallEvent() : SST::Event(), count(0) { }
    BallEvent(int64_t cnt) : SST::Event(), count(cnt) { }
    
    int64_t count;

    void serialize_order(SST::Core::Serialization::serializer &ser)  override {
      Event::serialize_order(ser);
      ser & count;
    }

    // Register this event as serializable
    ImplementSerializable(BallEvent);
};

static double artificialWorkValue = 1.1;
static double artificialWorkMultiplier = 1.23;
static void conductArtificialWork(int64_t count) {
  for(int64_t i = 0; i < count; i++) {
    artificialWorkValue *= artificialWorkMultiplier;
  }
}

Ponger::Ponger( SST::ComponentId_t id, SST::Params& params )
  : SST::Component(id)
{
  ballsHeadingNorth = params.find<int64_t>("ballsHeadingNorth", 0);
  ballsHeadingSouth = params.find<int64_t>("ballsHeadingSouth", 0);
  ballsHeadingWest  = params.find<int64_t>("ballsHeadingWest",  0);
  ballsHeadingEast  = params.find<int64_t>("ballsHeadingEast",  0);

  northPort = configureLink("northPort", new SST::Event::Handler<Ponger>(this, &Ponger::handleNorthPort));
  southPort = configureLink("southPort", new SST::Event::Handler<Ponger>(this, &Ponger::handleSouthPort));
  westPort  = configureLink("westPort",  new SST::Event::Handler<Ponger>(this, &Ponger::handleWestPort));
  eastPort  = configureLink("eastPort",  new SST::Event::Handler<Ponger>(this, &Ponger::handleEastPort));

  static bool setCallbacks = false;
  if(!setCallbacks) {
//    SST::sst_setNorthPortFunc(&Ponger::handleNorthPort);
//    SST::sst_setSouthPortFunc(&Ponger::handleSouthPort);
    setCallbacks = true;
  }

#ifdef ENABLE_SSTDBG
  dbg = new SSTDebug(getName(),"./");
#endif
}

Ponger::~Ponger() {
#ifdef ENABLE_SSTDBG
  delete dbg;
#endif
}

void Ponger::sendNorthPort(SST::Event *event) {
  SST::Link *link = getLinkByName("northPort");
  link->send(event);

  if(SST::sst_useVirtualLinks()) {
    delete link;
  }
}

void Ponger::sendSouthPort(SST::Event *event) {
  SST::Link *link = getLinkByName("southPort");
  link->send(event);

  if(SST::sst_useVirtualLinks()) {
    delete link;
  }
}


void Ponger::setup() {
  if(ballsHeadingNorth > 0) {
         if(isPortConnected("northPort")) { sendNorthPort(new BallEvent(ballsHeadingNorth)); }
    else if(isPortConnected("southPort")) { sendSouthPort(new BallEvent(ballsHeadingNorth)); }
  }

  if(ballsHeadingSouth > 0) {
         if(isPortConnected("southPort")) { sendSouthPort(new BallEvent(ballsHeadingSouth)); }
    else if(isPortConnected("northPort")) { sendNorthPort(new BallEvent(ballsHeadingSouth)); }
  }

  if(ballsHeadingWest > 0) {
         if(isPortConnected("westPort")) { westPort->send(new BallEvent(ballsHeadingWest)); }
    else if(isPortConnected("eastPort")) { eastPort->send(new BallEvent(ballsHeadingWest)); }
  }

  if(ballsHeadingEast > 0) {
         if(isPortConnected("eastPort")) { eastPort->send(new BallEvent(ballsHeadingEast)); }
    else if(isPortConnected("westPort")) { westPort->send(new BallEvent(ballsHeadingEast)); }
  }
}

void Ponger::finish() { }

bool Ponger::tick( SST::Cycle_t currentCycle ) {
  return false;
}

void Ponger::handleNorthPort(SST::Event *ev) {
  if(gVerbose) {
    std::cout << std::setw(10) << getElapsedSimTime().toStringBestSI() << " | "
              << "vvvvvv " << getName() << std::endl;
  }

  conductArtificialWork(gArtificialWork);

  int64_t incomingBalls = (dynamic_cast<BallEvent*>(ev))->count;
  if(isPortConnected("southPort")) {
    southPort->send(new BallEvent(incomingBalls));
  } else if(isPortConnected("northPort")) {
    northPort->send(new BallEvent(incomingBalls));
  }

  delete ev;
}

void Ponger::handleSouthPort(SST::Event *ev) {
  if(gVerbose) {
    std::cout << std::setw(10) << getElapsedSimTime().toStringBestSI() << " | "
              << "^^^^^^ " << getName() << std::endl;
  }

  conductArtificialWork(gArtificialWork);

  int64_t incomingBalls = (dynamic_cast<BallEvent*>(ev))->count;
  if(isPortConnected("northPort")) {
    northPort->send(new BallEvent(incomingBalls));
  } else if(isPortConnected("southPort")) {
    southPort->send(new BallEvent(incomingBalls));
  }

  delete ev;
}

void Ponger::handleWestPort(SST::Event *ev) {
  if(gVerbose) {
    std::cout << std::setw(10) << getElapsedSimTime().toStringBestSI() << " | "
              << " -----> " << getName() << std::endl;
  }

  conductArtificialWork(gArtificialWork);

  int64_t incomingBalls = (dynamic_cast<BallEvent*>(ev))->count;
  if(isPortConnected("eastPort")) {
    eastPort->send(new BallEvent(incomingBalls));
  } else if(isPortConnected("westPort")) {
    westPort->send(new BallEvent(incomingBalls));
  }

  delete ev;
}

void Ponger::handleEastPort(SST::Event *ev) {
  if(gVerbose) {
    std::cout << std::setw(10) << getElapsedSimTime().toStringBestSI() << " | "
              << getName() << " <-----" << std::endl;
  }

  conductArtificialWork(gArtificialWork);

  int64_t incomingBalls = (dynamic_cast<BallEvent*>(ev))->count;
  if(isPortConnected("westPort")) {
    westPort->send(new BallEvent(incomingBalls));
  } else if(isPortConnected("eastPort")) {
    eastPort->send(new BallEvent(incomingBalls));
  }

  delete ev;
}

#ifdef ENABLE_SSTDBG
void Ponger::printStatus(SST::Output& out){
  if(!dbg->dump(getCurrentSimCycle(),
     DARG(ballsHeadingNorth),
     DARG(ballsHeadingSouth),
     DARG(ballsHeadingWest),
     DARG(ballsHeadingEast)))
  {
    out.output("Debug dump failed!\n");
  }
}
#endif
