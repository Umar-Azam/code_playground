import meshcat
import meshcat.geometry as g
import numpy as np
from lie_group import *


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
    Rx = element_SE3(np.array([0,0,-np.pi/2]),np.array([0,0,0])) 
    Ry = element_SE3(np.array([0,0,0]),np.array([0,0,0]))
    Rz = element_SE3(np.array([np.pi/2,0,0]),np.array([0,0,0])) 

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



def vector_generator(input_visualizer : meshcat.Visualizer, position1 : np.ndarray, position2 : np.ndarray, name_space : str = "vectors"):
    """
    Generate a Vector in the visualizer
    """
    # create meshcat geometry objects for cylinders pointing in the x,y,z directions
    length = np.linalg.norm(position2 - position1)

    if length < 1e-6:
        return input_visualizer
    
    radius = 0.02
    Translate = element_SE3([0,0,0],[0,length/2,0])

    y_cylinder = g.Cylinder(length, radius)

    #generator matrix
    gen_y = np.array([[0,0,-1],[0,0,0],[1,0,0]]).T
    unit_v = (position2 - position1)/length

    rot_axis =  gen_y @ unit_v
    rot_angle = np.arccos(np.dot(unit_v, [0,1,0]))

    cross_length = np.linalg.norm(rot_axis) 
    if cross_length  < 1e-6:
        Rot =  element_SE3(np.array([0,0,0]),position1)
    else :
        Rot =  element_SE3(rot_axis * rot_angle / cross_length , position1)

    # visualize the arrows in the visualizer
    input_visualizer[f"{name_space}/vector0"].set_object(y_cylinder, g.MeshLambertMaterial(color=hex(np.random.randint(0, 0xFFFFFF))))

    input_visualizer[f"{name_space}/vector0"].set_transform(Rot @ Translate)

    return input_visualizer