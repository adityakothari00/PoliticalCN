This repo contains the files associated with my Political Polarization project.

This repository primarly contains folders for each of the Senates that I am analyzing. The contents of each are the following: a raw voting data CSV file,
a raw member information data CSV file, a list_construction.py file, a signed_triangles.py file, and the output files of each of the scripts: edge list 
CSV file, node list CSV file and triangle count summary file, all triangle CSV file, respetcively.

**How to read it:**
The repository contains folders for each of the Senates that I am analyzing. Each folder contains two files: list_construction.py and signed_triangles.py.
list_construction.py is the first script that is run and takes the raw data and creates node and edge lists from them.
signed_triangles.py is what creates the graph and analyzes the balanced triangles, outputting a summary with counts of the different types of triangles.
