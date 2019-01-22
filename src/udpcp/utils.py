__all__ = [
    'Identifier',
    'get_best_selector_class',
]

import itertools
import selectors

from typing import Type


class Identifier:

    def __init__(self):
        self._generator = itertools.cycle(range(1, 0xFFFF))

    def next(self) -> int:
        return next(self._generator)


def get_best_selector_class() -> Type[selectors.BaseSelector]:
    for selector in ['EpollSelector', 'PollSelector', 'SelectSelector']:
        if hasattr(selectors, selector):
            return getattr(selectors, selector)

    raise RuntimeError('Could not get any selector class')
