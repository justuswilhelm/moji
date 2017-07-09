# Moji

Literate Programming Tool using Pandoc filters. The implementation is in
Python 3 using the [pandocfilters](https://github.com/jgm/pandocfilters)
package.

## Prelude

Just some standard Python imports.

```{.python file=moji.py}
#!/usr/bin/env python3
from collections import defaultdict
from pandocfilters import walk
from sys import stdin
import json
import logging
import re
```

## Regular Expressions

These are used to match Moji instructions

```{.python file=moji.py}
FRAGMENT_RE = re.compile(r"(?P<indentation>\s*)##\s+(?P<fragment_name>\w+)")
```

## Set Up Logging

I like to use logging a lot for debugging purposes, so I'm setting up a logger
here.

```{.python file=moji.py}
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
```

## Some global vars

This is where we store files and fragments, and also a global count of all
code blocks that we have created so far.

```{.python file=moji.py}
code_block = 1
files = defaultdict(list)
fragments = {}
```

## Filter Action

This is the main action for Pandoc AST traversal.

```{.python file=moji.py}
def action(key, value, format, meta):
    """."""
    if key != 'CodeBlock':
        return
    global code_block
    logger.debug("CodeBlock Nr. %d", code_block)
    code_block += 1

    ((_, classes, keyvals), code) = value
    keyvals = dict(keyvals)
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

```python
## fragment_name
```

with the correct fragment, like so

```python
print("Hello, World!")
```


Furthermore, great care is taken to match the indent
level at the position that contained the fragment reference. Therefore, if

```python
    ## fragment_name
```

is defined, it will be replaced with a fragment like so

```python
    print("Hello, World!")
```

```{.python file=moji.py}
def indent_fragment(fragment, indent):
    """Return the fragment with each line prepended by 'indent'."""
    for line in fragment.splitlines():
        yield "{}{}".format(indent, line)


def replace_fragments(block):
    """Replace a designated fragment with a stored fragment."""
    def _iter():
        for line in block.splitlines():
            match = FRAGMENT_RE.match(line)
            if match:
                fragment_name = match.group('fragment_name')
                indentation = match.group('indentation')
                logger.debug("Found 'fragment' %s in %s", fragment_name, path)
                fragment = fragments[fragment_name]
                yield from indent_fragment(fragment, indentation)
            else:
                yield line
    return "\n".join(_iter())
```

## Call Main Method

Here we parse, process and output the JSON.

```{.python file=moji.py}
if __name__ == "__main__":
    ## fragment
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

```{.python fragment=fragment}
print("This will appear inside the __main__ if block")
```


## Makefile

Finally, a makefile shall be created.

```{.makefile file=Makefile}
SOURCE = README.md
TARGET = moji.py moji.pdf

.PHONY: moji.py Makefile

all: $(TARGET)

moji.py Makefile: $(SOURCE)
	pandoc $^ --to=json --preserve-tabs | ./moji.py

moji.pdf: $(SOURCE)
	pandoc -o $@ $^
```

## TODO

- [ ] Add a second pandoc filter that makes code block parameters visible
in the PDF.
- [ ] Remove code block count.

## Further Reading

- [pandocfilters](https://github.com/jgm/pandocfilters)
- [Pandoc User Guide](https://github.com/jgm/pandocfilters)
- [Wikipedia on Literate Programming](https://en.wikipedia.org/wiki/Literate_programming)
