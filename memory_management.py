### Script for founctions to limit memory usage when encountering memory leaks
### Found https://stackoverflow.com/questions/41105733/limit-ram-usage-to-python-program

# import resource
# import sys

# def limit_memory():
#         """Limit max memory usage to half."""
#         soft, hard = resource.getrlimit(resource.RLIMIT_AS)
#         # Convert KiB to bytes, and divide by integer to 
#         resource.setrlimit(resource.RLIMIT_AS, (int(get_memory() * 1024 / 5), hard))


# def get_memory():
#     with open('/proc/meminfo', 'r') as mem:
#         free_memory = 0
#         for i in mem:
#             sline = i.split()
#             if str(sline[0]) in ('MemFree:', 'Buffers:', 'Cached:'):
#                 free_memory += int(sline[1])
#                 return free_memory  # KiB

import psutil
import resource

def limit_memory(percentage = 0.8):
        # Calculate the maximum memory limit (80% of available memory)
    virtual_memory = psutil.virtual_memory()
    available_memory = virtual_memory.available
    memory_limit = int(available_memory * percentage)

        # Set the memory limit
    # resource.setrlimit(resource.RLIMIT_AS, (memory_limit, memory_limit))
    resource.setrlimit(resource.RLIMIT_DATA, (memory_limit, memory_limit))
    print("memory set to: " + str(memory_limit))

        
