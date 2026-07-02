# Global preferences

## Language & style
- I primarily code in Python. Prefer type hints and standard library where reasonable.
- Keep comments sparse — explain *why*, not *what*. No narrating obvious lines.

## Testing philosophy
- Strict TDD: write the failing test FIRST, run it, and SEE it fail before any implementation.
- Never write the test and the implementation in the same step. If I ask for a feature, give me the failing test first.
- Commit tests-first: `test: ...` then `feat: ...`.

## Communication
- Be concise and direct. Lead with the answer. Skip preamble and flattery.
- When you change dependencies or config, tell me exactly what and why in one line.
