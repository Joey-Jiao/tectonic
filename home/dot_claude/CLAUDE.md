# Global Instructions

## Context
At the start of a session, call `info_context` to understand who I am,
my workspace, and infrastructure.

## Modes
At the start of a work session, the user will specify the mode. Load the appropriate guide:
- **Coding**: call `info_conventions` and follow it strictly for all code changes
- **Reading papers**: call `info_reading` for the reading workflow, note-taking format, and available tools

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
