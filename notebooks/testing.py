import heapq as hq

priority_queue = []

# hq.heappush(priority_queue, [(8, 'fleck'),(7,'hippy'),(9,'gringo')])
hq.heappush(priority_queue, (8, 'fleck'))
hq.heappush(priority_queue, (7,'hippy'))
hq.heappush(priority_queue, (9,'gringo'))
# print(priority_queue)

for item in priority_queue:
    print(f'before pop len is {len(priority_queue)}')
    print(hq.heappop(priority_queue))
    print(f'after pop len is {len(priority_queue)}')
# print(hq.heappop(priority_queue))
# print(hq.heappop(priority_queue))
print(hq.heappop(priority_queue))
# print(priority_queue)