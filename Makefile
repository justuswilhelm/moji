.PHONY: moji.py Makefile

moji.py Makefile: moji.md
	pandoc $^ --to=json --preserve-tabs | ./moji.py

moji.pdf: moji.md
	pandoc -o $@ $^