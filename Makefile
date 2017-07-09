SOURCE = README.md
TARGET = moji.py moji.pdf

.PHONY: moji.py Makefile

all: $(TARGET)

moji.py Makefile: $(SOURCE)
	pandoc $^ --to=json --preserve-tabs | ./moji.py

moji.pdf: $(SOURCE)
	pandoc -o $@ $^