import numpy as np


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

  # Initialize the rotation matrix
  rot_mat = np.eye(3)

  if coord_type == 'exponential':
    # Generate the exponential map of the Lie group SO(3)
    rot_mat = matrix_so3_exp(rot_axis)
  
  elif coord_type == 'euler':

    rot_mat_x = matrix_so3_exp(np.array([1, 0, 0]) * rot_axis[0])
    rot_mat_y = matrix_so3_exp(np.array([0, 1, 0]) * rot_axis[1])
    rot_mat_z = matrix_so3_exp(np.array([0, 0, 1]) * rot_axis[2])

    # Compute the rotation matrix based on desired order of rotations
    rot_mat = rot_mat_z @ rot_mat_y @ rot_mat_x
  
  return rot_mat


# Method to generate the matrix exponential for SO(3)
def matrix_so3_exp(w : np.ndarray) -> np.ndarray:
  """
  Computes the matrix exponential of a skew-symmetric matrix in so(3).

  Args:
    w: A NumPy array representing the 3x1 vector in so(3).

  Returns:
    A NumPy array representing the 3x3 rotation matrix.
  """

  # Compute the angle of rotation
  angle = np.sqrt(w[0]**2 + w[1]**2 + w[2]**2)
  if (angle < 1e-6):
    omega = np.array([0, 0, 0])
  else:
    omega = w / angle

  # Generate the exponential map of the Lie group SO(3)
  omega_skew =  so3_hat(omega)
  rot_mat = np.eye(3) + np.sin(angle) * omega_skew + (1 - np.cos(angle)) * omega_skew @ omega_skew

  return rot_mat


# Method for Matrix logarithm for SO(3)
def matrix_so3_logarithm(rot_mat : np.ndarray) -> np.ndarray:
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

  if np.isclose(theta, 0):
    return np.zeros((3,3))
  
  # Edge case for if the angle is +-pi
  if np.isclose(theta, np.pi) or np.isclose(theta, -np.pi):
    w = np.zeros(3)
    # check which case will apply for axis
    index = np.argmax(np.abs([rot_mat[0,0]+1, rot_mat[1,1]+1, rot_mat[2,2]+1]))
    w[index] = np.sqrt((rot_mat[index,index] + 1) / 2)
    w[(index + 1) % 3] = rot_mat[index, (index + 1) % 3] / (2 * w[index])
    w[(index + 2) % 3] = rot_mat[index, (index + 2) % 3] / (2 * w[index])
    return so3_hat(w) * np.pi
  
  # Compute the skew-symmetric matrix
  omega_skew = (rot_mat - rot_mat.T)/(2*np.sin(theta))

  return omega_skew * theta
  
    

# Method to compute the hat operator of a vector in so(3)
def so3_hat(omega : np.ndarray) -> np.ndarray:
  """
  Computes the hat operator of a vector in so(3).

  Args:
    omega: A NumPy array representing the 3x1 vector in so(3).

  Returns:
    A NumPy array representing the 3x3 skew-symmetric matrix.
  """
  # Generators for the Lie algebra so(3)
  gen_x = np.array([[0, 0, 0], [0, 0, 1], [0, -1, 0]]).T
  gen_y = np.array([[0, 0, -1], [0, 0, 0], [1, 0, 0]]).T
  gen_z = np.array([[0, 1, 0], [-1, 0, 0], [0, 0, 0]]).T

  return omega[0] * gen_x + omega[1] * gen_y + omega[2] * gen_z

# Method to compute the vee operator of a skew-symmetric matrix in so(3)
def so3_vee(omega_hat : np.ndarray) -> np.ndarray:
  """
  Computes the vee operator of a skew-symmetric matrix in so(3).

  Args:
    omega_hat: A NumPy array representing the 3x3 skew-symmetric matrix.

  Returns:
    A NumPy array representing the 3x1 vector in so(3).
  """
  omega = np.array([omega_hat[2,1], omega_hat[0,2], omega_hat[1,0]])
  return omega



