# encoding: utf-8
"""Type hints."""

from typing import (
	Any as _A,
	ClassVar as _ClassVar, Protocol as _P, TypeVar as _TypeVar
)

from dataclasses import Field as _Field


# Borrowed from typeshed's `DataclassInstance`:
# https://github.com/python/typeshed/blob/7030b265d887eeacee07e47aa2cca412b07950c4/stdlib/_typeshed/__init__.pyi#L399
# noinspection PyPep8Naming
class P_Dataclass(_P):
	"""Protocol for an instance of any dataclass."""
	__dataclass_fields__: _ClassVar[dict[str, _Field[_A]]]


T = _TypeVar('T')
T_Dataclass = _TypeVar('T_Dataclass', bound=P_Dataclass)
