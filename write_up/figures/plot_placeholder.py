import matplotlib.pyplot as plt
import numpy as np

# Create Data
x = np.linspace(0.0, 5.0)

y = np.cos(2 * np.pi * x) * np.exp(-x)

# Set up figure
f = plt.figure(figsize=(7, 7))
ax = f.add_subplot(111)

# Plot data and trendline
ax.plot(x, y, 'o--', color="red")

ax.set_xlabel("\n $No!\ X\ axis\ is\ best\ axis$", ha='center', va='center', fontsize=24)
ax.set_ylabel("$Y\ axis\ is\ best\ axis$\n", ha='center', va='center', fontsize=24)


# Show plot
plt.savefig("./placeholderfig.png")
