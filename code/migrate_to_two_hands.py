import pandas as pd
import shutil
import os

INPUT_FILE = "models/training_data.csv"
BACKUP_FILE = "models/training_data_backup_63feat.csv"

shutil.copy(INPUT_FILE, BACKUP_FILE)
print(f"Backup saved to {BACKUP_FILE}")

df = pd.read_csv(INPUT_FILE)
old_feature_cols = [c for c in df.columns if c != "label"]
assert len(old_feature_cols) == 63, f"Expected 63 feature columns, found {len(old_feature_cols)}"

rename_map = {}
for i in range(21):
    for axis in ["x", "y", "z"]:
        rename_map[f"{axis}{i}"] = f"h1_{axis}{i}"

df = df.rename(columns=rename_map)

for i in range(21):
    for axis in ["x", "y", "z"]:
        df[f"h2_{axis}{i}"] = 0.0

ordered_cols = ["label"]
for i in range(21):
    for axis in ["x", "y", "z"]:
        ordered_cols.append(f"h1_{axis}{i}")
for i in range(21):
    for axis in ["x", "y", "z"]:
        ordered_cols.append(f"h2_{axis}{i}")

df = df[ordered_cols]
df.to_csv(INPUT_FILE, index=False)
print(f"Migrated {len(df)} rows \u2192 126 features (63 real + 63 zero-padded).")
print(f"Total columns now: {len(df.columns) - 1} features + label")
