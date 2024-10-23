import pandas as pd
import re
import netaddr
from bisect import bisect
import csv

df = pd.read_csv("ip2location.csv")

def lookup_region(ipaddr):
    ip = re.sub("[a-z]|[A-Z]", "0", ipaddr)
    int_representation = int(netaddr.IPAddress(ip))
    idx = bisect(df["low"], int_representation) - 1
    return df.iloc[idx]["region"]

class Filing:
    def __init__(self, html):
        self.dates = re.findall(r"\d[19|20]\d\d-\d[01|02|03|04|05|06|07|08|09|10|11|12]-\d\d", html)
        sic = re.findall(r"SIC=(\d+)", html)
        if len(sic) == 0:
            self.sic = None
        else:
            self.sic = int(sic[0])
        self.addresses = []
        for addr_html in re.findall(r'<div class="mailer">([\s\S]+?)</div>', html):
            lines = []
            for line in re.findall(r'<span class="mailerAddress">([\s\S]+?)</span>', addr_html):
                lines.append(line.strip())
            self.addresses.append("\n".join(lines))
        
        # remove all empty strings
        self.addresses = [i for i in self.addresses if i]

    def state(self):
        for address in self.addresses:
            state_code = re.findall(" ([A-Z][A-Z]) \d\d\d\d\d", address)
            if len(state_code) == 0:
                continue
            else:
                return ''.join(state_code)
        return None
