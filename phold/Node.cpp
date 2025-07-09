#include <sst/core/sst_config.h>
#include <sst/core/interfaces/stringEvent.h>
#include "Node.h"


Node::Node( SST::ComponentId_t id, SST::Params& params )
  : SST::Component(id)
{
  std::cout << "initializing Node\n" << std::flush;
  numRings = params.find<int>("numRings");
  
  myCol = params.find<int>("j", 1);
  myRow = params.find<int>("i", 1);
  timeToRun = params.find<std::string>("timeToRun");
  
  recvCount = 0;
  numLinks = (2*numRings+1) * (2*numRings+1);
  
  rng = std::mt19937(0);
  dist = std::uniform_int_distribution<int>(0, numLinks-1);

  links = std::vector<SST::Link*>(numLinks);
  for (int i = 0; i < numLinks; ++i) {
    std::string portName = "port" + std::to_string(i);
    std::cout << "port name: " << portName << "\n";
    links[i] = configureLink(portName, new SST::Event::Handler<Node>(this, &Node::handleEvent));
  }

  registerAsPrimaryComponent();
  primaryComponentDoNotEndSim();
  registerClock(timeToRun, new SST::Clock::Handler<Node>(this, &Node::tick));
}

Node::~Node() {
#ifdef ENABLE_SSTDBG
  delete dbg;
#endif
}

void Node::setup() {
  std::cout << "Node::setup on " << myRow << " " << myCol << "\n" << std::flush;
  for(int i = 0; i < links.size(); i++) {
    std::cout << "sending amessage on link " << i << "\n" << std::flush;
    if (links.at(i) != nullptr) {
      std::cout << "Link " << i << " is valid\n" << std::flush;
      auto ev = new SST::Event();
      std::cout << "created event\n" << std::flush;
      links.at(i)->send(ev);
    }
  }
  std::cout << "Node::setup done\n" << std::flush;
}

void Node::finish() { 
  std::cout << "Component at " << myRow << "," << myCol << " processed " << recvCount << " messages\n";
}

bool Node::tick( SST::Cycle_t currentCycle ) {
  std::cout << "Ticking at " << currentCycle << "\n";
  primaryComponentOKToEndSim();
  return false;
}

void Node::handleEvent(SST::Event *ev){
  std::cout << "Handling event from component\n";
  recvCount += 1;

  size_t nextRecipientLinkId = movementFunction();

  while (links.at(nextRecipientLinkId) == nullptr) {
    nextRecipientLinkId = movementFunction();
  }
  links[nextRecipientLinkId]->send(ev);
}
  
size_t Node::movementFunction() {
  return dist(rng);
}