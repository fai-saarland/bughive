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

#LDFLAGS += -L. -lbughive -pthread
LDFLAGS += libbughive.a -pthread

DEP  = Makefile
DEP += src/msg/flatbuffers_common_reader.h
DEP += third-party/nng/build/libnng.a

SRC  = policy_server
SRC += policy_client

OBJS := $(foreach obj,$(SRC),.objs/$(obj).o)

TESTS  = policy_server
TESTS += policy_cat_fdr_task_fd
TESTS := $(foreach t,$(TESTS),test/test_$(t))

libbughive_standalone.a: $(OBJS) $(MAKE_FILES)
	rm -f $@
	$(AR) cr $@ $(OBJS)
	$(RANLIB) $@

libbughive.a: libbughive_standalone.a third-party/nng/build/libnng.a third-party/flatcc/lib/libflatcc.a
	rm -f $@
	$(AR) -rcT $@ $^
	$(RANLIB) $@

test: $(TESTS)

.objs/%.o: src/%.c bughive/%.h $(DEP)
	$(CC) $(CFLAGS) -c -o $@ $<

test/test_%: test/%.c libbughive.a
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

src/msg/flatbuffers_common_reader.h: third-party/flatcc/bin/flatcc msg/*.fbs
	./third-party/flatcc/bin/flatcc -o src/msg -a msg/*.fbs
	touch $@


python: $(FLATC)
	rm -rf python/msg/*
	$(FLATC) --python -o python/msg/ msg/*

clean:
	rm -f .objs/*.o
	rm -f src/msg/*.h
	rm -rf python/msg/*
	rm -f $(TESTS)

mrproper: clean third-party-clean

third-party: flatcc nanomsg flatbuffers
third-party-clean: flatcc-clean nanomsg-clean flatbuffers-clean

flatcc: third-party/flatcc/lib/libflatcc.a
third-party/flatcc/lib/libflatcc.a: third-party/flatcc/bin/flatcc
third-party/flatcc/bin/flatcc: third-party/flatcc/README.md
	rm -rf third-party/flatcc/build && mkdir third-party/flatcc/build
	cd third-party/flatcc/build && cmake -DFLATCC_TEST=OFF -DFLATCC_CXX_TEST=OFF -DFLATCC_REFLECTION=OFF ..
	cd third-party/flatcc/build && $(MAKE)
third-party/flatcc/README.md:
	git submodule update --init -- third-party/flatcc
flatcc-clean:
	cd third-party/flatcc && git clean -fdx .

nanomsg: third-party/nng/build/libnng.a
third-party/nng/build/libnng.a: third-party/nng/README.adoc
	rm -rf third-party/nng/build && mkdir third-party/nng/build
	cd third-party/nng/build && cmake -DNNG_ENABLE_NNGCAT=OFF -DNNG_TESTS=OFF -DNNG_TOOLS=OFF ..
	cd third-party/nng/build && $(MAKE)
third-party/nng/README.adoc:
	git submodule update --init -- third-party/nng
nanomsg-clean:
	cd third-party/nng && git clean -fdx .


flatbuffers: $(FLATC)
$(FLATC): third-party/flatbuffers/LICENSE
	rm -rf third-party/flatbuffers/build && mkdir third-party/flatbuffers/build
	cd third-party/flatbuffers/build \
        && cmake -DFLATBUFFERS_BUILD_FLATLIB=OFF \
                 -DFLATBUFFERS_BUILD_TESTS=OFF \
                 -DFLATBUFFERS_INSTALL=OFF \
                 -DFLATBUFFERS_BUILD_FLATC=ON ..
	cd third-party/flatbuffers/build && $(MAKE)

third-party/flatbuffers/LICENSE:
	git submodule update --init -- third-party/flatbuffers
flatbuffers-clean:
	cd third-party/flatbuffers && git clean -fdx .



help:
	@echo "Targets:"
	@echo "  all    - Build C library (default)"
	@echo "  python - Build python library"
	@echo ""
	@echo "  clean             - Remove all generated files"
	@echo "  mrproper          - Clean library and third-party/"
	@echo "  third-party-clean - Clean all third-party projects."
	@echo ""
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
