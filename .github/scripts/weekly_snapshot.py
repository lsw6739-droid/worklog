import json, os, datetime

with open('/tmp/current.json') as f:
    current = json.load(f)
with open('/tmp/employees.json') as f:
    employees = {e['id']: e['name'] for e in json.load(f)}

# 원본 투두만 (공유본 제외)
root_todos = [t for t in current if not t.get('parent_todo_id')]

snapshot = []
for t in root_todos:
    cl = []
    if t.get('checklist'):
        try:
            cl = json.loads(t['checklist'])
        except:
            cl = []
    snapshot.append({
        'title': t.get('title') or t.get('content', ''),
        'content': t.get('content', ''),
        'status': t.get('status', ''),
        'due_date': t.get('due_date') or '',
        'note': t.get('note') or '',
        'employee_name': employees.get(t.get('employee_id'), '?'),
        'assignee_names': t.get('assignee_names') or '',
        'is_done': bool(t.get('is_done')),
        'source': t.get('source') or '',
        'checklist': cl
    })

tz = datetime.timezone(datetime.timedelta(hours=9))
now = datetime.datetime.now(tz)
date_str = now.strftime('%Y-%m-%d')

os.makedirs('snapshots', exist_ok=True)
out_file = f'snapshots/{date_str}.json'
with open(out_file, 'w', encoding='utf-8') as f:
    json.dump(snapshot, f, ensure_ascii=False, indent=2)

print(f"스냅샷 저장: {date_str}, {len(snapshot)}개 투두")
