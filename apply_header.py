import os
import glob
import re

files = glob.glob('c:/wamp64/www/lotofacil/*.php')
files = [f for f in files if not f.endswith('header.php')]

# The regular expression matches the <nav class="navbar"> ... </nav> block
nav_regex = re.compile(r'<nav\s+class="navbar".*?</nav>', re.DOTALL)

for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # 1. Replace the <nav> block with the header include
    if nav_regex.search(content):
        # We replace the first occurrence
        content = nav_regex.sub("<?php include 'header.php'; ?>", content, count=1)
        
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f'Atualizado (removida <nav>): {f}')
    
    # Wait, some pages might not have a <nav> but we still want the header.
    # Actually, all our 9 main pages have <nav class="navbar">
