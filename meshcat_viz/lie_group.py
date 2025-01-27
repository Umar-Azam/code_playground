import numpy as np
import sympy as sp

# Method to generate a rotation matrix element of SO(3)
def rotation_matrix(rot_axis : np.ndarray, coord_type='exponential') -> np.ndarray:
  """
  Generates a rotation matrix given components theta_x, theta_y, and theta_z, and .

  Args:
    rot_axis: [theta_x, theta_y, theta_z] The components of the rotation axis.
    coord_type: The type of coordinates to use. Options are 'exponential' and 'euler'.

  Returns:
    A NumPy array representing the 3x3 rotation matrix.
  """
  theta_x, theta_y, theta_z = rot_axis

  # Generate the generators of the Lie algebra so(3)
  gen_x = np.array([[0, 0, 0], [0, 0, 1], [0, -1, 0]]).T
  gen_y = np.array([[0, 0, -1], [0, 0, 0], [1, 0, 0]]).T
  gen_z = np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 0]]).T

  # Split components to unit vector for rotation and angular speed
  angle = np.sqrt(theta_x**2 + theta_y**2 + theta_z**2)
  if (angle < 1e-6):
    omega = np.array([0, 0, 0])
  else:
    omega = np.array([theta_x, theta_y, theta_z]) / angle

  # Initialize the rotation matrix
  rot_mat = np.eye(3)

  if coord_type == 'exponential':
    # Generate the exponential map of the Lie group SO(3)
    omega_skew = gen_x * omega[0] + gen_y * omega[1] + gen_z * omega[2]
    rot_mat = np.eye(3) + np.sin(angle) * omega_skew + (1 - np.cos(angle)) * omega_skew @ omega_skew
  
  elif coord_type == 'euler':
    # Generate the symbolic representation of the rotation matrix
    symat_x = sp.matrices.Matrix(theta_x * gen_x)
    symat_y = sp.matrices.Matrix(theta_y * gen_y)
    symat_z = sp.matrices.Matrix(theta_z * gen_z)

    rot_mat_x = sp.simplify(sp.exp(symat_x))
    rot_mat_y = sp.simplify(sp.exp(symat_y))
    rot_mat_z = sp.simplify(sp.exp(symat_z))
    rot_mat = sp.simplify(rot_mat_x * rot_mat_y * rot_mat_z)

    # Convert the symbolic matrix to a NumPy array
    rot_mat = np.array(rot_mat).astype(np.float64).round(5)
  
  return rot_mat

# Method for Matrix logarithm for SO(3)
def matrix_logarithm(rot_mat : np.ndarray) -> np.ndarray:
  """
  Computes the matrix logarithm of a rotation matrix.

  Args:
    rot_mat: A NumPy array representing the 3x3 rotation matrix.

  Returns:
    A NumPy array representing the 3x3 matrix logarithm.
  """

  # Compute the angle of rotation
  cos_theta = (np.trace(rot_mat) - 1) / 2
  cos_theta = np.clip(cos_theta, -1, 1)
  theta = np.arccos(cos_theta)

  gen_x = np.array([[0, 0, 0], [0, 0, 1], [0, -1, 0]]).T
  gen_y = np.array([[0, 0, -1], [0, 0, 0], [1, 0, 0]]).T
  gen_z = np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 0]]).T

  if np.isclose(theta, 0):
    return np.zeros((3,3))
  
  # Edge case for if the angle is pi
  if np.isclose(theta, np.pi) or np.isclose(theta, -np.pi):
    w = 1
    # TODO

  
  


# Method to generate an element of the Lie group SE(3)
def element_SE3(w, p, coord_type='exponential') -> np.ndarray:
  theta_x,theta_y,theta_z = w
  x,y,z = p
  se3mat = np.eye(4)
  se3mat[:3,:3] = rotation_matrix([theta_x, theta_y, theta_z], coord_type=coord_type)
  se3mat[:3,3] = np.array([x,y,z])
  return se3mat

# Method to generate the inverse of an element of the Lie group SE(3)
def inverse_SE3(se3mat : np.ndarray) -> np.ndarray:
  inv_se3mat = np.eye(4)
  inv_se3mat[:3,:3] = se3mat[:3,:3].T
  inv_se3mat[:3,3] = -se3mat[:3,:3].T @ se3mat[:3,3]
  return inv_se3mat