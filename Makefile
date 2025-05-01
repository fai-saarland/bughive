-include Makefile.config

ROOTDIR := $(dir $(realpath $(word $(words $(MAKEFILE_LIST)),$(MAKEFILE_LIST))))

DEBUG ?= no
WERROR ?= no
TEST_LAB_ENV ?= no
ENABLE_GPU ?= no

ifeq '$(ENABLE_GPU)' 'yes'
	HAS_NVCC := $(shell which nvcc 1> /dev/null 2>& 1 && echo yes || echo no)
	USE_GPU ?= $(HAS_NVCC)
else
	USE_GPU ?= no
endif

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

PHEROMONE_LDFLAGS ?= $(ROOTDIR)/pheromone/libpheromone.a $(shell pkg-config --libs grpc++ protobuf)

#DYNET_ROOT ?= /opt/dynet
#DYNET_LDFLAGS ?= -L$(DYNET_ROOT)/lib -Wl,-rpath=$(DYNET_ROOT)/lib -ldynet
DYNET_CPPFLAGS ?= -I$(realpath dynet)
DYNET_LDFLAGS ?= -L$(realpath dynet)/build/dynet -Wl,-rpath=$(realpath dynet)/build/dynet -ldynet -lstdc++
DYNET_CMAKE_CONFIG := -DEIGEN3_INCLUDE_DIR=$(realpath .)/eigen-fp16 -Wno-dev #-DENABLE_BOOST=ON
ifeq '$(USE_GPU)' 'yes'
	DYNET_CMAKE_CONFIG += -DBACKEND=cuda
else
	DYNET_CMAKE_CONFIG += -DBACKEND=eigen 
endif

ASNETS_CFLAGS := $(CFLAGS)
ASNETS_CFLAGS += -Iasnets-cpddl

ASNETS_LDFLAGS += -Lasnets-cpddl -lpddl
ASNETS_LDFLAGS += $(PHEROMONE_LDFLAGS)
ASNETS_LDFLAGS += $(DYNET_LDFLAGS)
ASNETS_LDFLAGS += -lm -lstdc++

TARGETS = asnets

all: asnets asnets-bin pheromone fd-action-policy-testing dynet eigen

asnets: policy-servers/asnets.c pheromone/libpheromone.a asnets-cpddl/libpddl.a
	$(CC) $(ASNETS_CFLAGS) -o policy-servers/$@ $< $(ASNETS_LDFLAGS)

eigen-fp16/INSTALL: eigen-fp16.zip # currently used eigen commit: c29c800126982c561e8d0b9255dc65474cd98de3 git@gitlab.com:Flamefire/eigen.git
	unzip -n eigen-fp16.zip
	touch eigen-fp16/INSTALL
eigen: eigen-fp16/INSTALL


dynet: dynet/build/libdynet.so
dynet/build/libdynet.so: eigen-fp16/INSTALL
	cmake -S dynet -B dynet/build $(DYNET_CMAKE_CONFIG)
	cmake --build dynet/build -- -j 8

pheromone: pheromone/libpheromone.a
pheromone/libpheromone.a: pheromone/Makefile
	cd pheromone && $(MAKE)
pheromone/libpheromone.so: pheromone/Makefile
	cd pheromone && $(MAKE) libpheromone.so

pheromone/Makefile:
	if [ $(TEST_LAB_ENV) = no ]; then git submodule update --init -- pheromone; fi

asnets-cpddl: asnets-cpddl/bin/pddl-asnets
asnets-cpddl/libpddl.a: asnets-cpddl/Makefile dynet/build/libdynet.so
	cd asnets-cpddl && $(MAKE) USE_DYNET=yes USE_SQLITE=yes DYNET_CPPFLAGS="$(DYNET_CPPFLAGS)" DYNET_LDFLAGS="$(DYNET_LDFLAGS)"
asnets-cpddl/bin/pddl-asnets: asnets-cpddl/Makefile dynet/build/libdynet.so
	cd asnets-cpddl && $(MAKE) USE_DYNET=yes USE_SQLITE=yes DYNET_CPPFLAGS="$(DYNET_CPPFLAGS)" DYNET_LDFLAGS="$(DYNET_LDFLAGS)" bin
asnets-cpddl/Makefile:
	if [ $(TEST_LAB_ENV) = no ]; then git submodule update --init -- asnets-cpddl; fi
asnets-bin: asnets-cpddl/bin/pddl-asnets


fd-action-policy-testing: fd-action-policy-testing/build.py pheromone/libpheromone.a
	cd fd-action-policy-testing && PHRM_ROOT=$(ROOTDIR)/pheromone python3 build.py release
fd-action-policy-testing-debug: fd-action-policy-testing/build.py pheromone/libpheromone.a
	cd fd-action-policy-testing && PHRM_ROOT=$(ROOTDIR)/pheromone python3 build.py debug
fd-action-policy-testing/build.py:
	if [ $(TEST_LAB_ENV) = no ]; then git submodule update --init -- fd-action-policy-testing; fi

clean:
	rm -f $(TARGETS)

mrproper: clean
	if [ -f pheromone/Makefile ]; then $(MAKE) -C pheromone clean; fi;
	if [ -f asnets-cpddl/Makefile ]; then $(MAKE) -C asnets-cpddl mrproper; fi
	if [ -d fd-action-policy-testing/builds ]; then rm -rf fd-action-policy-testing/builds; fi
	if [ -d dynet/build ]; then rm -rf dynet/build; fi

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
	@echo "  MAKEFLAGS = $(MAKEFLAGS)"
	@echo "  BUGHIVE_UPDATE_SUBMODULES = $(BUGHIVE_UPDATE_SUBMODULES)"

.PHONY: all clean mrproper pheromone asnets-cpddl \
        fd-action-policy-testing fd-action-policy-testing-debug


