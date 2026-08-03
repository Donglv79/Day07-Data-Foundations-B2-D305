import csv
import re
from pathlib import Path

D = Path('data/university_services_retrieval')
REQ = ['doc_id', 'title', 'source_url', 'retrieved_at', 'document_version']
mds = sorted(D.glob('*.md'))
rows = list(csv.DictReader(open(D / 'sources.csv', encoding='utf-8')))
ids, roles = [], {}
KEY = 'audience'

for p in mds:
    content = p.read_text(encoding='utf-8')
    fm = dict(re.findall(r'^(\w+):\s*(.+)$', content.split('---')[1], re.M))
    doc_id = fm.get('doc_id')
    ids.append(doc_id)
    role_val = fm.get(KEY)
    roles[role_val] = roles.get(role_val, 0) + 1
    ok = all(k in fm for k in REQ) and KEY in fm and doc_id == p.stem
    print(f"{p.name:40} {'OK' if ok else 'THIEU METADATA'}")

print('so file :', len(mds), '(can 5-10)')
print('csv     :', 'khop' if sorted(r['doc_id'] for r in rows) == sorted(ids) else 'LECH')
print(KEY, ':', roles)
