Author: Diego Mendez

Requirements: Python3
***NOTE***: If using visual studio code, install the sqllite extension to see the tables from the database. Then, enter 
           ctr + shift + p (windows). A search bar will appear, enter 'sqllite', then 'open database' and finally select 'dfs' database

***IMPORTANT NOTES***:
 1. when copyToDFS a file, the program checks for all the data nodes in the database and then checks for the 
    current ports that are running. Those ports that are running will be used to store our chunks. Example: I want
    to copy to our DFS the file 'prueba.txt'. I check for the available data nodes in our database and we get 6 servers, but only 3 are running. The 3 servers that are running will be stored to save the chunks of our files, not the 6 servers

2. when copyFromDFS a file, you need to be running the servers where the chunks were stored. Example: I want 
   to get a copy of the file named 'prueba.txt' stored in our DFS. Let's say this file was stored in 3 servers, 
   the server with nid 1, 2 and 4. The servers with nid 1, 2 and 4 should be running in order to get our copy of the file. 

***OTHER IMPORTANT NOTE***: for more info about the program, go to README2.md

***LAST IMPORTANT NOTE***: If you have any doubts, please contact me at diego.mendez1@upr.edu



Important files or folders:
 * storeDataBlocks: where we will store our data blocks
 * test.txt: file that will be used to copy to our dfs and copy from our dfs
 * jpMorgan.jpg: file that will be used to copy to our dfs and copy from our dfs

How to run program?
1. python createdb.py (to create database)

2. python testdb.py (to insert data to database)

3. python meta-data.py 8000 (to run meta-data server)

4. python data-node.py localhost 4017 storeDataBlocks 8000
   * storeDataBlocks will be the folder where we will store our data blocks. It is MANDATORY to use as third argument 'storeDataBlocks'. You can run multiple data node servers. The only argument that changes is the port

5. python ls.py localhost 8000 (this returns the files in table inode)

6. python copy.py prueba.txt localhost:8000:/home/prueba.txt
   * (to copy our file to the DFS, this will store chunks of our file in the storeDataBlocks folder)
   
   python copy.py jpMorgan.jpg localhost:8000:/home/jpMorgan.jpg 
   * (to copy our file to the DFS, this will store chunks of our file in the storeDataBlocks folder)

7. python copy.py localhost:8000:/home/prueba.txt copyPrueba.txt 
   * (to copy our file from the DFS and create a copyPrueba.txt with the original contents of prueba.txt)
   
   python copy.py localhost:8000:/home/jpMorgan.jpg copyjpMorgan.jpg
   * (to copy our file from the DFS and create a copyjpMorgan.jpg with the original contents of jpMorgan.jpg)


