# JetBRAINS FLASK DEVELOPER - Calculator for Investors project
# https://hyperskill.org/projects/264
# submitted by Chris Freeman 2022-NOV-17
# Version History
# Stage 1/4 - 0.1 2022/11/12
# Stage 2/4 - 0.2 2022/11/14
# Stage 3/4 - 0.3 2022/11/18

import sqlite3
import csv
from os.path import exists


db_name = 'investor.db'
csv_company = 'companies.csv'
csv_financial = 'financial.csv'


def build_database():
    if exists(db_name):
        con = sqlite3.connect(db_name)
        return con          # just return if the database is already available
    assert exists(csv_company), 'companies.csv file not found'
    assert exists(csv_financial), 'financial.csv file not found'
    con = sqlite3.connect(db_name)
    try:
        with con:
            con.execute('CREATE TABLE companies(ticker TEXT PRIMARY KEY, name TEXT, sector TEXT);')
    except Exception as e:
        print("Can't create company table:", e)
    try:
        line = -1
        with open(csv_company, 'r', newline='', encoding='latin-1') as company_fileobj:
            company_iterator = csv.reader(company_fileobj)
            for row in company_iterator:
                line += 1
                if line == 0:
                    assert row == ['ticker', 'name', 'sector'], 'companies.csv file structure fault'
                    continue
                row_nulled = [None if r == '' else r for r in row]
                row_tuple = tuple(row_nulled)
                con.execute('INSERT INTO companies(ticker, name, sector) VALUES (?, ?, ?);',
                            row_tuple)
    except Exception as e:
        print("Can't insert companies:", e)
    try:
        with con:
            con.execute("""CREATE TABLE financial(
                ticker TEXT PRIMARY KEY, 
                ebitda REAL, 
                sales REAL, 
                net_profit REAL, 
                market_price REAL, 
                net_debt REAL, 
                assets REAL, 
                equity REAL, 
                cash_equivalents REAL, 
                liabilities REAL
                );""")
    except Exception as e:
        print("Can't create financial table:", e)
    try:
        line = -1
        with open(csv_financial, 'r', newline='', encoding='latin-1') as financial_fileobj:
            financial_iterator = csv.reader(financial_fileobj)
            for row in financial_iterator:
                line += 1
                if line == 0:
                    assert row == ['ticker', 'ebitda', 'sales', 'net_profit', 'market_price',
                                   'net_debt', 'assets', 'equity', 'cash_equivalents', 'liabilities'], \
                        'financial.csv file structure fault'
                    continue
                row_float = [float(int(r)) if r.isdigit() else r for r in row]
                row_nulled = [None if r == '' else r for r in row_float]
                row_tuple = tuple(row_nulled)
                with con:
                    con.execute("""INSERT INTO financial(ticker, ebitda, sales, net_profit, 
                        market_price, net_debt, assets, equity, cash_equivalents, liabilities) 
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", row_tuple)
    except Exception as e:
        print("Can't insert financials:", e)
    else:
        print('Database created successfully!')
    finally:
        try:
            with con:
                con.execute("""CREATE TABLE metrics(
                    ticker TEXT PRIMARY KEY, 
                    nd_ebitda REAL, 
                    roe REAL, 
                    roa REAL
                    );""")
        except Exception as e:
            print("Can't create metrics table:", e)
        return con


def get_option(prompts, valid_options, no_prompt=False, return_when_invalid=False):
    valid = False
    while not valid:
        print(prompts)
        option = ''
        while option == '':
            if not no_prompt:
                print('Enter an option:')
            option = input().strip()
        if option not in valid_options:
            print('Invalid option!')
            if return_when_invalid:
                valid = True
        else:
            valid = True
    return option


def build_metrics(con):
    try:
        with con:
            con.execute("DELETE FROM metrics;")
    except Exception as e:
        print("Deleting Metrics:", e)
    try:
        with con:
            mlist = con.execute("SELECT * FROM financial;").fetchall()
    except Exception as e:
        print("Metrics: Can't select financial data:", e)
    for row in mlist:
        ticker = row[0]                             # company ticker code
        if row[5] is None or row[1] is None:
            nd_ebitda = None
        else:
            nd_ebitda = row[5] / row[1]             # Net debt / EBITDA
        if row[3] is None or row[7] is None:
            roe = None
        else:
            roe = row[3] / row[7]                   # Net profit / Equity
        if row[3] is None or row[6] is None:
            roa = None
        else:
            roa = row[3] / row[6]                   # Net profit / Assets
        metrics_tuple = (ticker, nd_ebitda, roe, roa)
        try:
            with con:
                con.execute("INSERT INTO metrics(ticker, nd_ebitda, roe, roa) VALUES (?, ?, ?, ?);",
                            metrics_tuple)
        except Exception as e:
            print("Failed to insert metrics:", e)


def top10_menu(con):
    build_metrics(con)
    tstring = 'TOP TEN MENU\n0 Back\n1 List by ND/EBITDA\n2 List by ROE\n3 List by ROA'
    tvalids = ['0', '1', '2', '3']
    choice = get_option(tstring, tvalids, return_when_invalid=True)
    if choice == tvalids[0]:
        return                          # 0 Back
    elif choice == tvalids[1]:
        try:                            # 1 List by ND/EBITDA
            with con:
                top10_nd_ebitda = con.execute('''SELECT ticker, round(nd_ebitda,2) FROM metrics 
                    ORDER BY nd_ebitda DESC, ticker DESC
                    LIMIT 10;''').fetchall()
        except Exception as e:
            print("Failed to read top10 ND/EBITDA", e)
        print("TICKER ND/EBITDA")
        for row in top10_nd_ebitda:
            ticker = row[0]
            nd_ebitda = row[1]
            print(ticker, nd_ebitda)
    elif choice == tvalids[2]:
        try:                            # 2 List by ROE
            with con:
                top10_roe = con.execute('''SELECT ticker, round(roe,2) FROM metrics 
                    ORDER BY roe DESC, ticker DESC
                    LIMIT 10;''').fetchall()
        except Exception as e:
            print("Failed to read top10 ROE", e)
        print("TICKER ROE")
        for row in top10_roe:
            ticker = row[0]
            roe = row[1]
            print(ticker, roe)
    elif choice == tvalids[3]:
        try:                            # 2 List by ROA
            with con:
                top10_roa = con.execute('''SELECT ticker, round(roa,2) FROM metrics 
                    ORDER BY roa DESC, ticker DESC
                    LIMIT 10;''').fetchall()
        except Exception as e:
            print("Failed to read top10 ROA", e)
        print("TICKER ROA")
        for row in top10_roa:
            ticker = row[0]
            roa = row[1]
            print(ticker, roa)


def get_company_details():
    print("Enter ticker (in the format 'MOON'):")
    ticker = input()
    print("Enter company (in the format 'Moon Corp'):")
    name = input()
    print("Enter industries (in the format 'Technology'):")
    sector = input()
    return (ticker, name, sector)


def get_company_financials(ticker):
    ebitda = input("Enter ebitda (in the format '987654321'):\n")
    sales = input("Enter sales (in the format '987654321'):\n")
    net_profit = input("Enter net profit (in the format '987654321'):\n")
    market_price = input("Enter market price (in the format '987654321'):\n")
    net_debt = input("Enter net debt (in the format '987654321'):\n")
    assets = input("Enter assets (in the format '987654321'):\n")
    equity = input("Enter equity (in the format '987654321'):\n")
    cash_equivalents = input("Enter cash equivalents (in the format '987654321'):\n")
    liabilities = input("Enter liabilities (in the format '987654321'):\n")
    return (ticker, ebitda, sales, net_profit, market_price, net_debt, assets, equity,
            cash_equivalents, liabilities)


def financial_ratio(title, numerator, denominator):
    if numerator is None or denominator is None:
        return "{} = None".format(title)
    return "{} = {:.2f}".format(title, numerator / denominator)


def crud_menu(con):
    cstring = 'CRUD MENU\n0 Back\n1 Create a company\n2 Read a company\n3 Update a company\n\
4 Delete a company\n5 List all companies'
    cvalids = ['0', '1', '2', '3', '4', '5']    # valid options
    choice = get_option(cstring, cvalids)
    if choice == cvalids[0]:
        return                                  # 0 Back
    elif choice == cvalids[1]:
        company_tuple = get_company_details()   # 1 Create a company
        financial_tuple = get_company_financials(company_tuple[0])
        try:
            with con:
                con.execute('INSERT INTO companies(ticker, name, sector) VALUES (?, ?, ?);', company_tuple)
                con.execute("""INSERT INTO financial(ticker, ebitda, sales, net_profit, 
                    market_price, net_debt, assets, equity, cash_equivalents, liabilities) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", financial_tuple)
        except sqlite3.IntegrityError as e:
            print('Create company failed:', e)
        else:
            print('Company created successfully!')
    elif choice == cvalids[2]:
        name = input('Enter company name:\n')   # 2 Read a company
        cname = "%{}%".format(name)
        try:
            with con:
                clist = con.execute("SELECT * FROM companies WHERE name LIKE ?;", (cname,)).fetchall()
        except Exception as e:
            print("Can't select company:", e)
        if len(clist) == 0:
            print("Company not found!")
            return
        for r in range(len(clist)):
            print(r, clist[r][1])
        coy = int(get_option("Enter company number:", [str(r) for r in range(len(clist))], no_prompt=True))
        ticker = clist[coy][0]
        try:
            with con:
                plist = con.execute("SELECT * FROM financial WHERE ticker = ?;", (ticker,)).fetchone()
        except Exception as e:
            print("Can't get company financials:", e)
        print(ticker, clist[coy][1])
        print(financial_ratio("P/E", plist[4], plist[3]))   # Market price / Net profit
        print(financial_ratio("P/S", plist[4], plist[2]))   # Market price / Sales
        print(financial_ratio("P/B", plist[4], plist[6]))   # Market price / Assets
        print(financial_ratio("ND/EBITDA", plist[5], plist[1]))  # Net debt / EBITDA
        print(financial_ratio("ROE", plist[3], plist[7]))   # Net profit / Equity
        print(financial_ratio("ROA", plist[3], plist[6]))   # Net profit / Assets
        print(financial_ratio("L/A", plist[9], plist[6]))   # Liabilities / Assets
    elif choice == cvalids[3]:
        name = input('Enter company name:\n')     # 3 Update a company
        cname = "%{}%".format(name)
        try:
            with con:
                clist = con.execute("SELECT * FROM companies WHERE name LIKE ?;", (cname,)).fetchall()
        except Exception as e:
            print("Can't select company:", e)
        if len(clist) == 0:
            print("Company not found!")
            return
        for r in range(len(clist)):
            print(r, clist[r][1])
        coy = int(get_option("Enter company number:", [str(r) for r in range(len(clist))], no_prompt=True))
        ticker = clist[coy][0]
        f = get_company_financials(ticker)
        update_tuple = (f[1], f[2], f[3], f[4], f[5], f[6], f[7], f[8], f[9], f[0])
        try:
            with con:
                con.execute('''UPDATE financial 
                            SET ebitda = ?,
                                sales = ?,
                                net_profit = ?,
                                market_price = ?,
                                net_debt = ?,
                                assets = ?,
                                equity = ?,
                                cash_equivalents = ?,
                                liabilities = ?
                            WHERE ticker = ?;''', update_tuple)
        except Exception as e:
            print('Company financials update failed:', e)
        else:
            print('Company updated successfully!')
    elif choice == cvalids[4]:
        name = input('Enter company name:\n')   # 4 Delete a company
        cname = "%{}%".format(name)
        try:
            with con:
                clist = con.execute("SELECT * FROM companies WHERE name LIKE ?;", (cname,)).fetchall()
        except Exception as e:
            print("Can't select company:", e)
        if len(clist) == 0:
            print("Company not found!")
            return
        for r in range(len(clist)):
            print(r, clist[r][1])
        coy = int(get_option("Enter company number:", [str(r) for r in range(len(clist))], no_prompt=True))
        ticker = clist[coy][0]
        try:
            with con:
                con.execute("DELETE FROM financial WHERE ticker = ?;", (ticker,))
                con.execute("DELETE FROM companies WHERE ticker = ?;", (ticker,))
        except Exception as e:
            print("Can't delete financials and/or company:", e)
        else:
            print('Company deleted successfully!')
    elif choice == cvalids[5]:
        print('COMPANY LIST')       # 5 List all companies
        with con:
            clist = con.execute("SELECT * FROM companies ORDER BY ticker").fetchall()
        for row in clist:
            print(row[0], row[1], row[2])
    else:
        raise RuntimeError          # shouldn't get here!


def main_menu(con):
    mstring = 'MAIN MENU\n0 Exit\n1 CRUD operations\n2 Show top ten companies by criteria'
    mvalids = ['0', '1', '2']   # valid options
    fin = False
    while not fin:
        choice = get_option(mstring, mvalids)
        if choice == mvalids[0]:
            fin = True          # 0 Back
        elif choice == mvalids[1]:
            crud_menu(con)      # 1 CRUD operations
        elif choice == mvalids[2]:
            top10_menu(con)     # 2 Show top ten companies
        else:
            raise RuntimeError  # shouldn't get here!


if __name__ == '__main__':
    print('Welcome to the Investor Program!\n')
    connect = build_database()      # build database if required & get Sqlite3 connection
    main_menu(connect)              # off we go...
    connect.close()                 # release Sqlite3 connection
    print('Have a nice day!')   # all done!
