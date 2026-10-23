# encoding: utf-8
"""
Static classes to be used as conditional keyword-arguments added only on compatible python versions.
"""

import typing as _t
from typing import Dict as _Dict

from sys import version_info as _version_info

from .__typing import _A


def _validator_kwargs(value) -> bool:
	"""Validate value for ``kwargs`` field."""
	return isinstance(value, _t.Mapping) and all(
		isinstance(k, str) for k in value
	)


def _validator_version(value) -> bool:
	"""Validate value for ``min_python`` field."""
	return not value or (
		isinstance(value, tuple) and value and all(isinstance(x, int) for x in value)
	)


class _OptionalKwargsMeta(type, _t.Mapping[str, _A]):
	"""
	A metaclass to make static classes that act as
	conditional keyword-arguments added only on compatible python versions.

	Requires to specify two class-level fields: ``kwargs`` and ``min_python``.

	Example::

		class Slots(metaclass=_OptionalKwargsMeta):
			kwargs = dict(slots=True)
			min_python = (3, 10)

	Then use::

		@dataclass(<your args>, **Slots)
		class MyDataClass: ...
	"""
	__eq__ = type.__eq__
	__hash__ = type.__hash__

	def __new__(mcs, name: str, bases: _t.Tuple[type, ...], namespace: _Dict[str, _A], **kwds):
		reserved_fields = {'__cached_kwargs', }
		required_fields: _Dict[str, _t.Tuple[str, _t.Callable[[_A], bool]]] = {
			# name: (what, type-validator)
			'kwargs': (
				'a mapping with str keys',
				_validator_kwargs
			),
			'min_python': (
				'a tuple of ints',
				_validator_version
			),
		}

		clashing_names = [f for f in reserved_fields if f in namespace]
		if clashing_names:
			joined = ', '.join(clashing_names)
			s = 's' if len(clashing_names) > 1 else ''
			raise TypeError(f"<{name}> can't define field{s}: {joined}")

		missing_names = [f for f in required_fields if f not in namespace]
		if missing_names:
			joined = ', '.join(
				f"{x!r} as {required_fields[x][0]}" for x in missing_names
			)
			s = 's' if len(missing_names) > 1 else ''
			raise TypeError(f"<{name}> must define class field{s}: {joined}")

		type_errors = []
		for req_field, (what, validator) in required_fields.items():
			value = namespace[req_field]
			if not validator(value):
				type_errors.append(f"{req_field} must be {what!r} (got: {value!r})")
		if type_errors:
			joined = ', '.join(type_errors)
			s = 's' if len(type_errors) > 1 else ''
			raise TypeError(f"Wrong type of class-field{s} on <{name}>: {joined}")

		new_class = super().__new__(mcs, name, bases, namespace, **kwds)

		# Explicitly reassign to prevent IDE from complaining + enforce type + copy:
		new_class.kwargs = {k: v for k, v in namespace['kwargs'].items()}
		new_class.min_python = tuple(namespace['min_python'])

		return new_class

	def __call__(cls, *args, **kwargs) -> _t.NoReturn:
		raise TypeError(f"{cls.__name__} is a static class and cannot be instantiated")

	@property
	def active_kwargs(cls) -> _Dict[str, _A]:
		try:
			# noinspection PyUnresolvedReferences
			return cls.__cached_kwargs
		except AttributeError:
			min_python = cls.min_python
			kwargs: _Dict[str, _A] = dict(cls.kwargs) if (not min_python or _version_info >= min_python) else {}
			# noinspection PyAttributeOutsideInit
			cls.__cached_kwargs = kwargs
			return kwargs

	def __len__(cls) -> int:
		return len(cls.active_kwargs)

	def __iter__(cls) -> _t.Iterator[str]:
		return iter(cls.active_kwargs)

	def __getitem__(cls, key: str) -> _A:
		return cls.active_kwargs[key]

	def keys(cls) -> _t.KeysView[str]:
		return cls.active_kwargs.keys()

	def items(cls) -> _t.ItemsView[str, _A]:
		return cls.active_kwargs.items()


############################################################


class NotMatchArgs(metaclass=_OptionalKwargsMeta):
	"""
	Adds ``match_args=False`` under python ``3.10+``, when expanded as kwarg.

	Usage::

		@dataclass(<your args>, **NotMatchArgs)
		class MyDataClass: ...
	"""
	kwargs = dict(match_args=False)
	min_python = (3, 10)


class KWOnly(metaclass=_OptionalKwargsMeta):
	"""
	Adds ``kw_only=True`` under python ``3.10+``, when expanded as kwarg.

	Usage::

		@dataclass(<your args>, **KWOnly)
		class MyDataClass: ...
	"""
	kwargs = dict(kw_only=True)
	min_python = (3, 10)


class Slots(metaclass=_OptionalKwargsMeta):
	"""
	Adds ``slots=True`` under python ``3.10+``, when expanded as kwarg.

	Usage::

		@dataclass(<your args>, **Slots)
		class MyDataClass: ...
	"""
	kwargs = dict(slots=True)
	min_python = (3, 10)


class WeakrefSlot(metaclass=_OptionalKwargsMeta):
	"""
	Adds ``weakref_slot=True`` under python ``3.11+``, when expanded as kwarg.

	Usage::

		@dataclass(<your args>, **WeakrefSlot)
		class MyDataClass: ...
	"""
	kwargs = dict(weakref_slot=True)
	min_python = (3, 11)
