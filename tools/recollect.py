#!/usr/bin/env python3
"""Simple recollect stub: writes a timestamped JSON file into recollections/"""
import json
from datetime import datetime
import os
os.makedirs('recollections', exist_ok=True)
now = datetime.utcnow().isoformat() + 'Z'
payload = {'recollection_time': now, 'summary': 'Automated recollection run (stub)'}
with open('recollections/recollection-'+now.replace(':','-')+'.json','w') as f:
    json.dump(payload, f)
print('wrote recollection', now)
