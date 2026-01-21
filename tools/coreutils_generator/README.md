# Coreutils Output Generator

This tool generates reference outputs for coreutils commands with various option combinations, designed to create authentic mock data for unit tests.

## Overview

The generator creates deterministic test environments in Docker containers and executes coreutils commands with different option combinations. Results are saved as JSON fixtures that can be used in unit tests for realistic mocking.

## Features

- **Tiered Testing Strategy**: Generates combinations at different coverage levels
- **Docker Execution**: Runs commands in isolated, deterministic containers
- **JSON Output**: Structured fixtures with command metadata
- **Configurable**: YAML-based configuration for commands and environments

## Quick Start

### Generating Fixtures

**⚠️ Important:** If you encounter `FileNotFoundError` when running tests that use `load_coreutils_output()`, you need to generate the fixtures first.

1. **Build the Docker image:**
   ```bash
   cd /home/pyroxar/Dokumenty/mancer
   PYTHONPATH=/home/pyroxar/Dokumenty/mancer python3 tools/coreutils_generator/cli.py --rebuild-image
   ```

2. **Generate all fixtures for all commands (recommended):**
   ```bash
   cd /home/pyroxar/Dokumenty/mancer
   PYTHONPATH=/home/pyroxar/Dokumenty/mancer python3 tools/coreutils_generator/cli.py --pipeline --clean --tiers tier0 tier1
   ```
   
   This will generate fixtures for: `ls`, `cat`, `echo`, `wc`, `grep`, `sort`, `uniq`, `head`, `tail`

3. **Generate outputs for specific commands only:**
   ```bash
   PYTHONPATH=/home/pyroxar/Dokumenty/mancer python3 tools/coreutils_generator/cli.py --pipeline --commands ls cat --tiers tier0 tier1
   ```

4. **Preview what will be generated (dry run):**
   ```bash
   PYTHONPATH=/home/pyroxar/Dokumenty/mancer python3 tools/coreutils_generator/cli.py --pipeline --dry-run
   ```

## Configuration

### commands.yaml
Defines which commands to generate outputs for, with their arguments and popular option combinations.

### environments.yaml
Docker environment configuration including image tags and execution settings.

## Output Structure

```
tests/fixtures/coreutils_outputs/
├── ls/
│   ├── tier0_basic.json
│   ├── tier0_-l.json
│   └── tier1_-la.json
├── cat/
│   └── ...
└── manifest.json  # Index of all fixtures
```

## Using in Tests

```python
from tests.fixtures.loader import load_coreutils_output

def test_ls_long_format():
    output = load_coreutils_output("ls", "tier1_-la")
    assert "file1.txt" in output["result"]["stdout"]
    assert output["result"]["exit_code"] == 0
```

**Note:** If you get `FileNotFoundError` when running tests, the fixtures are missing. Generate them using:
```bash
PYTHONPATH=/home/pyroxar/Dokumenty/mancer python3 tools/coreutils_generator/cli.py --pipeline --clean --tiers tier0 tier1
```

## Tier Coverage

- **Tier 0**: Basic usage + individual popular options
- **Tier 1**: Popular option combinations from documentation
- **Tier 2**: Pairwise coverage (each option pair tested)
- **Tier 3**: Error scenarios (missing files, permissions)
- **Tier 4**: Full combinatorial (limited depth for performance)
