from database import driver

class Graph:
    ''''''

    def _add_tx(tx, name, age):
        '''Execute a transaction to create a Person node if it doesn't exist
        
        If the person doesn't exist, create the node and add an age property to
        it.'''
        # It uses MERGE instead of CREATE because with MERGE you only create a
        # node if it doesn't exist, allowing uniqueness (not enforced by the 
        # database). It pretty much like a MATCH-or-CREATE statement.
        # See https://neo4j.com/docs/cypher-manual/current/clauses/merge/
        result = tx.run("""
            MERGE (p:Person {name: $name})
            ON CREATE
                SET p.age = $age
            """,
            name=name,
            age=age
        )
        # Forces the database to flush it's results to the client, results are
        # consumed lazily otherwise
        summary = result.consume()

        # Get the number of nodes created from the counters of the operations'
        # summary
        return summary.counters.nodes_created

    def _remove_tx(tx, name):
        '''Execute a transaction to delete a Person node'''              
        # It uses DETACH DELETE instead of plain DELETE because we're deleting
        # every relationship coming or going from the target node. It will, update
        # the relationship data of each linked node.
        # See https://neo4j.com/docs/cypher-manual/current/clauses/delete/#delete-delete-a-node-with-all-its-relationships
        result = tx.run(
            "MATCH (p:Person {name: $name}) DETACH DELETE p",
            name=name
        )
        # Forces the database to flush it's results to the client, results are
        # consumed lazily otherwise
        summary = result.consume()

        # Get the number of nodes deleted from the counters of the operations'
        # summary
        return summary.counters.nodes_deleted

    def _list_tx(tx, name, depth, full):
        '''Execute a transaction to retrieve a Person friends
        
        It returns their friends and their friends' friends up to a certain
        depth. It also allows to retrieve only those friends found at that
        depth or every friend up to it.'''
        # To retrieve only direct relationships you specify the type within
        # the MATCH clause with the syntaxis: -[:REL_TYPE]- or -[]- or even --

        # The MATCH clause allows specifying the minimum and maximum number of 
        # hops to traverse. The syntaxis is: -[:REL_TYPE*min..max]-. This also
        # works with a without a type: -[*min..max]-. You can also specify only 
        # one like: -[*min..]- or -[*max]-

        # All paths get traversed if they match the MATCH pattern, that's why we
        # need to return DISTINCT to guarantee we're not returning the same friend
        # more than once. This would happen if retrieving friends of friends, and
        # two direct friend have a mutual friend.

        # For the same reason, the initial anchor node (the one we're matching
        # against) needs to be excluded in the WHERE clause. The traversal may end
        # up visiting the anchor node again, and we don't want to count that
        # person as being a friend with themselves.
        # See https://neo4j.com/docs/cypher-manual/current/clauses/match/#varlength-rels
        # See https://neo4j.com/docs/cypher-manual/current/clauses/where/
        # See https://neo4j.com/docs/cypher-manual/current/clauses/return/#return-unique-results
        result = tx.run(
            f"MATCH (f:Person)-[:FRIENDS_OF*{1 if full else depth}..{depth}]"
            """-(p:Person {name: $name})
            WHERE f <> p
            RETURN DISTINCT f""",
            name=name
        )

        # Iterating the result consumes the data from the database, otherwise
        # the data would be incomplete or missing
        return [record['f'] for record in result]

    def _befriend_tx(tx, name, friend):
        '''Execute a transaction to create a FRIENDS_OF relationship between two
        Person nodes.'''
        # It uses MERGE instead of CREATE to guarantee there will be only one
        # FRIENDS_OF relationship between the two of them. It also sets a property
        # on the relationship if it was created instead of matched. See 
        # See https://neo4j.com/docs/cypher-manual/current/clauses/merge/

        result = tx.run(
            '''
            MATCH (p:Person {name: $name}), (f:Person {name: $friend})
            MERGE (p)-[r:FRIENDS_OF]->(f)
            ON CREATE
                SET r.since = timestamp()
            ''', 
            name=name, friend=friend
        )
        # Forces the database to flush it's results to the client, results are
        # consumed lazily otherwise
        summary = result.consume()

        # Get the number of relationships created from the counters of the
        # operations' summary
        return summary.counters.relationships_created


    def _edit_tx(tx, name, age):
        '''Execute a transaction to set the age property on a Person node'''

        # See https://neo4j.com/docs/cypher-manual/current/clauses/set/
        result = tx.run(
            'MATCH (p:Person {name: $name}) SET p.age = $age', 
            name=name, age=age
        )

        # Forces the database to flush it's results to the client, results are
        # consumed lazily otherwise
        summary = result.consume()

        # Get the number of properties set from the counters of the operations'
        # summary
        return summary.counters.properties_set

    def _info_tx(tx):
        ''''''
        # This statement uses the count store to get node count and relationship
        # count. The UNION clause is used because in order to use the store
        # (which is database metadata and does not hit any nodes nor 
        # relationships to get it's value) there are some constraints that the
        # query must meet. One is that there should be only one value returned
        # (the count) and there should not be any other clauses besided the 
        # MATCH.
        # See https://neo4j.com/docs/cypher-manual/4.3/execution-plans/operators/#query-plan-node-count-from-count-store
        # See https://neo4j.com/docs/cypher-manual/4.3/execution-plans/operators/#query-plan-relationship-count-from-count-store
        result = tx.run('''
            MATCH ()-[r]->() RETURN COUNT(r) AS count
            UNION ALL
            MATCH () RETURN COUNT(*) AS count
        '''
        )
        return dict(zip(('r', 'n'), [record['count'] for record in result]))

    @classmethod
    def add(cls, name, age):
        ''''''
        with driver.session() as session:
            return session.write_transaction(cls._add_tx, name, age)

    @classmethod
    def remove(cls, name):
        ''''''
        with driver.session() as session:
            return session.write_transaction(cls._remove_tx, name)        

    @classmethod
    def list_friends(cls, name, depth, full):
        ''''''
        with driver.session() as session:
            return session.read_transaction(cls._list_tx, name, depth, full)


    @classmethod
    def befriend(cls, name, friend):
        ''''''
        with driver.session() as session:
            return session.write_transaction(cls._befriend_tx, name, friend)

    @classmethod
    def edit(cls, name, age):
        ''''''
        with driver.session() as session:
            return session.write_transaction(cls._edit_tx, name, age)

    @classmethod
    def info(cls):
        ''''''
        with driver.session() as session:
            return session.read_transaction(cls._info_tx)