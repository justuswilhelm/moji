moji.py moji.pdf: moji.md
	pandoc --filter ./moji.py $^ -o moji.pdf
