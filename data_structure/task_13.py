import itertools


def three_sum(nums):
    l = []
    for a in range(len(nums)):
        for b in range(len(nums)):
            for c in range(len(nums)):
                if (a != b) and (a != c) and (b != c) and (nums[a] + nums[b] + nums[c] == 0):
                    if sorted([nums[a], nums[b], nums[c]]) not in l:
                        l.append(sorted([nums[a], nums[b], nums[c]]))
    return l


def three_sum_2(nums):
    r = []
    if len(nums) < 3:
        return r
    m = list(itertools.combinations(nums, 3))
    for n in m:
        if sum(n) == 0:
            if sorted(n) not in r:
                r.append(sorted(n))
    return r


print(three_sum_2(
    [-4, -8, 7, 13, 10, 1, -14, -13, 0, 8, 6, -13, -5, -4, -12, 2, -11, 7, -5, 0, -9, -14, -8, -9, 2, -7, -13, -3, 13,
     9, -14, -6, 8, 1, 14, -5, -13, 8, -10, -5, 1, 11, -11, 3, 14, -8, -10, -12, 6, -8, -5, 13, -15, 2, 11, -5, 10, 6,
     -1, 1, 0, 0, 2, -7, 8, -6, 3, 3, -13, 8, 5, -5, -3, 9, 5, -4, -14, 11, -8, 7, 10, -6, -3, 11, 12, -14, -9, -1, 7,
     5, -15, 14, 12, -5, -8, -2, 4, 2, -14, -2, -12, 6, 8, 0, 0, -2, 3, -7, -14, 2, 7, 12, 12, 12, 0, 9, 13, -2, -15,
     -3, 10, -14, -4, 7, -12, 3, -10]))
print(three_sum(
    [-4, -8, 7, 13, 10, 1, -14, -13, 0, 8, 6, -13, -5, -4, -12, 2, -11, 7, -5, 0, -9, -14, -8, -9, 2, -7, -13, -3, 13,
     9, -14, -6, 8, 1, 14, -5, -13, 8, -10, -5, 1, 11, -11, 3, 14, -8, -10, -12, 6, -8, -5, 13, -15, 2, 11, -5, 10, 6,
     -1, 1, 0, 0, 2, -7, 8, -6, 3, 3, -13, 8, 5, -5, -3, 9, 5, -4, -14, 11, -8, 7, 10, -6, -3, 11, 12, -14, -9, -1, 7,
     5, -15, 14, 12, -5, -8, -2, 4, 2, -14, -2, -12, 6, 8, 0, 0, -2, 3, -7, -14, 2, 7, 12, 12, 12, 0, 9, 13, -2, -15,
     -3, 10, -14, -4, 7, -12, 3, -10]))