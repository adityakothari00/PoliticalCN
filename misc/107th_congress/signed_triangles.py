import pandas as pd
import networkx as nx
from itertools import combinations

# Constants
edgeFile = "S107_edges.csv"
outputFile = "S107_triangle_counts.csv"

# Choose which column determines the sign
SIGN_COLUMN = "signed_weight"

# Ignore edges with exactly zero sign
ignoreZeroSign = True


# Load edge list from CSV
edges_df = pd.read_csv(edgeFile)

print("Loaded edges:")
print(edges_df.head())
print(edges_df.shape)


# Builds the signed graph from the edge list
G = nx.Graph()

for _, row in edges_df.iterrows():
    u = int(row["source"])
    v = int(row["target"])
    sign_value = row[SIGN_COLUMN]

    if sign_value > 0:
        sign = "+"
    elif sign_value < 0:
        sign = "-"
    else:
        sign = "0"

    if ignoreZeroSign and sign == "0":
        continue

    G.add_edge(u, v, sign=sign, signed_weight=sign_value)

print("Stats of graph built:")
print("Nodes:", G.number_of_nodes())
print("Edges:", G.number_of_edges())


# Counting triangles
ppp_count = 0
pmm_count = 0
other_count = 0

triangle_rows = []

nodes = list(G.nodes())

for a, b, c in combinations(nodes, 3):
    if G.has_edge(a, b) and G.has_edge(a, c) and G.has_edge(b, c):
        s1 = G[a][b]["sign"]
        s2 = G[a][c]["sign"]
        s3 = G[b][c]["sign"]

        signs = sorted([s1, s2, s3])

        if signs == ["+", "+", "+"]:
            triangle_type = "(+,+,+)"
            ppp_count += 1
        elif signs == ["+", "-", "-"]:
            triangle_type = "(+,-,-)"
            pmm_count += 1
        else:
            triangle_type = "other"
            other_count += 1

        triangle_rows.append({
            "node1": a,
            "node2": b,
            "node3": c,
            "sign_ab": s1,
            "sign_ac": s2,
            "sign_bc": s3,
            "triangle_type": triangle_type
        })

triangle_df = pd.DataFrame(triangle_rows)

print("\nTriangle counts:")
print("(+,+,+):", ppp_count)
print("(+,-,-):", pmm_count)
print("other:", other_count)
print("total triangles:", len(triangle_df))


# export sumamry dataframe
summary_df = pd.DataFrame([
    {"triangle_type": "(+,+,+)", "count": ppp_count},
    {"triangle_type": "(+,-,-)", "count": pmm_count},
    {"triangle_type": "other", "count": other_count},
    {"triangle_type": "total", "count": len(triangle_df)}
])

summary_df.to_csv(outputFile, index=False)

print(f"\nSaved summary to: {outputFile}")


# full triangle list export
triangle_df.to_csv("S107_all_triangles.csv", index=False)
print("Saved full triangle list to: S107_all_triangles.csv")
