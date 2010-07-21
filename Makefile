# This build a library which is named libMGDO{name_dir}.so


include $(MGDODIR)/buildTools/config.mk

INCLUDEFLAGS += -I. -I$(MGDODIR)/Base -I$(MGDODIR)/Root
LIBFLAGS += -L$(MGDODIR)/lib -lMGDORoot -lMGDOBase -lMGDOTransforms

include $(MGDODIR)/buildTools/BasicROOTMakefile

ifneq ($(SOSUFFIX),so)
shared::
	@if [ ! -f $(basename $(SHLIB)).so ]; then ln -s $(SHLIB) $(basename $(SHLIB)).so; fi
endif

clean::
	@rm -f $(basename $(SHLIB)).*
