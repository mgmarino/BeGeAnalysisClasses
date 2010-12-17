# This build a library which is named libMGDO{name_dir}.so


include buildTools/config.mk

packageName := $(notdir $(shell pwd))
SHLIB := lib$(packageName).$(SOSUFFIX)
ROOTDICTCCNAME := BeGe$(packageName)DICT.C
ROOTDICTHHNAME := BeGe$(packageName)DICT.h
ROOTDICTOBJECT := $(ROOTDICTCCNAME:.C=.o)
INCLUDEFLAGS += $(ROOT_INCLUDE_FLAGS)
LIBFLAGS += $(ROOT_LIB_FLAGS) 

SOURCES ?= $(wildcard *.cc)
OBJECTS ?= $(SOURCES:.cc=.o)
ROOTDICTHEADERS ?= $(shell grep -l ClassDef $(wildcard *.hh) | xargs) 

.PHONY: all depend lib clean shared

all: lib finish

lib: shared

shared:: $(SHLIB)

.depend depend: $(ROOTDICTCCNAME)
	@echo Checking dependencies...
	$(CXX) -M $(CXXFLAGS) $(INCLUDEFLAGS) $(SOURCES) $(ROOTDICTCCNAME) > .depend

%.o: %.cc 
	$(CXX) -c $(CXXFLAGS) $(INCLUDEFLAGS) $< 

%.o: %.C
	$(CXX) -c $(CXXFLAGS) $(INCLUDEFLAGS) $< 

$(ROOTDICTCCNAME): $(ROOTDICTHEADERS) LinkDef.h
	@echo Rootifying files...
	@rm -f $(ROOTDICTCCNAME) $(ROOTDICTHHNAME) 
	$(ROOTCINT) $(ROOTDICTCCNAME) -c -p $(CXXFLAGS) $(ROOTDICTINCLUDE) $(INCLUDEFLAGS) $(ROOTDICTHEADERS) LinkDef.h
 
$(SHLIB): $(OBJECTS) $(ROOTDICTOBJECT)
	$(SOMAKER) $(SOFLAGS) -o $(SHLIB) $(OBJECTS) $(ROOTDICTOBJECT) $(LIBFLAGS)

clean::
	@rm -f $(SHLIB) $(ROOTDICTCCNAME) $(ROOTDICTHHNAME) *.o *~ .depend

ifneq ($(MAKECMDGOALS),clean)
-include .depend
endif

ifneq ($(SOSUFFIX),so)
shared::
	@if [ ! -f $(basename $(SHLIB)).so ]; then ln -s $(SHLIB) $(basename $(SHLIB)).so; fi
endif

clean::
	@rm -f $(basename $(SHLIB)).*

finish:
	@echo 
	@echo "BeGe classes built, be sure to add the following line to your ~/.rootlogon.C file:"
	@echo 
	@echo "  gApplication->ExecuteFile(\"$(shell pwd)/LoadMGMClasses.C\");"
	@echo 
