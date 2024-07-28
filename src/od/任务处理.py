#  任务处理
import heapq


def solve():
    ans = 0
    pq = []  # 使用优先队列作为待处理队列
    for i in range(100005):
        while pq and pq[0] < i:
            heapq.heappop(pq)  # 第一步：移除已经结束的任务
        if i in a:
            for task in a[i]:
                heapq.heappush(pq, task)  # 第二步：将当前时刻开始的任务加入队列
        if pq:
            ans += 1
            heapq.heappop(pq)  # 第三步：从队列中取出结束时间最早的任务，安排在这一天
    return ans


n = int(input())  # 输入任务数量
a = {}  # 存储任务的开始和结束时间
for _ in range(n):
    x, y = map(int, input().split())
    if x in a:
        a[x].append(y)
    else:
        a[x] = [y]
print(solve())
