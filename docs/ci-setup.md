# CI Integration

skillforge includes a GitHub Actions workflow for validating skills in pull requests.

## Setup

Copy `.github/workflows/skill-check.yml` to your repository. The workflow:

1. Checks out the repository
2. Sets up Python 3.12
3. Installs skillforge
4. Runs `skillforge validate --strict` on the `.skills/` directory

## Customising

Adjust the `SKILLS_PATH` environment variable to point to your skills directory if it differs from `.skills/`.

## Example

```yaml
name: Skill Check
on:
  pull_request:
    paths:
      - '.skills/**'
      - '.github/workflows/skill-check.yml'
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'
      - run: pip install skillforge
      - run: skillforge validate --strict .skills/
```
