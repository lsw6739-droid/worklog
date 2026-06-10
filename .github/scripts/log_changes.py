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

for tid, t in curr_map.items():
    if tid not in prev_map and not t.get('parent_todo_id'):
        changes.append({'action':'added','title':t.get('title') or t.get('content',''),'employee':employees.get(t.get('employee_id'),'?')})

for tid, t in prev_map.items():
    if tid not in curr_map and not t.get('parent_todo_id'):
        changes.append({'action':'deleted','title':t.get('title') or t.get('content',''),'employee':employees.get(t.get('employee_id'),'?')})

for tid in set(prev_map) & set(curr_map):
    p, c = prev_map[tid], curr_map[tid]
    if c.get('parent_todo_id'): continue
    diffs = []
    if p.get('is_done') != c.get('is_done'):
        diffs.append('완료처리' if c.get('is_done') else '완료취소')
    if (p.get('title') or p.get('content','')) != (c.get('title') or c.get('content','')):
        diffs.append('제목 변경')
    if p.get('status') != c.get('status'):
        diffs.append(f"상태→{c.get('status','')}")
    if p.get('checklist') != c.get('checklist'):
        diffs.append('체크리스트 변경')
    if p.get('due_date') != c.get('due_date'):
        diffs.append(f"기한→{c.get('due_date') or '없음'}")
    if diffs:
        changes.append({'action':'modified','title':c.get('title') or c.get('content',''),'employee':employees.get(c.get('employee_id'),'?'),'detail':', '.join(diffs)})

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
