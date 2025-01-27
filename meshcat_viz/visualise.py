import numpy as np
import meshcat



class FrameNode:
    
    def __init__(self, frame_id = 'World', orientation : np.ndarray = np.eye(4)):
        self.frame_id = frame_id
        self.orientation = orientation
        self.parent = None
        self.children = []

    def add_child(self, child_id, orientation : np.ndarray = np.eye(4)):

        def node_id_check(node,id):
            try:
                for child in node.children:
                    if (child.frame_id == id):
                        raise ValueError('Frame with the same name already exists')
                return id
            except Exception as e:
                print(f'{e} : {id}')
                if (id.split('_')[-1].isdigit()):
                    offset = id.rfind('_')
                    id = id[:offset+1] + str(int(id.split('_')[-1]) + 1)
                else:
                    id += '_0'
                return node_id_check(node, id)

        child_id = node_id_check(self, child_id)
        temp_node = FrameNode(child_id, orientation)
        temp_node.parent = self
        self.children.append(temp_node)

    def add_object(self, object):
        self.object = object
        # Add meshcat object here

    def get_parent(self):
        return self.parent
        
    def print_tree(self):
        
        def print_recursively(node : FrameNode, num = 0):
            print(f'{node}\t Current Level : {num}')
            for child in node.children:
                print_recursively(child, num + 1)
        
        print_recursively(self)

    def __str__(self):

        def print_id(node):
            if (node.parent == None):
                return node.frame_id
            else:
                return f'{print_id(node.parent)}/{node.frame_id}'
            
        return print_id(self)
    

class WorldScene:
    def __init__(self, vis : meshcat.Visualizer):
        self.vis = vis
        self.FrameTree = FrameNode()
        self.vis.open()

    def add_frame(self, frame_node: FrameNode):
        return self.FrameTree.add_child(frame_node)
    
    def animation(self):
        # Build frame by frame animation
        # Frame by Frame animation of entire tree, sparse input with checkpoints
        pass