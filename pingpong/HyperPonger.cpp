#include <sst/core/sst_config.h>
#include <sst/core/rng/marsaglia.h>
#include "HyperPonger.h"
#include "GlobalParams.h"

class BallEvent : public SST::Event {
  public:
    BallEvent() : SST::Event(), count(0) { }
    BallEvent(int64_t cnt) : SST::Event(), count(cnt) { }

    int64_t count;

    void serialize_order(SST::Core::Serialization::serializer &ser)  override {
      Event::serialize_order(ser);
      SST_SER(count);
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

HyperPonger::HyperPonger( SST::ComponentId_t id, SST::Params& params )
  : SST::Component(id)
{
  rng = new SST::RNG::MarsagliaRNG();
  initialBalls = params.find<int64_t>("numBalls", 0);

  linkN = configureLink("port_n", new SST::Event::Handler2<HyperPonger, &HyperPonger::handleEvent>(this));
  linkS = configureLink("port_s", new SST::Event::Handler2<HyperPonger, &HyperPonger::handleEvent>(this));
  linkW = configureLink("port_w", new SST::Event::Handler2<HyperPonger, &HyperPonger::handleEvent>(this));
  linkE = configureLink("port_e", new SST::Event::Handler2<HyperPonger, &HyperPonger::handleEvent>(this));

  for(int i = 0; i < NUM_LINKS; i++) {
    hyperLink[i] = configureLink("port_" + std::to_string(i),
      new SST::Event::Handler2<HyperPonger, &HyperPonger::handleEvent>(this));
  }
}

#ifdef ENABLE_SSTCHECKPOINT
  HyperPonger::HyperPonger() { }
#endif

HyperPonger::~HyperPonger() { }

void HyperPonger::setup() {
  for(int i = 0; i < initialBalls; i++) {
    sendOutRandomBall();
  }
}

void HyperPonger::finish() { }

bool HyperPonger::tick( SST::Cycle_t currentCycle ) {
  return false;
}

void HyperPonger::handleEvent(SST::Event *ev) {
  conductArtificialWork(gArtificialWork);
  sendOutRandomBall();
  delete ev;
}

void HyperPonger::sendOutRandomBall() {
  int rndNumber;
  rndNumber = (int)(rng->generateNextInt32());
  rndNumber = (rndNumber & 0x0000FFFF) ^ ((rndNumber & 0xFFFF0000) >> 16);
  rndNumber = abs((int)(rndNumber % 204));

  if(rndNumber == 0) {
    if(isPortConnected("port_n")) { linkN->send(new BallEvent(1)); }
    else { rndNumber += 1; }
  }

  if(rndNumber == 1) {
    if(isPortConnected("port_s")) { linkS->send(new BallEvent(1)); }
    else { rndNumber += 1; }
  }

  if(rndNumber == 2) {
    if(isPortConnected("port_w")) { linkW->send(new BallEvent(1)); }
    else { rndNumber += 1; }
  }

  if(rndNumber == 3) {
    if(isPortConnected("port_e")) { linkE->send(new BallEvent(1)); }
    else { rndNumber += 1; }
  }

  if(rndNumber > 3)  {
    int hyperPort = rndNumber - 4;
    if(isPortConnected("port_" + std::to_string(hyperPort))) {
      hyperLink[hyperPort]->send(new BallEvent(1));
    } else {
      // we don't have self links back in this topology.
      hyperLink[hyperPort+1]->send(new BallEvent(1));
    }
  }
}

#ifdef ENABLE_SSTCHECKPOINT
void HyperPonger::serialize_order(SST::Core::Serialization::serializer& ser) {
  SST::Component::serialize_order(ser);
  SST_SER(initialBalls);
  SST_SER(rng);
  SST_SER(out);
  SST_SER(linkN);
  SST_SER(linkS);
  SST_SER(linkW);
  SST_SER(linkE);
  for (size_t i = 0; i < NUM_LINKS; i++) {
    SST_SER(hyperLink[i]);
  }
}
#endif
