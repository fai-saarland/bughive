-include Makefile.config

ROOTDIR := $(dir $(realpath $(word $(words $(MAKEFILE_LIST)),$(MAKEFILE_LIST))))

DEBUG ?= no
WERROR ?= no

CC ?= gcc
CXX ?= g++

CFLAGS :=
CFLAGS += -Wall -pedantic
ifeq '$(DEBUG)' 'yes'
  CFLAGS += -g -pipe
else
  CFLAGS += -O3 -pipe
endif
ifeq '$(WERROR)' 'yes'
  CFLAGS += -Werror
endif
CFLAGS += -I.
CFLAGS += -Ipheromone/include

PHEROMONE_LDFLAGS ?= -Lpheromone -lpheromone $(shell pkg-config --libs grpc++ protobuf)

DYNET_ROOT ?= /opt/dynet
DYNET_LDFLAGS ?= -L$(DYNET_ROOT)/lib -Wl,-rpath=$(DYNET_ROOT)/lib -ldynet

ASNETS_CFLAGS := $(CFLAGS)
ASNETS_CFLAGS += -Iasnets-cpddl

ASNETS_LDFLAGS += -Lasnets-cpddl -lpddl
ASNETS_LDFLAGS += -Lpheromone -lpheromone
ASNETS_LDFLAGS += $(PHEROMONE_LDFLAGS)
ASNETS_LDFLAGS += $(DYNET_LDFLAGS)
ASNETS_LDFLAGS += -lm -lstdc++

TARGETS = asnets

all:

asnets: asnets.c pheromone asnets-cpddl
	$(CC) $(ASNETS_CFLAGS) -o $@ $< $(ASNETS_LDFLAGS)

pheromone: pheromone/libpheromone.a
pheromone/libpheromone.a: pheromone/Makefile
	cd pheromone && $(MAKE)
pheromone/Makefile:
	git submodule update --init -- pheromone

asnets-cpddl: asnets-cpddl/libpddl.a
asnets-cpddl/libpddl.a: asnets-cpddl/Makefile
	cd asnets-cpddl && $(MAKE) DYNET_ROOT=$(DYNET_ROOT)
asnets-cpddl/Makefile:
	git submodule update --init -- asnets-cpddl

fd-action-policy-testing: pheromone
	cd fd-action-policy-testing && PHRM_ROOT=$(ROOTDIR)/pheromone python3 build.py testing


clean:
	rm -f $(TARGETS)

mrproper: clean
	if [ -f pheromone/Makefile ]; then $(MAKE) -C pheromone clean; fi;
	if [ -f asnets-cpddl/Makefile ]; then $(MAKE) -C asnets-cpddl mrproper; fi


help:
	@echo "Variables:"
	@echo "  CC      = $(CC)"
	@echo "  CXX     = $(CXX)"
	@echo "  DEBUG   = $(DEBUG)"
	@echo "  WERROR  = $(WERROR)"
	@echo "  CFLAGS  = $(CFLAGS)"
	@echo "  PHEROMONE_LDFLAGS = $(PHEROMONE_LDFLAGS)"
	@echo "  DYNET_ROOT = $(DYNET_ROOT)"
	@echo "  DYNET_LDFLAGS = $(DYNET_LDFLAGS)"
	@echo "  ASNETS_CFLAGS = $(ASNETS_CFLAGS)"
	@echo "  ASNETS_LDFLAGS = $(ASNETS_LDFLAGS)"

.PHONY: all clean mrproper pheromone asnets-cpddl \
        fd-policy-testing
