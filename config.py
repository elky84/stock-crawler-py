import os
import pathlib
from collections import ChainMap

from typing import Mapping


class Configure:

    def __init__(self, pre_configure: Mapping={}):
        self._config = ChainMap(pre_configure)

    @property
    def raw(self):
        return dict(self._config)

    @classmethod
    def from_path(cls, path: pathlib.Path):
        """Load configuration from given ``path``\ , first it guess that file
        is TOML, if it fails, try to parse file as a ``env``

        """
        if not path.exists():
            raise TypeError('inexist path: {}'.format(path))
        with open(str(path), 'r') as f:
            source = f.read()
        try:
            c = cls.loads_env(source)
        except Exception:
            raise ValueError('.env expected, '
                             'found: {}'.format(source))
        return cls(c)

    @classmethod
    def loads_env(cls, source: str) -> Mapping:
        """Load ``.env`` file from given ``source``

        .. code-block:: python

           base = pathlib.Path('.')
           config = Configure.loads_env('a=1')

        :return: a loaded configuration from ``.env``
        :rtype: :class:`collections.abc.Mapping`

        """
        return {
            k.strip(): v.rstrip()
            for k, v in [
                line.split('=') for line in source.split('\n')
                if '=' in line
            ]
        }

    @property
    def logging_formatter(self):
        logging = {
            'version': 1,
            'formatters': {
                'default': {
                    'format':
                        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
                }
            },
            'handlers': {
                'console': {
                    'formatter': 'default',
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://sys.stdout',
                },
                'file': {
                    'formatter': 'default',
                    'class': 'logging.handlers.TimedRotatingFileHandler',
                    'filename': 'crawler.log',
                    'when': 'midnight',
                    'encoding': 'utf-8',
                    'utc': True
                },
            },
            'loggers': {
                'crawler': {
                    'handlers': ['console', 'file'],
                    'level': 'DEBUG'
                }
            }
        }
        return logging
   
config = Configure.from_path(
    pathlib.Path(os.path.dirname(__file__)) / '.env'
)
