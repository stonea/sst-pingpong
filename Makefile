CXX=$(shell sst-config --CXX)
CXXFLAGS=$(shell sst-config --ELEMENT_CXXFLAGS) -g
LDFLAGS=$(shell sst-config --ELEMENT_LDFLAGS)

SRCS=Simulator.cpp Ponger.cpp

all: libpingpong.so install

libpingpong.so: $(SRCS)
	$(CXX) $(CXXFLAGS) $(LDFLAGS) -o $@ $^

install:
	sst-register pingpong pingpong_LIBDIR=$(CURDIR)

clean:
	rm -rf tests/graphs libpingpong.so
	sst-register -u pingpong
