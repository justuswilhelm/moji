# Test

## Files

```files
Makefile
moji.py
```

## Prelude

```{file=moji.py}
#!/usr/bin/env python3
from pandocfilters import walk
from logging import getLogger, basicConfig
from sys import stdin
import json
```

## Set Up Logging

```{file=moji.py}
logger = getLogger(__name__)
basicConfig(level='DEBUG')
```

## Some global vars

```{file=moji.py}
code_block = 1
files = {}
fragments = {}
```

## Filter Action

```{file=moji.py}
def action(key, value, format, meta):
    """."""
    if key != 'CodeBlock':
        return
    global code_block
    logger.debug("CodeBlock Nr. %d", code_block)
    code_block += 1

    ((_, classes, keyvals), code) = value
    keyvals = dict(keyvals)
    if 'files' in classes:
        for path in code.splitlines():
            logger.debug("Seen file %s", path)
            files[path] = []
    else:
        if 'file' in keyvals:
            path = keyvals['file']
            logger.debug("Appending to %s", path)
            files[path].append(code)
        elif 'fragment' in keyvals:
            fragment = keyvals['fragment']
            logger.debug("Adding fragment %s")
            fragments[fragment] = code
```

## Fragment Replacement

```{file=moji.py}
def replace_fragments(block):
    """Replace a designated fragment with a stored fragment."""
    def _iter():
        for line in block.splitlines():
            if line.startswith('##'):
                fragment_name = line[2:]
                logger.debug("Found fragment %s in %s", fragment_name, path)
                fragment = fragments[fragment_name]
                yield fragment
            else:
                yield line
    return "\n".join(_iter())
```

## Call Main Method

```{file=moji.py}
if __name__ == "__main__":
##fragment
    tree = json.loads(stdin.read())
    walk(tree, action, '', {})
    for fragment, content in fragments.items():
        for path, content in files.items():
            content = list(map(replace_fragments, content))
            files[path] = content

    for path, content in files.items():
        with open(path, 'w') as fd:
            logger.debug("Finalizing file %s", path)
            fd.write("\n\n\n".join(content))
```

## Fragment Example

```{fragment=fragment}
    print("This will appear inside the __main__ if block")
```


## Makefile

```{file=Makefile}
SOURCE = README.md
TARGET = moji.py moji.pdf

.PHONY: moji.py Makefile

all: $(TARGET)

moji.py Makefile: $(SOURCE)
	pandoc $^ --to=json --preserve-tabs | ./moji.py

moji.pdf: $(SOURCE)
	pandoc -o $@ $^
```
