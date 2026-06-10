import os, datetime

tz = datetime.timezone(datetime.timedelta(hours=9))
today = datetime.datetime.now(tz).date()
cutoff = today - datetime.timedelta(days=7)

if not os.path.exists('logs'):
    exit(0)

for fname in os.listdir('logs'):
    if len(fname) == 15 and fname.endswith('.json') and fname[0].isdigit():
        try:
            fdate = datetime.date.fromisoformat(fname[:10])
            if fdate < cutoff:
                os.remove(f'logs/{fname}')
                print(f'삭제: {fname}')
        except Exception:
            pass
