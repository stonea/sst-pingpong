#include <sst/core/sst_config.h>
#include <sst/core/interfaces/stringEvent.h>
#include "cell.h"

class GolEvent : public SST::Event {
    bool _isAlive;

  public:
    GolEvent() : SST::Event(), _isAlive(false) { }
    GolEvent(bool isAlive) : SST::Event(), _isAlive(isAlive) { }

    bool isAlive() const { return _isAlive; }

    void serialize_order(SST::Core::Serialization::serializer &ser) override {
      Event::serialize_order(ser);
    }
    ImplementSerializable(GolEvent);
};

static bool postIfDead = true;
static bool shouldReport = false;
#ifdef ENABLE_SSTCHECKPOINT
  Cell::Cell() : SST::Component() { }
#endif

Cell::Cell( SST::ComponentId_t id, SST::Params& params )
  : SST::Component(id)
{
  isAlive = params.find<bool>("isAlive", false);
  postIfDead = params.find<bool>("postIfDead", true);
  shouldReport = params.find<bool>("shouldReport", false);
  aliveNeighbors = 0;

  registerClock("2s",   new SST::Clock::Handler2<Cell, &Cell::clockTick>(this));

  nwPort = configureLink("nwPort", new SST::Event::Handler2<Cell, &Cell::handleEvent>(this));
  nPort  = configureLink("nPort",  new SST::Event::Handler2<Cell, &Cell::handleEvent>(this));
  nePort = configureLink("nePort", new SST::Event::Handler2<Cell, &Cell::handleEvent>(this));
  wPort  = configureLink("wPort",  new SST::Event::Handler2<Cell, &Cell::handleEvent>(this));
  ePort  = configureLink("ePort",  new SST::Event::Handler2<Cell, &Cell::handleEvent>(this));
  swPort = configureLink("swPort", new SST::Event::Handler2<Cell, &Cell::handleEvent>(this));
  sPort  = configureLink("sPort",  new SST::Event::Handler2<Cell, &Cell::handleEvent>(this));
  sePort = configureLink("sePort", new SST::Event::Handler2<Cell, &Cell::handleEvent>(this));

  if(id == 0) {
    registerAsPrimaryComponent();
    primaryComponentDoNotEndSim();
  }
}

Cell::~Cell() { }

void Cell::setup() {
  communicate();
}

void Cell::handleEvent(SST::Event *ev) {
  if(dynamic_cast<GolEvent*>(ev)->isAlive()) {
    aliveNeighbors += 1;
  }
  delete ev;
}

void Cell::update() {
  if(isAlive && (aliveNeighbors < 2 || aliveNeighbors > 3)) {
    isAlive = false;
  } else if(!isAlive && aliveNeighbors == 3) {
    isAlive = true;
  }
  aliveNeighbors = 0;
}

void Cell::communicate() {
  if(postIfDead || isAlive) {
    if(isPortConnected("nwPort")) { nwPort->send(new GolEvent(isAlive)); }
    if(isPortConnected("nPort"))  { nPort->send(new GolEvent(isAlive));  }
    if(isPortConnected("nePort")) { nePort->send(new GolEvent(isAlive)); }
    if(isPortConnected("wPort"))  { wPort->send(new GolEvent(isAlive));  }
    if(isPortConnected("ePort"))  { ePort->send(new GolEvent(isAlive));  }
    if(isPortConnected("swPort")) { swPort->send(new GolEvent(isAlive)); }
    if(isPortConnected("sPort"))  { sPort->send(new GolEvent(isAlive));  }
    if(isPortConnected("sePort")) { sePort->send(new GolEvent(isAlive)); }
  }
}

void Cell::report() {
  if(!shouldReport) {
    return;
  }

  std::cout << (isAlive ? "#" : ".");
  if(getName().back() == '9') {
    std::cout << std::endl;
  }
  if(getName() == "cell_9_9" || getName() == "board0.cell_9_9") {
    std::cout << std::endl;
  }
}

bool Cell::clockTick(SST::Cycle_t currentCycle) {
  update();
  report();
  communicate();
  return false;
}

#ifdef ENABLE_SSTCHECKPOINT
  void Cell::serialize_order(SST::Core::Serialization::serializer& ser) {
    SST_SER(postIfDead);
    SST_SER(shouldReport);
    SST_SER(aliveNeighbors);
    SST_SER(nwPort);
    SST_SER(nPort);
    SST_SER(nePort);
    SST_SER(wPort);
    SST_SER(ePort);
    SST_SER(swPort);
    SST_SER(sPort);
    SST_SER(sePort);
  }
#endif // ENABLE_SSTCHECKPOINT
