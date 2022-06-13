import typing as t

from collections import namedtuple


Order = namedtuple('Order', 'min_amount max_amount currency price seller_id')


class Collector:
    def collect(self) -> t.Iterable[Order]:
        raise NotImplementedError
