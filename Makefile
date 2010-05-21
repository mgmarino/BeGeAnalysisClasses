# This build a library which is named libMGDO{name_dir}.so

include $(MGDODIR)/buildTools/config.mk

INCLUDEFLAGS += -I. -I$(MGDODIR)/Base -I$(MGDODIR)/Root
LIBFLAGS += -L$(MGDODIR)/lib -lMGDORoot -lMGDOBase -lMGDOTransforms

include $(MGDODIR)/buildTools/BasicROOTMakefile

