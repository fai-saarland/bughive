-include Makefile.config
-include Makefile.include

AR ?= ar
RANLIB ?= ranlib
CC ?= gcc
CFLAGS ?=
LDFLAGS ?= -L. -lbughive -pthread

CFLAGS += -Wall -pedantic
CFLAGS += -g
CFLAGS += -I.
CFLAGS += -Ithird-party/flatcc/include
CFLAGS += -Ithird-party/nng/include/nng/compat

#MAKE_FILES := Makefile Makefile.include $(wildcard Makefile.config)
DEP  = Makefile
DEP += src/msg/flatbuffers_common_reader.h
DEP += third-party/nng/build/libnng.a

SRC  = policy_server
SRC += policy_client

OBJS := $(foreach obj,$(SRC),.objs/$(obj).o)

TESTS  = policy_server
TESTS += policy_cat_fdr_task_fd
TESTS := $(foreach t,$(TESTS),test/test_$(t))

all: libbughive.a test

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


clean:
	rm -f .objs/*.o
	rm -f src/msg/*.h
	rm -f $(TESTS)

mrproper: clean third-party-clean

third-party: flatcc nanomsg
third-party-clean: flatcc-clean nanomsg-clean

flatcc: third-party/flatcc/lib/libflatcc.a
third-party/flatcc/lib/libflatcc.a: third-party/flatcc/bin/flatcc
third-party/flatcc/bin/flatcc: third-party/flatcc/README.md
	rm -rf third-party/flatcc/build && mkdir third-party/flatcc/build
	cd third-party/flatcc/build && cmake -DFLATCC_TEST=OFF -DFLATCC_CXX_TEST=OFF -DFLATCC_REFLECTION=OFF ..
	cd third-party/flatcc/build && make
third-party/flatcc/README.md:
	git submodule update --init -- third-party/flatcc
flatcc-clean:
	cd third-party/flatcc && git clean -fdx .

nanomsg: third-party/nng/build/libnng.a
third-party/nng/build/libnng.a: third-party/nng/README.adoc
	rm -rf third-party/nng/build && mkdir third-party/nng/build
	cd third-party/nng/build && cmake -DNNG_ENABLE_NNGCAT=OFF -DNNG_TESTS=OFF -DNNG_TOOLS=OFF ..
	cd third-party/nng/build && make
third-party/nng/README.adoc:
	git submodule update --init -- third-party/nng
nanomsg-clean:
	cd third-party/nng && git clean -fdx .




help:
	@echo "Targets:"
	@echo "  all         - Build library (default)"
	@echo ""
	@echo "  clean             - Remove all generated files"
	@echo "  mrproper          - Clean library and third-party/"
	@echo "  third-party-clean - Clean all third-party projects."
	@echo ""
	@echo "Variables:"
	@echo "  SYSTEM  = $(SYSTEM)"
	@echo "  CC      = $(CC)"
	@echo "  CXX     = $(CXX)"
	@echo "  AR      = $(AR)"
	@echo "  RANLIB  = $(RANLIB)"
	@echo "  SH      = $(SH)"
	@echo "  DEBUG   = $(DEBUG)"
	@echo "  PROFIL  = $(PROFIL)"
	@echo "  WERROR  = $(WERROR)"
	@echo "  CFLAGS  = $(CFLAGS)"
	@echo "  LDFLAGS = $(LDFLAGS)"
	@echo ""
	@echo "  LDFLAGS_EXTRA = $(LDFLAGS_EXTRA)"
	@echo "  SYSTEM_LDFLAGS = $(SYSTEM_LDFLAGS)"

.PHONY: all flatcc nanomsg
