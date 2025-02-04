class node:
    def __init__(self, name = '0'):
        self.name = name
        self.neighbours = set()
        print(f'Node {self.name} created')

    def add_neighbour(self, neighbour):
        self.neighbours.add(neighbour)
        pass

class graph:

    def __init__(self):
        self.nodes = dict()
        self.node_ids = set()
        

    def add_node(self, node_id = '0'):

        def validate_node_name(this_graph, node_id):
            if node_id not in this_graph.node_ids:
                return node_id
            else :
                if ( ('_' in node_id) and node_id.split('_')[-1].isdigit() ):
                    offset = node_id.rfind('_')
                    new_node_id = node_id[:offset+1]+str(int(node_id.split('_')[-1])+1)
                    return validate_node_name(this_graph,new_node_id)
                return node_id+'_1'

        validated_id = validate_node_name(self, node_id)
        self.node_ids.add(validated_id)
        self.nodes[validated_id] = node(validated_id)

    
    def get_node(self, node_id):
        return self.nodes[node_id]  
    
    def get_node_neighbours(self, node_id):
        if node_id not in self.node_ids:
            print('Node does not exist')
            return None
        return self.nodes[node_id].neighbours


    def add_edge(self, node_id1, node_id2):
        if node_id1 not in self.node_ids or node_id2 not in self.node_ids:
            print('Node does not exist')
            return None
        self.nodes[node_id1].add_neighbour(node_id2)
        self.nodes[node_id2].add_neighbour(node_id1)
        pass

    def get_path(self, node_id1, node_id2):

        if node_id1 not in self.node_ids or node_id2 not in self.node_ids:
            print('Node does not exist')
            return None
        
        def path_finder(this_graph, node_id1, node_id2, path = []):
            if node_id1 == node_id2:
                return path + [node_id1]
            path.append(node_id1)

            for neighbour in this_graph.get_node_neighbours(node_id1):
                if neighbour not in path:

                    # Trace path generation
                    # print(f'path : {path}\nneighbour : {neighbour}')

                    check_path = path_finder(this_graph, neighbour, node_id2, path.copy())
                    if check_path != None:
                        return check_path
                
        path = path_finder(self, node_id1, node_id2)
        if path is None:
            print('No path exists')
            return None
        return path
        


            

 # Validate / benchmark performance degradation with size increase

print(__name__)

if __name__ == '__main__':
    g = node()
