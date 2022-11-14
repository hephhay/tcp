import mmap
from timeit import default_timer as timer

start = timer()

with open("200k.txt", "r+b") as f:
    # memory-map the file, size 0 means whole file
    mm = mmap.mmap(f.fileno(), 0, prot=mmap.PROT_READ)
    # read content via standard file methods
    print(mm.find(b'4;0;11;26;0;17;3;0;\r\n'))
    #close memory map
    mm.close()

end = timer()
print((end - start)*1000*1000)