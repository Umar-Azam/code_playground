import meshcat
import numpy as np
import time
import meshcat.geometry as g
import meshcat.transformations as tf
import time

# Create a visualizer instance
vis = meshcat.Visualizer().open()

# Create a SE(3) transformation matrix (4x4)
# This represents some rotation and translation
# T = np.array([
#     [0.866, -0.5, 0.0, 1.0],  # Some rotation + translation
#     [0.5, 0.866, 0.0, 2.0],
#     [0.0, 0.0, 1.0, 0.5],
#     [0.0, 0.0, 0.0, 1.0]
# ])
T = np.array([
    [0.0, -1.0, 0.0, 1.0],  # Some rotation + translation
    [1.0, 0.0, 0.0, 1.0],
    [0.0, 0.0, 1.0, 1.0],
    [0.0, 0.0, 0.0, 1.0]
])

def frame_generator(input_visualizer : meshcat.Visualizer, input_frame_name : str, input_frame_transform : np.ndarray = np.eye(4)):
    """
    Generate a frame in the visualizer
    """
    # create meshcat geometry objects for cylinders pointing in the x,y,z directions
    length = 0.5
    radius = 0.02

    x_cylinder = g.Cylinder(length, radius)
    y_cylinder = g.Cylinder(length, radius)
    z_cylinder = g.Cylinder(length, radius)

    # Create rotations to align cylinders with x,y,z axes
    Rx = tf.rotation_matrix(-np.pi/2, [0, 0, 1])  
    Ry = tf.identity_matrix()  
    Rz = tf.rotation_matrix(np.pi/2, [1, 0, 0])  

    # Move cylinders to center
    Rx[:3,3] = [length/2, 0, 0]
    Ry[:3,3] = [0, length/2, 0]
    Rz[:3,3] = [0, 0, length/2]


    # visualize the arrows in the visualizer
    input_visualizer[f"{input_frame_name}/x_axis"].set_object(x_cylinder, g.MeshLambertMaterial(color=0xff0000))
    input_visualizer[f"{input_frame_name}/y_axis"].set_object(y_cylinder, g.MeshLambertMaterial(color=0x00ff00))
    input_visualizer[f"{input_frame_name}/z_axis"].set_object(z_cylinder, g.MeshLambertMaterial(color=0x0000ff))

    input_visualizer[f"{input_frame_name}/x_axis"].set_transform(input_frame_transform @ Rx)
    input_visualizer[f"{input_frame_name}/y_axis"].set_transform(input_frame_transform @ Ry)
    input_visualizer[f"{input_frame_name}/z_axis"].set_transform(input_frame_transform @ Rz)

    return input_visualizer

# Create a frame in the visualizer
vis = frame_generator(vis, "axes")

# Create an animation that moves the frame "axes" to the SE(3) transformation T
# Create an animation
anim = meshcat.animation.Animation()

# Set initial frame (frame 0) to identity matrix
with anim.at_frame(vis, 0) as frame:
    frame["axes"].set_transform(np.eye(4))

# Set final frame (frame 30) to target transform T
with anim.at_frame(vis, 30) as frame:
    frame["axes"].set_transform(T)

vis = frame_generator(vis, "axes2")

with anim.at_frame(vis, 30) as frame:
    frame["axes"].set_transform(T)
    frame["axes2"].set_transform(np.eye(4))

# Set final frame (frame 30) to target transform T
with anim.at_frame(vis, 60) as frame:
    frame["axes"].set_transform(T @ T)
    frame["axes2"].set_transform(T)

# Send the animation to the visualizer
# Play it once with default settings
vis.set_animation(anim)


# draw a sphere at a point (1, 0,0)
sphere = g.Sphere(0.1)
vis["sphere"].set_object(sphere, g.MeshLambertMaterial(color=0xff0000))
T_sphere = np.eye(4)
T_sphere[:3,3] = [1, 0, 0]
print(T_sphere)
vis["sphere"].set_transform(T_sphere)




try:
 while True:
     time.sleep(1)
except KeyboardInterrupt:
     pass