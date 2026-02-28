---
name: "invalid-skill"
description: "An invalid skill for testing validation."
version: "not-semver"
allowed_tools:
  - nonexistent_tool
asset_paths:
  - missing-file.txt
unknown_field: true
---

# invalid-skill

This skill should fail validation.
