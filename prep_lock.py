import os, json
from datetime import datetime
RESULTS='results'
# xoa ket qua pass cu cua bai goi/0 neu co (de test khoa)
for f in os.listdir(RESULTS):
    if f.startswith('anonymous_goi_0_') and 'test' not in f:
        # giu lai file test 30% da tao, xoa file 100%
        if 'pass' in f: os.remove(os.path.join(RESULTS,f))
# dam bao bai goi/0 chi co 5% (chua pass) -> bai 2 locked
print('done prep')
