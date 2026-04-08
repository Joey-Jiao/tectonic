# Global Instructions

## Context
At the start of a session, call `profile_context` to understand who I am,
my workspace, and infrastructure.

## Code
- Before every significant code change, call `profile_conventions` and follow the conventions strictly
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
