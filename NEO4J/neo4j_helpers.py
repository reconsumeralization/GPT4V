# %% Cells delimiter for Pycharm

# from neo4j import GraphDatabase  # official driver from Neo4j
# see pros and cons here https://py2neo.org/2020.1/
# Py2neo offers a larger surface, with both a higher level API and an OGM, but the official driver is fully supported
# by Neo4j. If you are new to Neo4j, need an OGM, do not want to learn Cypher immediately, or require data science
# integrations, py2neo may be the better choice. If you are in an Enterprise environment where you require support,
# you likely need the official driver.
from py2neo import Graph, Node, Relationship, NodeMatcher, RelationshipMatcher
from py2neo.errors import ConnectionUnavailable as Neo4jConnectionUnavailable
# I had to pip install monotonic since it was missing after installing py2neo
from dataclasses import dataclass, field, is_dataclass
from .nodedataclasses import NewUser, Question, Answer, LinguisticImage, Theme, Utters, HasTheme, HasImagery, Transcripts
from datetime import datetime as dt
from itertools import combinations
#from utilspie.collectionsutils import frozendict
# from typing import AnyStr, List, Dict, Tuple, Any

@dataclass()
class bcolors:
    '''
    Codes to change color or move cursor
    example
    print(bcolors.WARNING + "Warning: Budget limit reached. Continue?" + bcolors.END)
    '''
    HEADER = '\033[95m'  # purple
    OKBLUE = '\033[94m'  # blue
    OKGREEN = '\033[92m'  # green
    WARNING = '\033[93m'  # orange
    FAIL = '\033[91m'  # red
    END = '\033[0m'  # must use it to stop coloring
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    CURSOR_UP = "\033[1A"  # to go up one line
    CLEAR = "\x1b[2K"  # print((CURSOR_UP + CLEAR)*2, end="")  clears last two lines

class Conflict(Exception):
    pass

class MissingValue(Exception):
    pass

