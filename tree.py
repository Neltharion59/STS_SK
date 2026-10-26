import math

class Node:
    def __init__(self, name, parent=None):
        self.name = name
        self.parent = parent
        self.children = []
        self.printed = False
        self.visited = False

    def add_child(self, child_node):
        current = self
        while current is not None:    
            if current is child_node:  
                return
            current = current.parent

        self.children.append(child_node)
        child_node.parent = self

    def find_node(self, name):  
        if self.name == name:
            return self
        
        for child in self.children:
            result = child.find_node(name)
            
            if result is not None:
                return result
            
        return None

    def get_depth(self, name, current_depth=1):   
        if self.name == name:
            return current_depth
        
        for child in self.children:
            result = child.get_depth(name, current_depth + 1)
            
            if result is not None:
                return result
            
        return None

    def find_lcs(self, name1, name2):
        node1 = self.find_node(name1)
        node2 = self.find_node(name2)

        if node1 is None or node2 is None:
            return None

        ancestors1 = set()
        current_node = node1
        while current_node is not None:   
            ancestors1.add(current_node)
            current_node = current_node.parent
            
        current_node = node2
        while current_node is not None:   
            if current_node in ancestors1:  
                return current_node 
            current_node = current_node.parent

        return None 

    def wupalmer(self, name1, name2):
        lcs_node = self.find_lcs(name1, name2)

        if lcs_node is None:
            return 0

        depth1 = self.get_depth(name1)
        depth2 = self.get_depth(name2)
        depth_lcs = self.get_depth(lcs_node.name)

        if depth1 == 0 or depth2 == 0: 
            return 0
        
        similarity = (2 * depth_lcs) / (depth1 + depth2)
        return similarity

    def count_nodes(self):
        count = 1
        for child in self.children:
            count += child.count_nodes()
        return count

    def max_depth(self, current_depth=1):
        if not self.children:
            return current_depth
        return max(child.max_depth(current_depth + 1) for child in self.children)

    def to_dict(self):
        return {
            "name": self.name,
            "children": [child.to_dict() for child in self.children]
        }

    def distance(self, name1, name2):
        depth1 = self.get_depth(name1)
        depth2 = self.get_depth(name2)
        lcs_node = self.find_lcs(name1, name2)

        if lcs_node is None:
            return None

        depth_lcs = self.get_depth(lcs_node.name)

        return depth1 + depth2 - 2 * depth_lcs

    def shortest_path(self, name1, name2):
        dist = self.distance(name1, name2)

        if dist is None:
            return 0

        return 1 / (1 + dist)

    def leacock_chodorow(self, name1, name2):
        dist = self.distance(name1, name2)

        if dist is None:
            return 0

        if dist == 0:
            return 1  

        D = self.max_depth()

        return -math.log(dist / (2 * D))
    
    def tree_to_couples(self):
        if not self.printed:
            for child in self.children:
                yield (self.name, child.name)
            self.printed = True
            for child in self.children:
                for (p, ch) in child.tree_to_couples():
                    yield (p, ch)

    def tree_to_text(self):
        couples = [f"{parent} - {child}" for (parent, child) in self.tree_to_couples()]
        couples_string = ('\n').join(couples)
        return couples_string
