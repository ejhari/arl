#!/usr/bin/env python
"""Test the sandbox executor."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from arl.integrations.sandbox.executor import SandboxExecutor


def test_basic_execution():
    """Test basic code execution."""
    print("Testing basic Python execution...")

    executor = SandboxExecutor()

    code = '''
print("Hello from sandbox!")
result = 2 + 2
print(f"2 + 2 = {result}")
'''

    result = executor.execute_code(code)

    print(f"Success: {result.success}")
    print(f"Exit Code: {result.exit_code}")
    print(f"Output:\n{result.stdout}")
    if result.stderr:
        print(f"Errors:\n{result.stderr}")

    assert result.success, "Execution should succeed"
    assert "Hello from sandbox!" in result.stdout, "Output should contain greeting"
    print("✓ Basic execution test passed\n")


def test_scientific_libraries():
    """Test scientific library availability."""
    print("Testing scientific libraries...")

    executor = SandboxExecutor()

    code = '''
import numpy as np
import pandas as pd
import matplotlib
import scipy
import sklearn

print(f"NumPy version: {np.__version__}")
print(f"Pandas version: {pd.__version__}")
print(f"Matplotlib version: {matplotlib.__version__}")
print(f"SciPy version: {scipy.__version__}")
print(f"Scikit-learn version: {sklearn.__version__}")

# Test basic operations
arr = np.array([1, 2, 3, 4, 5])
print(f"Array mean: {arr.mean()}")

df = pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]})
print(f"DataFrame shape: {df.shape}")
'''

    result = executor.execute_code(code)

    print(f"Success: {result.success}")
    print(f"Output:\n{result.stdout}")

    assert result.success, "Library imports should succeed"
    assert "NumPy version:" in result.stdout, "NumPy should be available"
    assert "Array mean: 3.0" in result.stdout, "NumPy operations should work"
    print("✓ Scientific libraries test passed\n")


def test_file_artifact_generation():
    """Test artifact generation and collection."""
    print("Testing artifact generation...")

    executor = SandboxExecutor()

    code = '''
import json

# Create a data file
data = {"experiment": "test", "value": 42}
with open("results.json", "w") as f:
    json.dump(data, f)

# Create a text file
with open("log.txt", "w") as f:
    f.write("Experiment completed successfully\\n")

print("Artifacts created")
'''

    result = executor.execute_code(code)

    print(f"Success: {result.success}")
    print(f"Artifacts collected: {len(result.artifacts)}")
    print(f"Output:\n{result.stdout}")

    assert result.success, "Execution should succeed"
    assert len(result.artifacts) >= 2, "Should collect artifacts"
    print(f"✓ Artifact generation test passed (found {len(result.artifacts)} artifacts)\n")


def test_error_handling():
    """Test error handling for failing code."""
    print("Testing error handling...")

    executor = SandboxExecutor()

    code = '''
# This will cause a runtime error
result = 1 / 0
'''

    result = executor.execute_code(code)

    print(f"Success: {result.success}")
    print(f"Exit Code: {result.exit_code}")

    assert not result.success, "Execution should fail"
    assert result.exit_code != 0, "Exit code should be non-zero"
    print("✓ Error handling test passed\n")


def main():
    """Run all tests."""
    print("=" * 60)
    print("ARL Sandbox Executor Test Suite")
    print("=" * 60)
    print()

    try:
        test_basic_execution()
        test_scientific_libraries()
        test_file_artifact_generation()
        test_error_handling()

        print("=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
