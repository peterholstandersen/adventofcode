import matplotlib.pyplot as plt
import numpy as np

dim = 1000
thinkness = 40
size = 1200

u= np.linspace(0, 2*np.pi, 100)
v= np.linspace(0, 2*np.pi, 100)
u, v = np.meshgrid(u, v)
a = thinkness
b = dim
X = (b + a*np.cos(u)) * np.cos(v)
Y = (b + a*np.cos(u)) * np.sin(v)
Z = a * np.sin(u)

fig = plt.figure(figsize=(16,16))
ax = fig.add_subplot(111, projection='3d')
fig.set_facecolor('black')
ax.set_facecolor('black')
ax.xaxis.set_pane_color("black")
ax.yaxis.set_pane_color("black")
ax.zaxis.set_pane_color("black")
ax.grid(False)

ax.set_xlim(-size, size)
ax.set_ylim(-size, size)
ax.set_zlim(-size, size)
ax.set_aspect("equal")

ax.plot_surface(X, Y, Z, alpha=0.5, cmap="winter", shade=True)
plt.show()