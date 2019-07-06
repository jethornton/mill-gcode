HTML = $(patsubst %.txt,%.html,$(shell find -name \*.txt))

all: $(HTML)

clean:
	rm -f $(HTML)

%.html: %.txt
	cd $(<D) && asciidoc $(<F)

.PHONY: all clean

