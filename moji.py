#!/usr/bin/env python3
from collections import defaultdict
from pandocfilters import walk
from sys import stdin
import json
import logging
import re


FRAGMENT_RE = re.compile(r"(?P<indentation>\s*)##\s+(?P<fragment_name>\w+)")


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


code_block = 1
files = defaultdict(list)
fragments = {}


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


if __name__ == "__main__":
    print("This will appear inside the __main__ if block")
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