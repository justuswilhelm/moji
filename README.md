# Moji

Literate Programming Tool using Pandoc filters. The implementation is in
Python 3 using the [pandocfilters](https://github.com/jgm/pandocfilters)
package.

## Files

First, we'll tell Moji which files to initialize.

[ ] TODO: Since we add append content to files, we can leave this out in the
future and use a defaultdict.

If you want to see what's happening under the hood, the markdown contains extra
classes and key-value pairs for code blocks.

[ ] TODO: Add a second pandoc filter that makes code block parameters visible
in the PDF.

```files
Makefile
moji.py
```

## Prelude

Just some standard Python imports.

```{file=moji.py}
#!/usr/bin/env python3
from pandocfilters import walk
from sys import stdin
import json
import logging
```

## Set Up Logging

I like to use logging a lot for debugging purposes, so I'm setting up a logger
here.

```{file=moji.py}
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
```

## Some global vars

This is where we store files and fragments, and also a global count of all
code blocks that we have created so far.

[ ] TODO: Remove code block count.

```{file=moji.py}
code_block = 1
files = {}
fragments = {}
```

## Filter Action

This is the main action for Pandoc AST traversal.

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

This is the algorithm that replaces occurences of

```
##fragment name
```

with the correct fragment.

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

Here we parse, process and output the JSON.

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

Here we test fragment replacement. This will later show up in the `moji.py`
file.

```{fragment=fragment}
    print("This will appear inside the __main__ if block")
```


## Makefile

Finally, a makefile shall be created.

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

## Further Reading

- [pandocfilters](https://github.com/jgm/pandocfilters)
- [Pandoc User Guide](https://github.com/jgm/pandocfilters)
- [Wikipedia on Literate Programming](https://en.wikipedia.org/wiki/Literate_programming)
