from algorithm.parameters import params


class Tree:

    def __init__(self, expr, parent):
        """
        Initialise an instance of the tree class.
        
        :param expr: A non-terminal from the params['BNF_GRAMMAR'].
        :param parent: The parent of the current node. None if node is tree
        root.
        """

        self.parent = parent
        self.codon = None
        self.depth = 1
        self.root = expr
        self.children = []
        self.snippet = None

    def __str__(self):
        """
        Builds a string of the current tree.
        
        :return: A string of the current tree.
        """

        # Initialise the output string.
        result = "("

        # Append the root of the current node to the output string.
        result += str(self.root)

        for child in self.children:
            # Iterate across all children.

            if len(child.children) > 0:
                # Recurse through all children.
                result += " " + str(child)

            else:
                # Child is a terminal, append root to string.
                result += " " + str(child.root)

        result += ")"

        return result

    def __copy__(self):
        """
        Creates a new unique copy of self.
        
        :return: A new unique copy of self.
        """

        # Copy current tree by initialising a new instance of the tree class.
        tree_copy = Tree(self.root, self.parent)

        # Set node parameters.
        tree_copy.codon, tree_copy.depth = self.codon, self.depth

        tree_copy.snippet = self.snippet

        for child in self.children:
            # Recurse through all children.
            new_child = child.__copy__()

            # Set the parent of the copied child as the copied parent.
            new_child.parent = tree_copy

            # Append the copied child to the copied parent.
            tree_copy.children.append(new_child)

        return tree_copy

    def __eq__(self, other, same=True):
        """
        Set the definition for comparison of two instances of the tree
        class by their attributes. Returns True if self == other.

        :param other: Another instance of the tree class with which to compare.
        :return: True if self == other.
        """

        # Get attributes of self and other.
        a_self, a_other = vars(self), vars(other)

        # Don't look at the children as they are class instances themselves.
        taboo = ["parent", "children", "snippet", "id"]
        self_no_kids = {k: v for k, v in a_self.items() if k not in taboo}
        other_no_kids = {k: v for k, v in a_other.items() if k not in taboo}

        # Compare attributes
        if self_no_kids != other_no_kids:
            # Attributes are not the same.
            return False

        else:
            # Attributes are the same
            child_list = [self.children, other.children]

            if len(list(filter(lambda x: x is not None, child_list))) % 2 != 0:
                # One contains children, the other doesn't.
                return False

            elif self.children and len(self.children) != len(other.children):
                # Number of children differs between self and other.
                return False

            elif self.children:
                # Compare children recursively.
                for i, child in enumerate(self.children):
                    same = child.__eq__(other.children[i], same)

        return same

    def get_target_nodes(self, array, target=None):
        """
        Returns the all NT nodes which match the target NT list in a
        given tree.
        
        :param array: The array of all nodes that match the target.
        :param target: The target nodes to match.
        :return: The array of all nodes that match the target.
        """

        if self.root in target:
            # Check if the current node matches the target.

            # Add the current node to the array.
            array.append(self)

        # Find all non-terminal children of the current node.
        NT_kids = [kid for kid in self.children if kid.root in
                   params['BNF_GRAMMAR'].non_terminals]

        for child in NT_kids:
            if NT_kids:
                # Recursively call function on any non-terminal children.
                array = child.get_target_nodes(array, target=target)

        return array

    def get_node_labels(self, labels):
        """
        Recurses through a tree and appends all node roots to a set.
        
        :param labels: The set of roots of all nodes in the tree.
        :return: The set of roots of all nodes in the tree.
        """

        # Add the current root to the set of all labels.
        labels.add(self.root)

        for child in self.children:
            # Recurse on all children.
            labels = child.get_node_labels(labels)

        return labels

    def get_tree_info(self, nt_keys, genome, output, invalid=False,
                      max_depth=0, nodes=0):
        """
        Recurses through a tree and returns all necessary information on a
        tree required to generate an individual.
        
        :param genome: The list of all codons in a subtree.
        :param output: The list of all terminal nodes in a subtree. This is
        joined to become the phenotype.
        :param invalid: A boolean flag for whether a tree is fully expanded.
        True if invalid (unexpanded).
        :param nt_keys: The list of all non-terminals in the grammar.
        :param nodes: the number of nodes in a tree.
        :param max_depth: The maximum depth of any node in the tree.
        :return: genome, output, invalid, max_depth, nodes.
        """

        # Increment number of nodes in tree and set current node id.
        nodes += 1

        if self.parent:
            # If current node has a parent, increment current depth from
            # parent depth.
            self.depth = self.parent.depth + 1

        else:
            # Current node is tree root, set depth to 1.
            self.depth = 1

        if self.depth > max_depth:
            # Set new max tree depth.
            max_depth = self.depth

        if self.codon:
            # If the current node has a codon, append it to the genome.
            genome.append(self.codon)

        # Find all non-terminal children of current node.
        NT_children = [child for child in self.children if child.root in
                       nt_keys]

        if not NT_children:
            # The current node has only terminal children, increment number
            # of tree nodes.
            nodes += 1

            # Terminal children increase the current node depth by one.
            # Check the recorded max_depth.
            if self.depth + 1 > max_depth:
                # Set new max tree depth.
                max_depth = self.depth + 1

        if self.root in nt_keys and not self.children:
            # Current NT has no children. Invalid tree.
            invalid = True

        for child in self.children:
            # Recurse on all children.

            if not child.children:
                # If the current child has no children it is a terminal.
                # Append it to the phenotype output.
                output.append(child.root)

                if child.root in nt_keys:
                    # Current non-terminal node has no children; invalid tree.
                    invalid = True

            else:
                # The current child has children, recurse.
                genome, output, invalid, max_depth, nodes = \
                    child.get_tree_info(nt_keys, genome, output, invalid,
                                        max_depth, nodes)

        return genome, output, invalid, max_depth, nodes

    def print_tree(self):
        """
        Prints out all nodes in the tree, indented according to node depth.
        
        :return: Nothing.
        """

        print(self.depth, "".join([" " for _ in range(self.depth)]), self.root)

        for child in self.children:
            if not child.children:
                print(self.depth + 1,
                      "".join([" " for _ in range(self.depth + 1)]),
                      child.root)
            else:
                child.print_tree()
