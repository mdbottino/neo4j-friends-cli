# neo4j-friend-cli

This is a CLI app to experiment with neo4j. This app allows you to add people and befriend them.

## Overview

The goal is to use a very simple data model to experiment with Cypher and neo4j. Using a (sort of) realistic dataset shows the strenghts and weakneses of the database. It's also a great way to get my hands dirty and see what you can acomplish using Cypher. This little app solves the classic "list friends of a friend" problem.

## Installation

You can install the dependencies using the provided `requirements.txt` file:

> pip3 install -r requirements.txt

Note: It's highly recommended to use a virtual environment instead of the system installation

Another way is to use pipenv to create a virtual environment:

> pipenv install

## Running the script

> python3 main.py

Available commands:

- add (Add a person to the graph)
- befriend (Make two existing persons friends)
- edit (Update the age of a certain person)
- info (Get a summary of the nodes and relationships in the graph)
- list (Get the friends of a person)
- remove (Delete a person and all it's relationships from the graph)

## Data model

In the folder **docs** there is a file named _data-model.png_ with an example of the data model. There is only one node label (Person) and one relationship type (FRIENDS_OF).

## Misc

There are a couple of things missing including (but not limited to) unit tests, linting and CI config.

Regarding testing, I haven't figured out the best way to test the app. Most of the logic ended up being in the Cypher queries and currently I have no knowledge about an in-memory version to perform tests against. I may just use a local neo4j in the CI environment and test against it.
