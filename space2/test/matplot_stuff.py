import matplotlib.animation as animation
import matplotlib.pyplot as plt

circle1 = plt.Circle((0, 0), 0.2, color='brown', clip_on=False)
circle2 = plt.Circle((0.5, 0.5), 0.2, color='orange', clip_on=False)
circle3 = plt.Circle((1, 1), 0.2, color='olivedrab', clip_on=False)

plt.style.use('dark_background')

px = 1/plt.rcParams['figure.dpi']
fig, ax = plt.subplots(figsize=(2048/4*3*px, 2048/4*3*px))


# fig.add_axes([0,0,0,0], visible=False)

ax.set_axis_off()
ax.set_frame_on(False)

ax.margins(x=0.0, y=0.0)

ax.add_patch(circle1)
ax.add_patch(circle2)
ax.add_patch(circle3)

def update(frame):
    print(circle1.center)
    circle1.center = (circle1.center[0] + px, circle1.center[1] + px)
    print(frame)

ani = animation.FuncAnimation(fig=fig, func=update, interval=100) # 500 ms

plt.show()


