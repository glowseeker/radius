from matplotlib.patches import Circle
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, TextBox
import numpy as np

# Create figure and subplots
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

# Left pane - coordinate grid
ax1.grid(True)
ax1.axhline(0, color='black', linewidth=1)
ax1.axvline(0, color='black', linewidth=1)
ax1.set_xlim(-10, 10)
ax1.set_ylim(-10, 10)
ax1.set_aspect('equal')

# Set ticks and labels
ax1.set_xticks(range(-10, 11, 1))
ax1.set_yticks(range(-10, 11, 1))
ax1.xaxis.set_tick_params(labelsize=8)
ax1.yaxis.set_tick_params(labelsize=8)

# Right pane - sliders and textboxes
ax2.axis('off')  # Hide the axis for sliders

# Draw two circles
inner_circle = Circle((0, 0), 1, fill=False, color='blue', linewidth=2)
outer_circle = Circle((0, 0), 2, fill=False, color='red', linewidth=2)
ax1.add_patch(inner_circle)
ax1.add_patch(outer_circle)

# Create sliders
ax_inner = plt.axes([0.6, 0.7, 0.3, 0.05])
ax_outer = plt.axes([0.6, 0.6, 0.3, 0.05])
slider_inner = Slider(ax_inner, 'Inner Circle', 0.1, 10.0, valinit=1, valfmt=None, valstep=0.1)
slider_outer = Slider(ax_outer, 'Outer Circle', 0.1, 10.0, valinit=2, valfmt=None, valstep=0.1)

# Create textboxes
tb_inner = TextBox(plt.axes([0.6, 0.5, 0.3, 0.05]), 'Inner:', initial=str(inner_circle.radius))
tb_outer = TextBox(plt.axes([0.6, 0.4, 0.3, 0.05]), 'Outer:', initial=str(outer_circle.radius))

# Display intersection point below sliders
intersection_point, = ax1.plot(0, 2, 'ro')  # 'ro' means red circle
intersection_text = plt.text(0.6, 0.3, f'Intersection: {intersection_point}', transform=plt.gcf().transFigure)

# Tangent line
tangent_line, = ax1.plot([], [], color='green', linewidth=1)

# Update function for sliders and textboxes
def update(val):
    inner_radius = slider_inner.val
    outer_radius = slider_outer.val

    # Clamp max values of sliders
    slider_inner.valmax = outer_radius
    slider_outer.valmin = inner_radius

    tb_inner.set_val(str(inner_radius))
    tb_outer.set_val(str(outer_radius))
    inner_circle.set_radius(inner_radius)
    outer_circle.set_radius(outer_radius)

    # Update intersection point and its display
    intersection_coords = (0, outer_radius)
    intersection_text.set_text(f'Intersection: {intersection_coords}')
    intersection_point.set_data(*intersection_coords)

    # Calculate the slope of the line
    if inner_radius < outer_radius:
        x_intercept = np.sqrt(outer_radius ** 2 - inner_radius ** 2)
        slope = x_intercept / -inner_radius
        x_vals = np.linspace(-x_intercept, x_intercept, 100) + 0
        y_vals = slope * (x_vals - 0) + outer_radius
        tangent_line.set_data(x_vals, y_vals)
    else:
        tangent_line.set_data([], [])


    fig.canvas.draw_idle()

# Update function for textboxes
def update_textbox(val):
    inner_radius = min(float(tb_inner.text), 10.0)  # Ensure value is not greater than 10
    outer_radius = min(float(tb_outer.text), 10.0)  # Ensure value is not greater than 10

    # Ensure inner radius is not larger than outer radius
    if inner_radius > outer_radius:
        inner_radius = outer_radius
        tb_inner.set_val(str(inner_radius))  # Update the textbox value

    # Ensure outer radius is not smaller than inner radius
    if outer_radius < inner_radius:
        outer_radius = inner_radius
        tb_outer.set_val(str(outer_radius))  # Update the textbox value

    slider_inner.set_val(inner_radius)
    slider_outer.set_val(outer_radius)
    update(None)

# Call update function when textbox value is changed
tb_inner.on_submit(update_textbox)
tb_outer.on_submit(update_textbox)

# Call update function when slider value is changed
slider_inner.on_changed(update)
slider_outer.on_changed(update)

# Show plot
plt.show()