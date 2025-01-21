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
                print(f'{e}\nFrame with the same name already exists : {id}')
                if (id[-1].isdigit()):
                    id = id[:-1] + str(int(id[-1]) + 1)
                else:
                    id += '_0'
                return node_id_check(node, id)

        child_id = node_id_check(self, child_id)
        temp_node = FrameNode(child_id, orientation)
        temp_node.parent = self
        self.children.append(temp_node)

    def get_parent(self):
        if (self.parent == None):
            return None
        else:
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

    def add_frame(self, frame_node: FrameNode):
        self.frames[frame_node.frame_id] = frame_node
        self.update_visualization(frame_node)

    def update_visualization(self, frame_node: FrameNode):
        if frame_node.parent is None:
            self.vis[frame_node.frame_id].set_transform(frame_node.orientation)
        else:
            parent_transform = self.vis[frame_node.parent.frame_id].get_transform()
            self.vis[frame_node.frame_id].set_transform(parent_transform @ frame_node.orientation)

        for child in frame_node.children:
            self.update_visualization(child)

    def display(self):
        self.vis.open()