# Method to generate the matrix exponential for SE(3)

def matrix_se3_exp(twist : np.ndarray) -> np.ndarray:
  """
  Computes the matrix exponential of a twist (S * θ) in se(3) .

  Args:
    twist: A NumPy array representing the 6x1 twist vector in se(3) of shape [wx wy wz vx vy vz].T 

  Returns:
    A NumPy array representing the 4x4 transformation matrix.
  """

  se3_mat = np.eye(4)

  # Extract the angular and linear velocities
  angle = np.sqrt(twist[0]**2 + twist[1]**2 + twist[2]**2)

  if np.isclose(angle, 0):
    se3_mat[:3,3] = twist[3:]
    return se3_mat
  
  omega_skew = so3_hat(twist[:3]) / angle  
  p = (np.eye(3) * angle + (1 - np.cos(angle)) * omega_skew + (angle - np.sin(angle)) * omega_skew @ omega_skew) @ (twist[3:] / angle)
  se3_mat[:3,:3] = matrix_so3_exp(twist[:3])
  se3_mat[:3,3] = p
  return se3_mat
  



# Method to compute the matrix logarithm for SE(3)

def matrix_se3_logarithm(trans_mat : np.ndarray) -> np.ndarray:
  """
  Computes the matrix logarithm of a transformation matrix.

  Args:
    twist: A NumPy array representing the 4x4 transformation matrix.

  Returns:
    A NumPy array representing the 4x4 matrix logarithm.
  """

  se3_log_mat = np.zeros((4,4))
  omega_skew = matrix_so3_logarithm(trans_mat[:3,:3])
  p = trans_mat[:3,3]
  omega = so3_vee(omega_skew)
  angle = np.sqrt(omega[0]**2 + omega[1]**2 + omega[2]**2) 

  if np.isclose(angle, 0):
    se3_log_mat[:3,3] = p
    return se3_log_mat
  
  omega_skew = omega_skew / angle
  inv_mat = np.eye(3)/angle - (0.5 * omega_skew ) + ((1/angle - 1 / (2 * np.tan(angle/2))) * omega_skew @ omega_skew )
  v = inv_mat @ p
 
  se3_log_mat[:3,:3] = omega_skew * angle
  se3_log_mat[:3,3] = v * angle 
  return se3_log_mat


def matrix_se3log_split(se3_log_mat : np.ndarray) -> tuple[np.ndarray, np.float64]:
  """
  Splits the matrix logarithm of a transformation matrix into the normalized twist and scalar angle.

  Args:
    se3_log_mat: A NumPy array representing the 4x4 matrix logarithm.

  Returns:
    A tuple with 1 NumPy array and 1 scalar representing the 4x4 normalized twist / screw and the scalar angle
  """
  omega_skew = se3_log_mat[:3,:3]
  v = se3_log_mat[:3,3]
  omega = so3_vee(omega_skew)
  angle = np.sqrt(omega[0]**2 + omega[1]**2 + omega[2]**2)
  if np.isclose(angle, 0):
    norm = np.sqrt(v[0]**2 + v[1]**2 + v[2]**2)
    return se3_log_mat/ norm, norm
  return se3_log_mat / angle, angle


def matrix_se3_twist2screw(twist : np.ndarray) -> tuple[np.ndarray, np.ndarray, np.float64, np.float64]:
  """
  Splits a 6x1 twist vector of a transformation matrix logarithm to a q,s,h screw axis and a scalar angle.

  Args:
    twist: A NumPy array representing the 6x1 twist vector in se(3).

  Returns:
    A tuple with 2 NumPy arrays and 2 scalar representing the screw axis (q_point , s_axis, h_pitch, theta)
  """
  se3_log_mat, angle  = matrix_se3log_split(se3_hat(twist))
  omega_skew = se3_log_mat[:3,:3]
  v = se3_log_mat[:3,3]
  omega = so3_vee(omega_skew)
  omega_mag = np.sqrt(omega[0]**2 + omega[1]**2 + omega[2]**2)

  if np.isclose(omega_mag, 0):
    # If there is no rotation, only translation
    norm = angle
    q_point = np.array([0,0,0])
    s_axis = v
    h_pitch = np.inf
    return q_point, s_axis, h_pitch, norm
  
  q_point = omega_skew @ v
  s_axis = omega
  h_pitch = np.dot(s_axis, v)
  return q_point, s_axis, h_pitch, angle


