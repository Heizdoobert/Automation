---
name: airtest-agent
description: Automates and maintains Airtest (Python) test cases in this repository. Use when the user mentions Airtest, .air folders, air_tests/, pages/, template images, writing a new test case, reviewing/editing an existing test, or listing/understanding project structure.
---

# Airtest Agent (Project Skill)

## Quick Start

Apply this workflow when working on this repo's Airtest tests:

- Keep test cases in `air_tests/` (often inside `*.air/` folders).
- Use page objects in `pages/` and shared code in `common/`.
- Image templates must be referenced as relative paths starting with `images/` (matching `pages/images/`).
- Prefer core Airtest APIs: `touch`, `swipe`, `wait`, `exists`, `assert_exists`, `snapshot`, `start_app`, `stop_app`, `home`, `keyevent`, `text`.
- Do not add extra dependencies or change file structure unless explicitly requested.
- Any file write/edit must be preceded by showing the proposed code/diff and obtaining explicit user confirmation; recommend a backup first.

## Skill Scope and Triggers

Use this skill when the user asks to:

- Understand/list project structure (folders like `air_tests/`, `pages/`, `common/`, `pixon/`).
- View/understand a test case (e.g., "xem test", "show tc01", "đọc file .py trong air_tests").
- Generate a new test from natural-language steps.
- Edit a test based on review feedback (add steps, change templates, improve waiting/assertions).
- Validate Python syntax after generating or editing code.

## Standard Workflows

### 1) Understand project structure

If asked about structure, identify the repo root by locating these directories (when present): `air_tests/`, `pages/`, `common/`, `pixon/`.

If asked to "list tests", enumerate `*.py` under `air_tests/` (ignore caches like `__pycache__`).

### 2) Read and summarize a test case

When the user names a test loosely (partial name like `tc01_daily_mission`):

1. Find matching `*.py` files under `air_tests/`.
2. If multiple candidates exist, present the candidate paths and ask the user to choose.
3. Read the selected file and summarize:
   - Main test flow (key steps in order).
   - Which templates are used (the `Template("images/...")` paths).
   - Where assertions happen (`assert_exists`) and what is being validated.

### 3) Generate a new test case from a description

Follow this sequence:

1. Extract steps, inputs, and expected outcomes from the user's description.
2. Map each step to Airtest actions (`touch`, `text`, `wait`, `assert_exists`, etc.).
3. Produce a complete Python file matching the repo style:
   - `from airtest.core.api import *`
   - Optional `setup()` only when needed (e.g., `start_app`).
   - One or more `test_*` functions with clear names.
   - `if __name__ == "__main__":` to run.
4. Ensure all template paths are relative and start with `images/`.
5. Perform a basic syntax validation (e.g., using `ast.parse`/`compile` conceptually).
6. Ask where to save (relative path), then show the full code.
7. Ask for explicit confirmation before writing; recommend creating a backup if overwriting.

### 4) Edit a test case from review feedback

1. Identify the target file (list options if ambiguous).
2. Read the current content.
3. Apply the requested changes while preserving the overall file structure (imports, function layout, `if __name__`).
4. Prefer stable UI interactions:
   - Add `wait(..., timeout=...)` before `touch(...)` when elements might not be ready.
   - Use `assert_exists` for explicit validations.
5. Validate syntax after edits.
6. Show the updated full code (or a focused diff) and ask for explicit confirmation before writing; recommend a backup.

### 5) Syntax validation

After generating/editing Python:

- Check for obvious syntax issues (indentation, missing parentheses/quotes, invalid function defs).
- If a syntax issue exists, fix it and re-present the corrected code.

### 6) Safety and confirmation

Before any write operation:

- Ask for explicit confirmation (yes/no).
- Recommend backing up first (e.g., copy to a `.bak` file).
- Avoid modifying unrelated files.

## Optional Integration: Repo-local helper tools

If a repo-local helper exists (commonly named `cursor_agent_tools.py`):

- Prefer using its safe wrappers (e.g., read/write/syntax validation) instead of re-implementing ad-hoc helpers.
- If it does not exist, proceed with standard file operations while still following the confirmation/backup workflow.

## Additional Resources

- Usage examples: see [examples.md](examples.md)