# %%
class Neo4jGraph:
    """
    Graph class using py2neo methods, rather than CQL
    """

    def __init__(self, url="bolt://localhost:7687", id="neo4j", pw='', showstatus=False):
        """
        Initializes the Graph
        :param url:
        :param id:
        :param pw:
        """
        try:
            self.graph = Graph(url, auth=(id, pw))
            if showstatus:
                print('Graph Connected')
        except Neo4jConnectionUnavailable:
            raise Neo4jConnectionUnavailable('Connection failed')

        self.nodematcher = NodeMatcher(self.graph)
        self.relmatcher  = RelationshipMatcher(self.graph)
        
    def mergeNode(self, nodedataclass, DEBUG=False):
        """
        Creates a node in graph using a predefined dataclass if it doesn't exist
        PS: when we create a node, it can only be with a dataclass object
            but we have to test if a 'similar' node already exists, using
            the constraints defined in the dataclass

        :param nodedataclass: a dataclasses defined in this file
        :param DEBUG: if None, no error or exception message when an existing node is detected
                        (to be used in pytests, to avoid stray messages)
        :return: the new node object or the node with the same constraints if it already exists
        """
        if not is_dataclass(nodedataclass):
            raise TypeError("Attempt to create a node with other type than dataclass")

        else:
            # let's convert to tuple in case user specified a single string
            # also ('ab') is not a tuple, user should write ('ab',)
            labels, properties = self._toTuple(nodedataclass.labels), nodedataclass.properties
            labels_constraints = self._toTuple(nodedataclass.labels_constraints)
            properties_constr = self._toTuple(nodedataclass.properties_constraints)

            if set(labels_constraints) > set(labels):
                raise KeyError("Constraints specified on non existing labels")

            if set(properties_constr) > set(properties):
                raise KeyError("Constraints specified on non existing properties")

            # let's create the property dictionaries using actual values of such properties
            # we could have done this in each dataclass, but it would have been heavier
            # and maybe the user changed the properties values after that
            properties_constraints = {k: properties[k] for k in properties_constr}

            # let's test if node is unique, according to constraints
            # do not use graph.exists because it tests the identity which is useless here
            # since we haven't even created the node inside the graph yet...
            if len(labels_constraints) + len(properties_constraints):
                match = self._nodeMatch(*labels_constraints, **properties_constraints)
            else:
                # if we don't specify any constraints, then we use
                # all the labels and properties to find a duplicate
                # TODO remove/modify this when we decide how to implement constraints
                match = self._nodeMatch(*labels, **properties)

            if match is None:
                # we cannot user graph.merge here because it assumes ONE label only
                self.graph.create(Node(*labels, **properties))
                # graph.create does not return anything, so we have to use _NodeMatch again
                node = self._nodeMatch(*labels, **properties)

                if DEBUG is True:
                    print(f'New node {labels} created with ID =', node.identity)
                return node  # useful to create a relation
            else:
                error_msg = bcolors.FAIL + bcolors.BOLD + \
                            f"Node {labels} already exists with ID = {match.identity}" + bcolors.END
                if DEBUG is None:
                    pass
                elif DEBUG is True:
                    print(error_msg)
                else:
                    raise Conflict(error_msg)
                return match  # useful to create a relation

    @staticmethod
    def _toTuple(labels):
        '''
        Creates a tuple from labels.
        Converts integer labels to string.

        We can't do simply tuple(labels) because tuple('abc') is ('a','b','c')
        I created this function to help if a user defines a label as 'abc', or ('abc')
        when it should be ('abc',), but it's easy to forget the comma
        :param labels: either a string (if user forgot to input a tuple) or a tuple of strings
        :return: a tuple of labels
        '''
        if isinstance(labels, (tuple, set)):  # sets are ok too
            if len(labels) == 0 or isinstance(labels[0], (str, int)):
                return tuple(str(l) for l in labels)
            else:
                raise TypeError(f"Labels can only be string or integer. \n"
                                f"Here, we have labels of type {type(labels[0])}")
        elif isinstance(labels, (str, int)):
            return (str(labels),)
        else:
            raise TypeError("Labels can only be string or integer")

    def _getNode(self, nodeID):
        '''
        Checks if node with NodeID exists, then returns it
        :param nodeID: the node ID
        :return: node object if there is a node with nodeID, otherwise None
        '''
        if isinstance(nodeID, int):
            return self.nodematcher.get(nodeID)
        else:
            return None

    def _getNodeID(self, *labels, **properties):
        # TODO: do we want to return ALL matching nodes and let user pick the one he wants?
        '''
        Returns the node ID of a node, defined by its labels and properties
        :param labels: labels by which we want to identify the node
        :param properties: prop  "  "  "
        :return: Node's ID (int) if it exists, else None
        '''

        node = self._nodeMatch(*labels, **properties)
        return None if node is None else node.identity

    def _nodeMatch(self, *labels, first_only=True, all=False, **properties):
        '''
        Returns an existing node object matching labels and properties
        I modified the match function to deal with either missing labels
        or missing properties because it then picks a node with any label
        or any property.
        For instance, self.mather.match() picks any node.
        It's logical, but here we want to return nothing.

        :param labels: list of labels that an existing node must match
        :param properties: dictionary of properties that  " " " "
        :param first_only: returns only first occurrence
        :param all: if no labels or properties, returns all nodes
        :return: node object matching labels and properties, or None
        '''
        # do not use graph.exists since it tests the identity
        # which doesn't exist yet here since we want to find out
        # if we can create a new node with those labels and properties

        if (len(labels)+len(properties)) == 0:
            if all == False:
                return None
            else:
                return self.nodematcher.match().all()
        else:
            nodes = self.nodematcher.match(*labels, **properties)
            return nodes.first() if first_only else nodes

    def relationsCount(self, startnode,
                       *relation_labels,
                       endnode=None,
                       **relation_properties):

        '''
        Counts all relations between a startnode and endnode
        If endnode is None, we search for all possible ones.

        :param startnode: start node object
        :param relation_labels: labels of desired relationship
        :param endnode: any node with a counter for those labels if None, else node object
        :param relation_properties: properties of the relationship
        :return: total sum of all created relationships starting from startnode

        example:
        g.relationsCount( user, 'HAS IMAGE')
        with multiple relationship labels:
        g.relationsCount( user, 'HAS IMAGE', 'OTHER LABEL')

        '''

        # py2neo doesn't allow multiple labels for relationships -> concatenation
        relation = self.joinLabels(relation_labels)
        counter_name = relation + "__counter"

        matches  = self.relmatcher.match((startnode, endnode),
                                          r_type=relation,
                                          **relation_properties).all()

        count = 0
        # we could have the same relation going to several nodes, so if we
        # didn't specify the endnode, we need to add them all
        for rel in matches:
            startnode, endnode = rel.start_node, rel.end_node
            rellabel, relproperties = rel.__class__.__name__, dict(rel)

            _, endnode_properties = self.readNode(endnode)

            if counter_name in endnode_properties:
                count += endnode[counter_name]
            else:
                # there should always be a counter since it's created when the
                # relationship was created/added
                raise Conflict(f"Missing counter for relationship {relation_labels} in node {endnode}")

        return count

    def getPairs(self, startnode=None, relation=None, endnode=None, **properties):
        """
        Finds all pairs starting at startnode, with a relationship 'relation' (or any)
        to endnode (if specified) or any valid endnode
        :param startnode: starting node or None for any node
        :param endnode: endnode node or None for any node
        :param relation: relationship label or None for any relationship
        :param properties: properties of the relationship to match
        :return: list of tuples (startnode, relationship, endnode)
        """

        # TODO we could add a bidirectional search (pass the nodes as a Set)

        matches = self.relmatcher.match((startnode, endnode),
                                        r_type=relation,
                                        **properties).all()

        return [(m.start_node, type(m).__name__, m.end_node,
                 dict(m.end_node).get(type(m).__name__+'__counter',0) ) for m in matches]


    def _processNode(self, source, nodeclass='Source'):
        '''
        Checks if source exists, otherwise creates it
        :param source: a nodeID (int), a dataclass or a node object
        :param nodeclass: a string to be included in the error message (e.g. 'Target')
        :return: a node object for the existing or newly created node
        '''
        if isinstance(source, int):
            # a node ID was given, we return the existing node if it exists
            return self._getNode(source)

        elif is_dataclass(source):
            labels, properties = source.labels, source.properties
            return self.mergeNode(*labels, **properties)

        elif not isinstance(source, Node):
            raise TypeError(f'Node class was expected for {nodeclass} node')

        else:
            # we were given a node object, we return it
            return source

    def joinLabels(self, labels, separator='|'):
        '''
        Py2neo supports only one label for relationships, so
        if we want several, we can concatenate them
        :param labels: a list/tuple of labels, or just a label in str/int
        :return: a string with concatenated labels with separator
        '''
        # we use _toTuple in case user doesn't put label in a tuple,
        # e.g. 'HAS IMAGE' instead of ('HAS IMAGE',)
        return separator.join([str(l) for l in self._toTuple(labels)])

    def createRelation(self, source, target,
                       reldataclass,
                       allow_duplicates=True,
                       counting=True,
                       DEBUG=False):
        '''
        Adds a relation between two existing nodes, creates the nodes if they don't exist
        It will also increment an internal counter in the target (to count the
        number of times a specific relation links to it)

        REMINDER: Neo4J allows properties inside relationships but they are not taken into account
                  during a match

        :param source: id of source node if int, a node dataclass (to be created), otherwise a node object
        :param target: id of target node if int, a node dataclass (to be created), otherwise a node object
        :param reldataclass: relationship dataclass (or a tuple of str/int, for tests)
        :param allow_duplicates: if False, an error message appears if the relationship already exists
                                 if True, the relationship is created even if one already exists
        WARNING:
        There are no constraints on relationships at the moment, so, if allow_duplicates is True,
        Neo4J will replace an existing relationship, EVEN IF the properties are different!

        :param counting: if False, the counter is set to 1 at creation, and never incremented
                         if True, the counter is incremented, even if the relationship already exists
        :param DEBUG: if None, no error or exception message when an existing relation is detected
                        (to be used in pytests, to avoid stray messages)
        :return: the created or existing relation
        '''
        source = self._processNode(source)
        target = self._processNode(target, nodeclass='Target')

        if source is None and target is None:
            raise MissingValue (bcolors.FAIL + bcolors.BOLD +
                               "Neither source nor target exists for this relationship" +bcolors.END)
        if source is None:
            raise MissingValue (bcolors.FAIL + bcolors.BOLD +
                                "Source for this relationship doesn't exist" + bcolors.END)
        if target is None:
            raise MissingValue(bcolors.FAIL + bcolors.BOLD +
                               "Target for this relationship doesn't exist" + bcolors.END)

        if is_dataclass(reldataclass):
            # normal case, we must extract the relationship labels and properties
            # py2neo supports only one relation label, so if there are several
            # I concatenate them
            relation = self.joinLabels(reldataclass.labels) # in case 'abc' instead of ('abc',)

            try:
                # let's make sure the dataclass has properties (not a given for relations)
                properties = reldataclass.properties
            except AttributeError:
                properties = {}

        elif isinstance(reldataclass, (str, int)):
            # for tests only
            relation = self.joinLabels(reldataclass)
            properties = {}

        else:
            raise TypeError("The relationship is neither a relationship dataclass nor a str/int")

        relation_matches = self.relmatcher.match((source,target), r_type=relation, **properties)

        if not allow_duplicates and len(relation_matches):
            # there is already an identical relation between source and target
            # we don't count this attempt, just leave
            error_msg = f"Relationship '{relation}' already exists between nodes " \
                        f"{source.identity} and node {target.identity}"
            if DEBUG is None:
                pass
            elif DEBUG is True:
                print(bcolors.FAIL + bcolors.BOLD + error_msg + bcolors.END)
            else:
                raise Conflict(error_msg)

            return relation_matches.first()

        else:

            if counting:
                # user wants to count, so we add a counter the first time, and initialize it
                counter_name = relation + "__counter"
                _, target_properties = self.readNode(target)
                # we create a key in the dictionary with the labels of the wanted relation, and set it to 0
                target_properties.setdefault(counter_name, 0)

                # let's increase the counter in the target node for this relation
                count = target_properties[counter_name] + 1
                self.editProperty(target, **{counter_name: count})

            # TODO add constraints on relationships too ??
            self.graph.create(Relationship(source, relation, target, **properties))

            if DEBUG:
                print(f"Relationship '{relation}' created between nodes {source.identity} "
                      f"and node {target.identity}")
            # graph.create doesn't return the created object unfortunately, so we have to search for it
            return self.relmatcher.match((source,target), r_type=relation, **properties).first()

    def deleteAllNodes(self, DEBUG=False):
        ''' Deletes all nodes and relations '''
        self.graph.delete_all()

        if DEBUG:
            print("All nodes have been deleted!")

    def getNodes(self, *labels, **properties):
        """ Returns all nodes objects matching labels and properties values
            We have to set all to True to return all nodes if no labels
            or properties are specified.
        """

        return list(self._nodeMatch(*self._toTuple(labels),
                                    first_only=False,
                                    all=True,
                                    **properties))


    @property
    def nodesNb(self):
        ''' Returns the number of nodes in the graph '''
        return len(self.nodematcher.match())

    def showNode(self, node):
        '''
        Displays node labels and properties - mainly used for tests
        :param node: either a node Id or a node object
        :return: (labels) and {properties}
        '''
        if isinstance(node, int):
            # we have a NodeID
            nodeID = node
            node = self._getNode(node)
            # TODO does _toTuple return proper format?
            labels, properties = self._toTuple((*node.labels,)), dict(node.items())
        else:
            # node.labels are not tuples, but py2neo.cypher.encoding.LabelSetView
            labels, properties = self._toTuple((*node.labels,)), dict(node.items())
            nodeID = self._getNodeID(*labels, **properties)

        print(f"Node {nodeID} has labels: {node.labels}")
        print(f"Node {nodeID} has properties:")

        for k, v in node.items():
            print(f"\t\t\t {k}:{v}")

        return labels, properties

    def editProperty(self, node, append=False, DEBUG=False, **properties):
        # TODO technically, we should check if modification doesn't
        #       create a node identical to an existing one
        '''
        Update property with new value

        Neo4J properties cannot be a collection inside a collection, or a dictionary.

        Allowed properties types here: tuple, list, str or int

        With append = True,
        New value list or tuple will be added to existing one.
        A new value str or int will be added to a tuple or list property.
        If property is str, the new value will be concatenated to it.
        If property is int, existing and new values will be put in a tuple.

        :param node: node object
        :param append: to append new values (e.g. for transcripts) if true
                        otherwise property is replaced with new value
        :param property: dictionary with new values
        :return: nothing, node modified in place
        '''

        if node is None:
            raise TypeError("Node 'None' cannot be updated!")

        _, nodeproperties = self.readNode(node)
        if append:

            for k, v in properties.items():

                if k not in nodeproperties:
                    # if property k doesn't exist, we create it and initialize with v
                    if DEBUG:
                        print(f"Property {k} doestn't exist, so we create and initialize it.")

                    node[k] = v
                    continue
                # we allow to update a list or tuple with a str or int
                if isinstance(node[k], list)and isinstance(v, (str,int)):
                    v = [v]
                elif isinstance(node[k], tuple) and isinstance(v, (str,int)):
                    v = (v,)
                elif isinstance(node[k], int) and isinstance(v, int):
                    node[k] = tuple(node[k])
                    v = (v,)
                elif not (type(node[k]) == type(v)):
                    raise TypeError("Type mismatch between current property and new value!")

                node[k] += v

        else:
            for k, v in properties.items():
                if k not in nodeproperties and DEBUG:
                    # if property k doesn't exist, we create it and initialize with v
                    print(f"Property {k} doestn't exist, so we create and initialize it.")

                node[k] = v

        # let's push the modifications to the DB
        self.graph.push(node)


    def setGlobalConstraint(self, *constraints, ADD=True):
        '''
        Add or removes a global constraint
        :param constraints: a label and a property key, default is 'User' and 'display_name'
        :param ADD: sets a constraint if True, otherwise removes it
        :return: nothing, constraint added/removed in place
        '''
        # TODO add constraints removal
        if len(constraints) == 0:
            label, property_key = ('User', 'display_name')
        else:
            label, property_key = constraints

        if ADD:
            # TODO test if this constraint already exists
            self.graph.schema.create_uniqueness_constraint(label, property_key)
            self.graph.run(f'CREATE CONSTRAINT pass_required FOR (u:{constraints[0]}) '
                           f'REQUIRE u.password_hash IS NOT NULL')
        else:
            self.graph.schema.drop_uniqueness_constraint(label, property_key)
        # https://neo4j.com/docs/cypher-manual/current/constraints/
        # property existence constraints are for pro edition

    def readNode(self, node):
        '''
        Returns the labels and properties of a given node
        :param node: node object
        :return: labels and dictionary of node properties
        '''

        return list(node.labels), dict(node)


