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

from abc import ABCMeta as __ABCMeta
from dataclasses import fields as _fields, Field as _Field

from .__typing import (
	_A, T as _T,
	P_Dataclass as _P_Dataclass, T_Dataclass as _T_Dataclass
)
from ._conditional_args import *
from ._conditional_args import _OptionalKwargsMeta


def dc_fields_dict(obj: _T_Dataclass) -> _t.Dict[str, _A]:
	"""Return all the field names/values from the dataclass instance - as dict. No deep-copy."""
	field_names = (field.name for field in _fields(obj))
	return {
		attr: getattr(obj, attr)
		for attr in field_names
	}


def dc_override(obj: _T_Dataclass, **overrides) -> _T_Dataclass:
	"""Copy a dataclass instance to a new one, with optional overrides."""
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
	def fields(cls: _t.Type[_T_Dataclass]) -> _t.Tuple[_Field, ...]:
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
	def field_names(cls: _t.Type[_T_Dataclass]) -> _t.Tuple[str, ...]:
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
