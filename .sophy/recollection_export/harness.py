#!/usr/bin/env python3
import os
os.makedirs('recollections', exist_ok=True)
with open('recollections/manifest.txt','w') as f:
    f.write('manifest generated')
print('harness executed')