def Now(format="%m/%d/%Y, %H:%M:%S", as_string=True):
    '''
    Gives the time in specified format as string for inclusion in properties
    JSON does not accept datetime objects

    :param format: the format to use for the time
    :return: a string with the current time
    '''
    if as_string:
        return dt.now().strftime(format)
    else:
        return dt.now()


def createNode(g, *labels, DEBUG=False,
               labels_constraints=tuple(),
               properties_constraints=tuple(),
               **properties):
    '''
    High-level function adding a User node into a graph

    Constraints on labels and properties can be set to prevent duplicates
    E.g.
    createNode(g, ('User', 'SessionId'),
                user_id = 'JP007',  # **{'userid':'JP007'} if one prefers dictionaries
                properties_constraints=('user_id,),
                DEBUG=True)
        will create a new node with labels 'User' and 'SessionId',
        property user_id 'JP007' unless a node with such user_id already exists,
        in which case, if DEBUG is True, it will return None and display a msg
        such as "Node ('User', SessionID') already exists with ID = 309"

    WARNING: with no constraints, the code will use ALL the labels and
        properties to test for unicity.  This may be a problem with some
        properties such as 'transcript' holding all the conversations
        because, for sure, any node with everything else identical (user id ...)
        will still differ if the transcripts is taken into account, and
        a new node will be created.

        It is possible to avoid using constraints by creating a node first
        with the labels and properties that must be unique, and then
        update / add properties.

        See https://neo4j.com/docs/cypher-manual/current/constraints/ to understand
        how constraints work.  Only the business edition has property existence
        constraints.

    :param g: a Neo4jGraph object
    :param labels: 'User', 'Imagery', 'Theme' or anything else
    :param labels_constraints: tuple of labels to be tested for unicity
    :param properties_constraints: tuple of properties to be tested for unicity

            WARNING: for the uniqueness to trigger, it is not enough to have an
            identical property name.  It also needs to have the same value!
            Otherwise, a new node will be created, with that property and a new value.

    :param properties: dictionary with node properties
    :param DEBUG: if None, no error or exception message when an existing node is detected
                    (to be used in pytests, to avoid stray messages)

    :return: the new node object or the node with the same constraints if it already exists
    '''

    @dataclass
    class GeneralNode():
        labels: str = tuple()
        properties: dict = field(default_factory={})
        labels_constraints:tuple = tuple()         # constraints per node e.g. ('User',)
        properties_constraints:tuple = tuple()     # ('user_id', 'display_name')

    return g.mergeNode(GeneralNode(labels=labels,
                                   labels_constraints=labels_constraints,
                                   properties_constraints=properties_constraints,
                                   properties=properties),
                                   DEBUG= DEBUG  )


