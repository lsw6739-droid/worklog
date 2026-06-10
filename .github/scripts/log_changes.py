import json, os, datetime

with open('/tmp/current.json') as f:
    current = json.load(f)
with open('/tmp/employees.json') as f:
    employees = {e['id']: e['name'] for e in json.load(f)}

state_file = 'logs/state.json'
previous = []
if os.path.exists(state_file):
    with open(state_file) as f:
        previous = json.load(f)

prev_map = {t['id']: t for t in previous}
curr_map = {t['id']: t for t in current}
changes = []

def parse_cl(raw):
    try:
        return json.loads(raw) if raw else []
    except:
        return []

def compare_checklist(prev_raw, curr_raw):
    prev_cl = parse_cl(prev_raw)
    curr_cl = parse_cl(curr_raw)
    prev_by_id = {i.get('id', i.get('text','')): i for i in prev_cl}
    curr_by_id = {i.get('id', i.get('text','')): i for i in curr_cl}
    details = []
    for key, item in curr_by_id.items():
        if item.get('type') == 'header':
            continue
        text = item.get('text', '')
        if key in prev_by_id:
            p = prev_by_id[key]
            if not p.get('done') and item.get('done'):
                details.append(f'✅ {text}')
            elif p.get('done') and not item.get('done'):
                details.append(f'↩️ {text}')
            elif p.get('text','') != text:
                details.append(f'✏️ {p.get("text","")} → {text}')
        else:
            details.append(f'➕ {text}')
    for key, item in prev_by_id.items():
        if item.get('type') == 'header':
            continue
        if key not in curr_by_id:
            details.append(f'🗑 {item.get("text","")}')
    return details

for tid, t in curr_map.items():
    if tid not in prev_map and not t.get('parent_todo_id'):
        cl = parse_cl(t.get('checklist'))
        cl_items = [c.get('text','') for c in cl if c.get('type') != 'header']
        changes.append({'action':'added','title':t.get('title') or t.get('content',''),'employee':employees.get(t.get('employee_id'),'?'),'details':cl_items})

for tid, t in prev_map.items():
    if tid not in curr_map and not t.get('parent_todo_id'):
        changes.append({'action':'deleted','title':t.get('title') or t.get('content',''),'employee':employees.get(t.get('employee_id'),'?'),'details':[]})

for tid in set(prev_map) & set(curr_map):
    p, c = prev_map[tid], curr_map[tid]
    if c.get('parent_todo_id'): continue
    details = []
    if p.get('is_done') != c.get('is_done'):
        details.append('완료처리' if c.get('is_done') else '완료취소')
    old_title = p.get('title') or p.get('content','')
    new_title = c.get('title') or c.get('content','')
    if old_title != new_title:
        details.append(f'제목: {old_title} → {new_title}')
    if p.get('status') != c.get('status'):
        details.append(f"상태: {p.get('status','')} → {c.get('status','')}")
    if p.get('due_date') != c.get('due_date'):
        details.append(f"기한: {p.get('due_date') or '없음'} → {c.get('due_date') or '없음'}")
    if p.get('checklist') != c.get('checklist'):
        details.extend(compare_checklist(p.get('checklist'), c.get('checklist')))
    if details:
        changes.append({'action':'modified','title':new_title,'employee':employees.get(c.get('employee_id'),'?'),'details':details})

tz = datetime.timezone(datetime.timedelta(hours=9))
now = datetime.datetime.now(tz)
date_str = now.strftime('%Y-%m-%d')
time_str = now.strftime('%H:%M')

if changes:
    os.makedirs('logs', exist_ok=True)
    log_file = f'logs/{date_str}.json'
    log = []
    if os.path.exists(log_file):
        with open(log_file) as f:
            log = json.load(f)
    log.append({'time': time_str, 'changes': changes})
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(log, f, ensure_ascii=False, indent=2)
    print(f"변경 {len(changes)}건 기록: {time_str}")
else:
    print("변경 없음")

with open('logs/state.json', 'w', encoding='utf-8') as f:
    json.dump(current, f, ensure_ascii=False)
