import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv('signed_triangles_summary.csv')

x = df['congress_number'].values
y= df['pnn_over_total'].values

plt.figure(figsize=(8, 5))
plt.scatter(x, y, label="Data")

m, b = np.polyfit(x, y, 1)
plt.plot(x, m * x + b, color="red", label="Line of best fit")

plt.xlabel("Congress")
plt.ylabel("Fraction of balanced PNN triangles")
plt.title("Trend in positive_negative_negative_fraction_of_balanced_triangles")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()