def createRelation(g, source, target,
                   *relation_type,
                   DEBUG=False,
                   allow_duplicates=True,
                   counting=True,
                   **properties):
    '''
    High-level function adding a Relation Utterance between two nodes

    :param g: a Neo4jGraph object
    :param source: source node object
    :param target: target node object
    :param relation_type: relation labels between nodes ( tuple of str, or str)
    :param allow_duplicates: if False, an error message appears if the relationship already exists
                             if True, the relationship is created even if one already exists
    WARNING:
    There are no constraints on relationships at the moment, so, if allow_duplicates is True,
    Neo4J will replace an existing relationship, EVEN IF the properties are different!

    :param counting: if False, the counter is set to 1 at creation, and never incremented
                     if True, the counter is incremented, even if the relationship already exists
    :param DEBUG: if None, no error or exception message when an existing relation is detected
                    (to be used in pytests, to avoid stray messages)
    :return: the relationship object created in place
    '''
    @dataclass
    class Relation():
        labels:str
        properties: dict
        labels_constraints = tuple()
        properties_constraints = tuple()

    # TODO add constraints on relationships too?
    return g.createRelation(source, target,
                            Relation(labels=relation_type,
                                     properties=properties),
                            allow_duplicates = allow_duplicates,
                            counting = counting,
                            DEBUG= DEBUG)


