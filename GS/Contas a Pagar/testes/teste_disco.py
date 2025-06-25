import psutil

print(type(psutil.disk_partitions(all=True)[0]))
