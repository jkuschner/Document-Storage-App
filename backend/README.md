# Document Storage App Backend

## Local Dev Environment

We are using Poetry to manage the virtual environment and dependencies together.

To activate the virtual development environment:
```
poetry env activate
```

### Reconfigure Poetry for Python 3.9
If your virtual environment is not using the correct python version, follow these steps:

1. Make sure the environment is not active. If it is, type `deactivate` to exit.
2. Tell Poetry to use Python 3.9:
```
poetry env use python3.9
```
3. Install dependencies and rebuild environment
```
poetry install
```
4. Activate environment and verify Python version:
```
source $(poetry env info --path)/bin/activate
python --version
# Expected output: Python 3.9.x (or similar 3.9 version)
```

### Dependencies

- `boto3` for AWS interactions (production)
- `pytest` for unit testing (development)