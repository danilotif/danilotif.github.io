import pandas as pd
import umap
from sklearn.preprocessing import StandardScaler

df = pd.read_csv("ingredients.csv")

# Separate metadata from numeric features
meta_cols = ["Category", "Description", "Nutrient Data Bank Number"]
feature_cols = [c for c in df.columns if c not in meta_cols]

# Convert to numeric and fill NaN with 0
features = df[feature_cols].apply(pd.to_numeric, errors="coerce").fillna(0)

# Standardize
scaled = StandardScaler().fit_transform(features)

# UMAP to 2D
reducer = umap.UMAP(n_components=2, random_state=42, min_dist=0.7, n_neighbors=100)
embedding = reducer.fit_transform(scaled)

# Build output
out = df[meta_cols].copy()
out["x"] = embedding[:, 0]
out["y"] = embedding[:, 1]
out.to_csv("food_2d.csv", index=False)

print(f"Done: {len(out)} rows written to food_2d.csv")