# Method to compute the hat operator of a vector in se(3)
def se3_hat(twist : np.ndarray) -> np.ndarray:
  """
  Computes the hat operator of a twist in se(3).

  Args:
    twist: A NumPy array representing the 6x1 twist vector in se(3).

  Returns:
    A NumPy array representing the 4x4 skew-symmetric matrix.
  """
  omega = twist[:3]
  v = twist[3:]
  omega_skew = so3_hat(omega)
  se3mat = np.zeros((4,4))
  se3mat[:3,:3] = omega_skew
  se3mat[:3,3] = v
  return se3mat

# Method to compute the vee operator of a skew-symmetric matrix in se(3)

def se3_vee(twist_hat : np.ndarray) -> np.ndarray:
  """
  Computes the vee operator of a matrix in se(3).

  Args:
    twist_hat: A NumPy array representing the 4x4 matrix.

  Returns:
    A NumPy array representing the 6x1 twist vector in se(3).
  """
  omega_skew = twist_hat[:3,:3]
  omega = so3_vee(omega_skew)
  v = twist_hat[:3,3]
  return np.concatenate((omega, v))
  


# Method to generate an element of the Lie group SE(3)
def element_SE3(w, p, coord_type='exponential') -> np.ndarray:
  """ 
  Generates an element of the Lie group SE(3) given the components of the twist and position.

  Args:
    w: [theta_x, theta_y, theta_z] The components of the twist.
    p: [x, y, z] The components of the position.
    coord_type: The type of coordinates to use. Options are 'exponential' and 'euler'.

  Returns:
    A NumPy array representing the 4x4 element of the Lie group SE(3).
  """
  theta_x,theta_y,theta_z = w
  x,y,z = p
  se3mat = np.eye(4)
  se3mat[:3,:3] = rotation_matrix([theta_x, theta_y, theta_z], coord_type=coord_type)
  se3mat[:3,3] = np.array([x,y,z])
  return se3mat


# Method to generate the inverse of an element of the Lie group SE(3)
def inverse_SE3(se3mat : np.ndarray) -> np.ndarray:
  """
  Computes the inverse of an element of the Lie group SE(3).
  
  Args:
    se3mat: A NumPy array representing the 4x4 element of the Lie group SE(3).

  Returns:
    A NumPy array representing the 4x4 inverse of the element of the Lie group SE(3).
  """
  inv_se3mat = np.eye(4)
  inv_se3mat[:3,:3] = se3mat[:3,:3].T
  inv_se3mat[:3,3] = -se3mat[:3,:3].T @ se3mat[:3,3]
  return inv_se3mat


# Method to generate an adjoint from an element of the Lie group SE(3)

def adjoint_SE3(se3mat : np.ndarray) -> np.ndarray:
  """
  Computes the adjoint of an element of the Lie group SE(3).
  
  Args:
    se3mat: A NumPy array representing the 4x4 element of the Lie group SE(3).

  Returns:
    A NumPy array representing the 6x6 adjoint of the element of the Lie group SE(3).
  """
  adjoint = np.zeros((6,6))
  adjoint[:3,:3] = se3mat[:3,:3]
  adjoint[3:,3:] = se3mat[:3,:3]
  adjoint[3:,:3] = so3_hat(se3mat[:3,3]) @ se3mat[:3,:3]

  return adjoint