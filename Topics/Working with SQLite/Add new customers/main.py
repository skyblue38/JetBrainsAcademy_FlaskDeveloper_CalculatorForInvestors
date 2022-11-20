cust_tuple_list = []
for i in range(3):
    cust_tuple = tuple(input().split(';'))
    cust_tuple_list.append(cust_tuple)
cursor.executemany('INSERT INTO customers(CustomerName, Address, City, PostalCode, Country) VALUES (?,?,?,?,?)',
                   cust_tuple_list)
con.commit()