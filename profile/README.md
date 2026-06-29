<div align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/fiberpath/.github/main/brand/lockup-horizontal-reversed.png">
    <img alt="FiberPath" src="https://raw.githubusercontent.com/fiberpath/.github/main/brand/lockup-horizontal.png" width="460">
  </picture>
</div>

**An open, machine-agnostic filament-winding path planner.**

FiberPath turns a declarative winding specification into machine toolpaths
(G-code) for filament-winding machines. It is the software — the planner and
compiler — not a single reference machine: the goal is that anyone can build a
winder to a documented compatibility contract and drive it with FiberPath.

## Where to start

- 📖 **Documentation:** <https://fiberpath.org/fiberpath>
- 🧩 **Core software:** [`fiberpath`](https://github.com/fiberpath/fiberpath) — planner, CLI, API, and desktop GUI
- 🗺️ **Roadmap:** [development/roadmap](https://fiberpath.org/fiberpath/development/roadmap/)

## Repositories

- [`fiberpath`](https://github.com/fiberpath/fiberpath) — the path planner / compiler (Python core, CLI, FastAPI, Tauri GUI)
- [`fiberpath.github.io`](https://github.com/fiberpath/fiberpath.github.io) — the documentation site / project hub
- Hardware references (machine-specific, may move out over time): a Marlin winder firmware fork and design notes

## License

FiberPath is released under the **AGPL-3.0** license.
