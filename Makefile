DEBUG ?= no
WERROR ?= no

AR ?= ar
RANLIB ?= ranlib
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

# TODO
DYNET_ROOT ?= /opt/dynet

ASNETS_CFLAGS := $(CFLAGS)
ASNETS_CFLAGS += -Iasnets-cpddl

ASNETS_LDFLAGS += -Lasnets-cpddl -lpddl
ASNETS_LDFLAGS += -Lpheromone -lpheromone
ASNETS_LDFLAGS += $(shell pkg-config --libs grpc++ protobuf)
# TODO
ASNETS_LDFLAGS += -L$(DYNET_ROOT)/lib -Wl,-rpath=$(DYNET_ROOT)/lib -ldynet
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
	cd asnets-cpddl && $(MAKE) DYNET_ROOT=$(DYNET_ROOT) # TODO
asnets-cpddl/Makefile:
	git submodule update --init -- asnets-cpddl


help:
	@echo "Variables:"
	@echo "  CC      = $(CC)"
	@echo "  CXX     = $(CXX)"
	@echo "  AR      = $(AR)"
	@echo "  RANLIB  = $(RANLIB)"
	@echo "  DEBUG   = $(DEBUG)"
	@echo "  WERROR  = $(WERROR)"
	@echo "  CFLAGS  = $(CFLAGS)"
	@echo "  LDFLAGS = $(LDFLAGS)"

.PHONY: all python pheromone asnets-cpddl
