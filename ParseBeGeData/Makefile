# Makefile for linking against ROOT 
# M. Marino 22 May 2007 

TARGETS = parseBeGe #parseBeGeOld 

TARGETOBJ = $(patsubst %, %.o, $(TARGETS))
CXX = g++
CPPFLAGS = -I$(PWD) -I$(CLHEP_INCLUDE_DIR) -I$(MGDODIR)/Root -I$(MGDODIR)/Base -I$(MGDODIR)/Transforms #-DTEST
CXXFLAGS = -Wall -O2 
LIBS =  -lm -L$(CLHEP_LIB_DIR) -l$(CLHEP_LIB) -L$(MGDODIR)/lib -lMGDOBase -lMGDORoot -lMGDOTransforms

CXXFLAGS += $(shell $(ROOTSYS)/bin/root-config --cflags)
LIBS += $(shell $(ROOTSYS)/bin/root-config --libs) 

.PHONY: all

all: $(TARGETS)

%.o: %.cc
	$(CXX) -c $(CPPFLAGS) $(CXXFLAGS) $< 

$(TARGETS): $(TARGETOBJ) $(OBJS)
	$(CXX) $(CXXFLAGS) -o $@ $@.o $(OBJS) $(LIBS)

clean:
	rm -f $(TARGETS)
	rm -f *.o
