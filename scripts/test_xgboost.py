#!/usr/bin/env python
"""Test XGBoost in the sandbox."""

import asyncio
from arl.adk_agents.execution.agent import create_execution_engine
from rich.console import Console

console = Console()


async def test_xgboost():
    """Test XGBoost execution."""
    console.print("[bold cyan]Testing XGBoost in Docker Sandbox[/bold cyan]\n")

    test_code = '''
import numpy as np
import pandas as pd
from sklearn.datasets import make_classification
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
import lightgbm as lgb
from sklearn.metrics import accuracy_score

print("Generating test dataset...")
X, y = make_classification(n_samples=1000, n_features=20, n_informative=15,
                           n_redundant=5, random_state=42)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

print(f"Training set: {X_train.shape}")
print(f"Test set: {X_test.shape}")
print()

# Test Random Forest
print("Training Random Forest...")
rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)
rf_pred = rf.predict(X_test)
rf_acc = accuracy_score(y_test, rf_pred)
print(f"Random Forest Accuracy: {rf_acc:.4f}")
print()

# Test XGBoost
print("Training XGBoost...")
xgb = XGBClassifier(n_estimators=100, random_state=42, verbosity=0)
xgb.fit(X_train, y_train)
xgb_pred = xgb.predict(X_test)
xgb_acc = accuracy_score(y_test, xgb_pred)
print(f"XGBoost Accuracy: {xgb_acc:.4f}")
print()

# Test LightGBM
print("Training LightGBM...")
lgbm = lgb.LGBMClassifier(n_estimators=100, random_state=42, verbosity=-1)
lgbm.fit(X_train, y_train)
lgbm_pred = lgbm.predict(X_test)
lgbm_acc = accuracy_score(y_test, lgbm_pred)
print(f"LightGBM Accuracy: {lgbm_acc:.4f}")
print()

# Summary
print("=" * 50)
print("RESULTS SUMMARY")
print("=" * 50)
print(f"Random Forest: {rf_acc:.4f}")
print(f"XGBoost:       {xgb_acc:.4f}")
print(f"LightGBM:      {lgbm_acc:.4f}")
print()

# Save results
with open("results.txt", "w") as f:
    f.write(f"Random Forest: {rf_acc:.4f}\\n")
    f.write(f"XGBoost: {xgb_acc:.4f}\\n")
    f.write(f"LightGBM: {lgbm_acc:.4f}\\n")

print("Results saved to results.txt")
print("All tests completed successfully!")
'''

    try:
        console.print("[yellow]Executing in Docker sandbox...[/yellow]\n")

        execution_engine = create_execution_engine()
        result = await execution_engine.run(
            experiment_id="test_xgboost",
            code=test_code,
            timeout_seconds=60,
        )

        console.print(f"[bold]Success:[/bold] {result['success']}")
        console.print(f"[bold]Exit Code:[/bold] {result['exit_code']}")
        console.print()

        if result['stdout']:
            console.print("[bold green]Output:[/bold green]")
            console.print(result['stdout'])
            console.print()

        if result['stderr']:
            console.print("[bold yellow]Errors/Warnings:[/bold yellow]")
            console.print(result['stderr'])
            console.print()

        if result['success']:
            console.print("\n[bold green]✓ XGBoost, LightGBM, and Random Forest all working in Docker![/bold green]")
        else:
            console.print("\n[bold red]✗ Execution failed[/bold red]")

    except Exception as e:
        console.print(f"\n[bold red]Error:[/bold red] {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_xgboost())
