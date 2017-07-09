# Test

## Files

```files
moji.py
```

## Prelude

```{file=moji.py}
#!/usr/bin/env python3
from pandocfilters import toJSONFilter
from logging import getLogger, basicConfig
```

## Set Up Logging

```{file=moji.py}
logger = getLogger(__name__)
basicConfig(level='DEBUG')
```

## Filter Action

```{file=moji.py}
def action(key, value, format, meta):
    """."""
    if key != 'CodeBlock':
        return
    [[ident, classes, keyvals], code] = value
    keyvals = dict(keyvals)
    logger.debug(value)
    if 'files' in classes:
        for path in code.splitlines():
            open(path, 'w').close()
    else:
        with open(keyvals['file'], 'a') as fd:
            fd.write(code.strip() + "\n\n\n")
```

## Call Main Method

```{file=moji.py}
if __name__ == "__main__":
    toJSONFilter(action)
```
