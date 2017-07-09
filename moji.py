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
            files[path].append(code.strip())
        elif 'fragment' in keyvals:
            fragment = keyvals['fragment']
            logger.debug("Adding fragment %s")
            fragments[fragment] = (code.strip())


if __name__ == "__main__":
    ##fragment
    tree = json.loads(stdin.read())
    walk(tree, action, '', {})
    for path, content in files.items():
        with open(path, 'w') as fd:
            logger.debug("Finalizing file %s", path)
            fd.write("\n\n\n".join(content))