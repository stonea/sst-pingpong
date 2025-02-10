#include <sst/core/sst_config.h>
#include <sst/core/interfaces/stringEvent.h>
#include "Simulator.h"
#include <string>

Simulator::Simulator(SST::ComponentId_t id, SST::Params& params)
  : SST::Component(id)
{
  timeToRun = params.find<int64_t>("timeToRun", 100);

  registerClock(std::to_string(timeToRun) + "ps", new SST::Clock::Handler<Simulator>(this, &Simulator::clockTick));

  registerAsPrimaryComponent();
  primaryComponentDoNotEndSim();
}

Simulator::~Simulator() { }

void Simulator::setup()  { }
void Simulator::finish() { }

bool Simulator::clockTick(SST::Cycle_t currentCycle) {
  primaryComponentOKToEndSim();
  return true;
}
