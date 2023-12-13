from turtle import width
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.widgets import Slider
import numpy as np

# Create a figure and axis
fig, ax = plt.subplots(figsize=(9, 5))

# Adjust the position of the subplot
plt.subplots_adjust(left=0.1, right=0.5)

width = 20
height = 20

# Create axes for sliders
axcolor = 'lightgoldenrodyellow'
ax_inner = plt.axes([0.75, 0.1, 0.15, 0.03], facecolor=axcolor)
ax_outer = plt.axes([0.75, 0.15, 0.15, 0.03], facecolor=axcolor)

# Set the limits of the plot
ax.set_xlim([-width//2, width//2])
ax.set_ylim([-height//2, height//2])

# Create sliders
s_inner = Slider(ax_inner, 'Inner Radius', 0.1, 10.0, valinit=1)
s_outer = Slider(ax_outer, 'Outer Radius', 0.1, 10.0, valinit=2)

# Draw faint grid lines
ax.set_xticks(np.arange(-width//2, width//2, 1), minor=True)
ax.set_yticks(np.arange(-height//2, height//2, 1), minor=True)
ax.grid(color='gray', linestyle='-', linewidth=0.5)

# Draw thicker axes at x=0 and y=0
ax.axhline(0, color='r', linewidth=2)
ax.axvline(0, color='r', linewidth=2)

# Draw two circles
inner_circle = Circle((0, 0), 1, fill=False, color='blue', linewidth=2)
outer_circle = Circle((0, 0), 2, fill=False, color='blue', linewidth=2)
ax.add_patch(inner_circle)
ax.add_patch(outer_circle)

# Update function for sliders
def update(val):
    inner_radius = s_inner.val
    outer_radius = s_outer.val
    inner_circle.set_radius(inner_radius)
    outer_circle.set_radius(outer_radius)
    fig.canvas.draw_idle()

# Call update function when slider value is changed
s_inner.on_changed(update)
s_outer.on_changed(update)

# Labels
plt.xticks(np.arange(-width//2, width//2 + 1, 1))
plt.yticks(np.arange(-height//2, height//2 + 1, 1))

# Set the aspect ratio to 1
plt.gca().set_aspect('1.0')

# Show the plot
plt.show()