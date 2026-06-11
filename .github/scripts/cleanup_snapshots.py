import os, datetime

tz = datetime.timezone(datetime.timedelta(hours=9))
today = datetime.datetime.now(tz).date()
cutoff = today - datetime.timedelta(days=365)

if not os.path.exists('snapshots'):
    exit(0)

for fname in os.listdir('snapshots'):
    if len(fname) == 15 and fname.endswith('.json') and fname[0].isdigit():
        try:
            fdate = datetime.date.fromisoformat(fname[:10])
            if fdate < cutoff:
                os.remove(f'snapshots/{fname}')
                print(f'삭제: {fname}')
        except Exception:
            pass
