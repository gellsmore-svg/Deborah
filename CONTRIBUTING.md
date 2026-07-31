# Contributing to Deborah

Deborah maintains **Cairn**, a meta-language that **evolves from real use**. The most valuable
contribution is describing a real process in Cairn and reporting what was
awkward, ambiguous, or missing — that is exactly how v0.7 was shaped (see
[`examples/`](examples/)).

## Ways to contribute

- **Feedback** — an ambiguity, gap, or rough edge → open a
  [Feedback issue](../../issues/new/choose).
- **Proposal** — a new construct, tag, or change → open a Proposal issue. Say
  what real process motivated it; concrete beats theoretical.
- **Examples** — describe a system in Cairn and add it under `examples/`. Stress
  tests are welcome, especially when they break things.
- **Discussion** — open-ended questions and ideas go in
  [Discussions](../../discussions).

## Principles a change should respect

- **Human-first.** A reader should think *"I get what's happening,"* not *"I need
  to learn the notation."* Don't add ceremony that doesn't earn its keep.
- **Progressive formality.** Precision is optional and layered; the default stays
  terse and readable.
- **Evolve from use.** New vocabulary should come from a real process that needed
  it, not from theory.

## How changes land

- Spec changes go in `SPEC.md`; structure in `GRAMMAR.md`; every change is
  recorded in `CHANGELOG.md`.
- The reserved verb and tag vocabulary grows deliberately — a proposal that adds
  to it should show the gap in a real description.

## License

By contributing, you agree your contributions are licensed under
[Apache License 2.0](LICENSE).
