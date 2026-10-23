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