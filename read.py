import mmap
from timeit import default_timer as timer
from collections import defaultdict

hashmap = defaultdict(lambda : False)
with open("200k.txt", "r+b") as f:
    # memory-map the file, size 0 means whole file
    mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
    while True:
        a = mm.readline().strip()
        if a == b'':
            break
        hashmap[a] = True

start = timer()

a = bytes('8;0;1;28;0;7;4;0;', 'utf-8')

print(a.__len__())

print(hashmap[a])

end = timer()

print((end - start)*1000*1000)