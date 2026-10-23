# encoding: utf-8
"""Essential utils for dataclasses, that should've always been there. No bloat."""
__all__ = [
	# `__typing`:
	'_P_Dataclass', '_T_Dataclass', '_T', '_A',

	# `_conditional_args`:
	# '_OptionalKwargsMeta',  # deliberately excluded - available only by explicit import
	'NotMatchArgs', 'KWOnly', 'Slots', 'WeakrefSlot',

	# here:
	'dc_fields_dict', 'dc_override', 'FieldAccessPropsDC', 'UnsafeInitDC'
]

import typing as _t
from typing import (
	Dict as _Dict, Tuple as _Tuple,
	overload as _overload
)

from abc import ABCMeta as __ABCMeta
from dataclasses import fields as _fields, Field as _Field

from .__typing import (
	_A, _Mapping, _P,
	T as _T, T_KWMap as _T_KWMap, T_KWMap_co as _T_KWMap_co,
	P_Dataclass as _P_Dataclass, T_Dataclass as _T_Dataclass
)
from ._conditional_args import *
from ._conditional_args import _OptionalKwargsMeta


class __DictFactory(_P[_T_KWMap_co]):
	def __call__(self, __data: _t.Iterable[_Tuple[str, _A]]) -> _T_KWMap_co: ...


@_overload
def dc_fields_dict(obj: _T_Dataclass) -> _Dict[str, _A]: ...
@_overload
def dc_fields_dict(obj: _T_Dataclass, *, dict_factory: __DictFactory[_T_KWMap]) -> _T_KWMap: ...

def dc_fields_dict(obj: _T_Dataclass, *, dict_factory: __DictFactory[_Mapping[str, _A]] = dict) -> _Mapping[str, _A]:
	"""Return the field names/values from the dataclass instance - as new dict/mapping.

	Unlike built-in ``asdict()``, doesn't do it recursively. I.e., no deep-copy, and
	nested dataclass instances are kept as-is.
	"""
	field_names = (field.name for field in _fields(obj))
	return dict_factory(
		(name, getattr(obj, name))
		for name in field_names
	)


def dc_override(obj: _T_Dataclass, **overrides) -> _T_Dataclass:
	"""Copy a dataclass instance to a new one, with optional overrides.

	No deep-copy (nested mutable objects are reused, unless overridden).
	"""
	obj_dict = dc_fields_dict(obj)
	obj_dict.update(overrides)
	dataclass_type = type(obj)
	return dataclass_type(**obj_dict)


class FieldAccessPropsDC(metaclass=__ABCMeta):
	"""ABC for dataclass. Adds 3 class methods:

	- ``fields``: ``tuple`` with all the fields defined for the dataclass.
	- ``field_names``: ``tuple`` with field names.
	- ``field_names_set`` same, but as ``frozenset``.

	All three methods are cached: unlike the built-in ``fields(MyDataClass)``,
	they build the collection only once on first call per each dataclass,
	and return the same result for all further calls.

	The ``@dataclass`` decorator still need to be used on concrete dataclasses.

	Example::

		@dataclass
		class MyDataClass(FieldAccessPropsDC): ...
	"""

	@classmethod
	def fields(cls: _t.Type[_T_Dataclass]) -> _Tuple[_Field, ...]:
		""" Class method: full equivalent of ``fields(MyDataClass)``, but also...

		Cached per dataclass: all further calls reuse the first result.
		"""
		try:
			# noinspection PyUnresolvedReferences
			return cls.__cached_dataclass_fields
		except AttributeError:
			fields = tuple(_fields(cls))
			# noinspection PyAttributeOutsideInit
			cls.__cached_dataclass_fields = fields
			return fields

	@classmethod
	def field_names(cls: _t.Type[_T_Dataclass]) -> _Tuple[str, ...]:
		"""Class method: ``tuple`` with names of all the dataclass fields.

		Cached per dataclass: all further calls reuse the first result.
		"""
		try:
			# noinspection PyUnresolvedReferences
			return cls.__cached_dataclass_field_names
		except AttributeError:
			names = tuple(f.name for f in cls.fields())
			# noinspection PyAttributeOutsideInit
			cls.__cached_dataclass_field_names = names
			return names

	@classmethod
	def field_names_set(cls: _t.Type[_T_Dataclass]) -> frozenset[str]:
		"""Class method: ``frozenset`` with names of all the dataclass fields.

		Cached per dataclass: all further calls reuse the first result.
		"""
		try:
			# noinspection PyUnresolvedReferences
			return cls.__cached_dataclass_field_names_set
		except AttributeError:
			names = frozenset(cls.field_names())
			# noinspection PyAttributeOutsideInit
			cls.__cached_dataclass_field_names_set = names
			return names


class UnsafeInitDC(FieldAccessPropsDC):
	"""
	Adds ``unsafe_init()`` class-method: it creates a new instance while
	silently swallowing any invalid keyword-arguments (not defined in the dataclass).

	Inherits from ``FieldAccessPropsDC``, so also adds the same 3 class methods.

	The ``@dataclass`` decorator still need to be used on concrete dataclasses.

	Example::

		@dataclass
		class MyDataClass(UnsafeInitDC):
			aaa: int = 42
			bbb: float = 3.1416

		unfiltered_dict_of_kwargs = dict(aaa=7, qqq='string', www=None)
		instance = MyDataClass.unsafe_init(**unfiltered_dict_of_kwargs)
		# MyDataClass(aaa=7, bbb=3.1416), no error
	"""

	@classmethod
	def unsafe_init(cls: _t.Type[_T_Dataclass], **kwargs) -> _T_Dataclass:
		"""
        Class method: create the dataclass instance while passing any extra
        garbage fields in arguments - they will just be ignored.
        """
		valid_names = cls.field_names_set()
		valid_kwargs = {k: v for k, v in kwargs.items() if k in valid_names}
		return cls(**valid_kwargs)
