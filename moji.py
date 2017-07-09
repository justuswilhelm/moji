#!/usr/bin/env python3
from pandocfilters import walk
from logging import getLogger, basicConfig
from sys import stdin
import json


logger = getLogger(__name__)
basicConfig(level='DEBUG')


code_block = 1
files = {}
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