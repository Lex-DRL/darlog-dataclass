<div align="center">

# darlog-dataclass

[![PyPI][pypi-shield]][pypi-url]
[![GitHub Release][github-release-shield]][github-release-url]

[pypi-shield]: https://img.shields.io/pypi/v/darlog-dataclass?logo=pypi
[pypi-url]: https://pypi.org/p/darlog-dataclass
[github-release-shield]: https://img.shields.io/github/v/release/Lex-DRL/darlog-dataclass?logo=github
[github-release-url]: https://github.com/Lex-DRL/darlog-dataclass/releases/latest

*A tiny module with **ABSOLUTELY** essential utils for dataclasses, that should've **always** been there.*
</div>

> [!NOTE]
> By design, this package is as minimal as possible, providing only the **truly** must-have stuff.
> 
> No bloat.

---

Despite the whole point of built-in dataclasses is to prevent boilerplate code - counter-intuitively, this is exactly what they lead to if you try to write clean, pythonic and - especially - **type-hinted** code.

To avoid heavy dependencies, I kept reimplementing basically the same stuff for dataclasses in many of my python projects, until I got sick of it. So, here's this package. I made it just for myself *(to share the heavily reused code between the projects)*, but feel free to use it.

## Type-hints

Defines:
- `_P_Dataclass` as dataclass protocol;
- `_T_Dataclass` as its respective (bound) `TypeVar`;
- `_T` as a bonus (just an arbitrary `TypeVar`).

They're deliberately named as protected members (start with `_`), but still imported with:
```python
from darlog.dataclass import *
```

## Conditional kwargs

`dataclass` decorator has different sets of arguments for various python versions. Infamously, `slots` was added only in `3.10`. The following static classes behave like dicts that specify (or not) a specific argument, depending on the current version of python interpreter.

| Class | What adds | If python is... |
|---|---|---|
| `Slots` | `slots=True` | 3.10+ |
| `KWOnly` | `kw_only=True` | 3.10+ |
| `NotMatchArgs` | `match_args=False` | 3.10+ |
| `WeakrefSlot` | `weakref_slot=True` | 3.11+ |

Usage is simple: just pass them as unpacked kwargs:
```python
from darlog.dataclass import *

@dataclass(frozen=True, **Slots)
class DataClassWithSlotsWhenPossible: ...

@dataclass(**Slots, **WeakrefSlot)
class DataClassWithWeakrefSlotsWhenPossible: ...
```

The metaclass they're made with - `_OptionalKwargsMeta` - is also available to make your own python-version-dependent kwargs. But it's imported only explicitly:
```python
from darlog.dataclass import _OptionalKwargsMeta

class FrozenOnlySince39(metaclass=_OptionalKwargsMeta):
    kwargs = dict(frozen=True)
    min_python = (3, 9)

@dataclass(**FrozenOnlySince39)
class MyDataClass: ...
```

## Utility functions
- `dc_fields_dict`: Return all the field names/values from the dataclass instance - as dict. No deep-copy.
- `dc_override`: Copy a dataclass instance to a new one, with optional overrides.

## Base classes to inherit from
The following ABC classes define class-level methods:
- `FieldAccessPropsDC` - adds:
  - `fields` - tuple of `Field`,
  - `field_names` - tuple of `str`,
  - `field_names_set` - frozenset of `str`.
- `UnsafeInitDC` - adds `unsafe_init`, which silently swallows any invalid keyword arguments and creates the instance anyway (as long as required arguments passed).