# Global Instructions

## Context
At the start of every session, ask the user to run `/mcp__strata__context`
so you understand who I am, my workspace, and infrastructure.

## Modes
At the start of a work session, the user will specify the mode and run
the corresponding strata prompt. Treat its output as authoritative:
- **Coding** → user runs `/mcp__strata__code`; follow those conventions strictly
- **Reading papers** → user runs `/mcp__strata__read`; follow that workflow exactly

## Code
- Read existing code before modifying — understand the established design patterns first
- New code must fit the existing architecture; never introduce patterns that diverge from what's already established
- No band-aid fixes, no temporary workarounds, no appeasement code — solve problems at the right layer
- Always consider architectural elegance; if a fix feels hacky, step back and find the proper solution
- Don't add comments, docstrings, or type annotations to code you didn't change
- Don't refactor surrounding code when fixing a bug
- Don't create README or documentation files unless asked

## Git
- Don't commit unless asked
- Don't push unless asked
- Don't amend commits unless asked
