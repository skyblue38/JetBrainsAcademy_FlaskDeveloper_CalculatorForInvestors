import sqlite3
from sqlite3 import Error


# your code here
try:
    con = sqlite3.connect(':memory:')
except Error:
    print(Error)
finally:
    print('Connection established: Database created in memory')