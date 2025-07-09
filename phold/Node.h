#ifndef _pholdNode_H
#define _pholdNode_H

#include <sst/core/component.h>
#include <sst/core/link.h>
#include <sst/core/sst_types.h>
#include <random>
#ifdef ENABLE_SSTDBG
#include <sst/dbg/SSTDebug.h>
#endif




class Node : public SST::Component {
  public:
    Node( SST::ComponentId_t id, SST::Params& params );
    ~Node();

    void setup() override;
    void finish() override;

    bool tick( SST::Cycle_t currentCycle );

    void handleEvent(SST::Event *ev);

    size_t movementFunction();
    
    virtual SST::SimTime_t timestepIncrementFunction();


    template<typename T>
    void setupLinks() {
      for (int i = 0; i < links.size(); i++) {
        std::string portName = "port" + std::to_string(i);
        links[i] = configureLink(portName, new SST::Event::Handler<T>(dynamic_cast<T*>(this), &T::handleEvent));
      }
    }

    // Register the component
    SST_ELI_REGISTER_COMPONENT(
      Node,   // class
      "phold",   // element library
      "Node", // component
      SST_ELI_ELEMENT_VERSION( 1, 0, 0 ),
      "component that takes balls from its neighbors and passes along. If there's no neighbor to pass to, bounce back",
      COMPONENT_CATEGORY_UNCATEGORIZED
    )

    // Parameter name, description, default value
    SST_ELI_DOCUMENT_PARAMS(
     { "numRings", "number of rings to connect to", "1" },
     { "i", "My row index", "-1" },
     { "j", "My column index", "-1" },
     { "rowCount", "Total number of rows", "-1"},
     { "colCount", "Total number of columns", "-1"},
     { "timeToRun", "Time to run the simulation", "10ns" },
     { "eventDensity", "Number of events to start with per component", "0.1" }
    )

    SST_ELI_DOCUMENT_PORTS(
      {"port%d", "Ports to others", {}}
    )
    


#ifdef ENABLE_SSTDBG
    void printStatus(SST::Output& out) override;
#endif
    std::vector<SST::Link*> links;
    int myId;
    int numRings;
    int numLinks;
    int myRow,myCol;
    int rowCount, colCount;
    std::string timeToRun;
    int recvCount;
    std::mt19937 rng;
    std::uniform_int_distribution<int> uid;
    std::uniform_real_distribution<double> urd;

    double eventDensity;

#ifdef ENABLE_SSTDBG
    SSTDebug *dbg;
#endif
};


class ExponentialNode : public Node {

  public:
    ExponentialNode(SST::ComponentId_t id, SST::Params& params);
    SST::SimTime_t timestepIncrementFunction() override;
  SST_ELI_REGISTER_COMPONENT(
      ExponentialNode,   // class
      "phold",   // element library
      "ExponentialNode", // component
      SST_ELI_ELEMENT_VERSION( 1, 0, 0 ),
      "component that takes balls from its neighbors and passes along. If there's no neighbor to pass to, bounce back",
      COMPONENT_CATEGORY_UNCATEGORIZED
    )

    // Parameter name, description, default value
    SST_ELI_DOCUMENT_PARAMS(
     { "multiplier", "Multiplier for exponential distribution, in ns", "1ns"}
    )

    SST_ELI_DOCUMENT_PORTS(
      {"port%d", "Ports to others", {}}
    )

    double multiplier;
};

#endif
