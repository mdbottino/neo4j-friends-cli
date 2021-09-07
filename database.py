from neo4j import GraphDatabase

import config

driver = GraphDatabase.driver(config.DATABASE_URI,
                              auth=(config.DATABASE_USER, config.DATABASE_PASS))