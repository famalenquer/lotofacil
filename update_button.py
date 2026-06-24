import os
import glob

patterns = [
    '<button onclick="window.location.href=\'index.php\'" class="btn" style="background: var(--secondary); color: white;">Voltar ao Menu</button>',
    '<button onclick="window.location.href=\'index.php\'" class="btn" style="background: var(--secondary); color: white; width: auto;">Voltar ao Menu</button>',
    '<button onclick="window.location.href=\'index.php\'" style="background: var(--card-bg); border: 1px solid var(--card-border); color: white; padding: 8px 15px; border-radius: 8px; cursor: pointer; transition: 0.3s;">Voltar ao Menu</button>'
]

new_html = '''<button onclick="window.location.href=\'index.php\'" class="btn-voltar">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 8px;"><line x1="19" y1="12" x2="5" y2="12"></line><polyline points="12 19 5 12 12 5"></polyline></svg>
                Voltar
            </button>'''

files = glob.glob('c:/wamp64/www/lotofacil/*.php')
for f in files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
    
    modified = False
    for p in patterns:
        if p in content:
            content = content.replace(p, new_html)
            modified = True
            
    if modified:
        with open(f, 'w', encoding='utf-8') as file:
            file.write(content)
        print(f'Atualizado: {f}')
