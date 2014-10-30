
PREFIX=/usr/local

includedir = $(PREFIX)/include
include_HEADERS = \
	include/or1k-sprs.h \
	include/or1k-nop.h \
	include/or1k-asm.h

CLEAN_FILES = \
	include/or1k-sprs.h

include/or1k-sprs.h: scripts/gen-or1k-sprs.py xml/or1k-sprs.xml
	python scripts/gen-or1k-sprs.py xml/or1k-sprs.xml > $@.tmp
	mv -f $@.tmp $@

install: $(include_HEADERS)
	install -m 755 -d $(includedir)
	install -m 644 $(include_HEADERS) $(includedir)

clean:
	rm -f $(CLEAN_FILES)