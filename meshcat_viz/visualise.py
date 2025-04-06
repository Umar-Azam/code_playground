import numpy as np
import meshcat
import lie_group as lg
from draw import *



class FrameNode:
    
    def __init__(self, frame_id = 'World', orientation : np.ndarray = np.eye(4)):
        self.frame_id = frame_id
        self.orientation = orientation
        self.parent = None
        self.children = []
        self.objects = []

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
        child_node = FrameNode(child_id, orientation)
        child_node.parent = self
        self.children.append(child_node)
        return child_node

    def get_transform(self):

        def tree_transform(node):
            if node.parent == None:
                return node.orientation
            else :
                return tree_transform(node.parent) @ node.orientation

        return tree_transform(self)


    def add_object(self, object_id):
        ## TODO : Add vectors / object to the frame
        self.objects.append(object_id)

    def get_parent(self):
        return self.parent
        
    def print_tree(self):
        
        def print_recursively(node : FrameNode, num = 0):
            print(f'{node}\t Current Level : {num}')
            for child in node.children:
                print_recursively(child, num + 1)
        
        print_recursively(self)

    def get_tree(self):

        def tree_recursively(node):

            if len(node.children) == 0:
                return {}
            else:
                return {child.frame_id : tree_recursively(child) for child in node.children}
        
        return {self.frame_id : tree_recursively(self)}

    def __str__(self):
        # Print the full path to the frame
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
        self.FrameReference = {str(self.FrameTree) : self.FrameTree}
        self.FrameTreeAnimation = []
        self.vis.open()
        frame_generator(self.vis, str(self.FrameTree), self.FrameTree.orientation)


    def get_node(self, node_id):

        if node_id not in self.FrameReference:
            raise ValueError('Frame does not exist')
        
        return self.FrameReference[node_id]
    
    def update_tree(self):
        pass


    def add_frame(self, frame_id, parent_id = 'World', orientation = np.eye(4)):
        # Add a new frame to the tree. 
        # Caution : If partial parent name is provided, a matching frame_id will be searched across the tree via DFS
        # Caution : If partial parent name is provided, a collision may occur with the another frame_id in the tree
        # Fallback to the root frame if the parent frame does not exist

        try:
            parent_id = self.__find_full_node_id__(parent_id)
        except ValueError as e:
            print(f'{e} : {parent_id}\nAdding new frame to the root frame :{self.FrameTree}')
            parent_id = str(self.FrameTree)
        parent_node = self.FrameReference[parent_id]
        frame_node = parent_node.add_child(frame_id, orientation)
        self.FrameReference[str(frame_node)] = frame_node
        frame_generator(self.vis, str(frame_node), frame_node.get_transform())
        return frame_node

    def __find_full_node_id__(self, node_id):
        if node_id not in self.FrameReference:
            tree = self.FrameTree.get_tree()

            def tree_search(tree_dict):
                if node_id in tree_dict.keys():
                    return node_id
                else:
                    for key, value in tree_dict.items():
                        if len(value) > 0:
                            sub_full_node_id = tree_search(value)
                            if sub_full_node_id is not None:
                                return f"{key}/{sub_full_node_id}"


            full_node_id = tree_search(tree)

            if full_node_id is None:
                raise ValueError('Frame does not exist')
            else:
                return full_node_id

        return node_id



    def animation(self):
        # Build frame by frame animation
        # Frame by Frame animation of entire tree, sparse input with checkpoints
        pass