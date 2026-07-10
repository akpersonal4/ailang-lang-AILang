import os

SOURCE_TEXT = "apple\nbanana\ncherry\ndate\nfig\ngrape"
REPLICA_TEXT = "apple\ncherry\ndate\nelderberry\nfig\nhoneydew"

def read_lines(filepath):
    with open(filepath) as f:
        return [line.strip() for line in f if line.strip()]

def binary_search(sorted_list, target):
    left, right = 0, len(sorted_list) - 1
    while left <= right:
        mid = (left + right) // 2
        if sorted_list[mid] == target:
            return mid
        elif target < sorted_list[mid]:
            right = mid - 1
        else:
            left = mid + 1
    return -1

def find_unique(a, b):
    return [line for line in a if binary_search(b, line) < 0]

def find_common(a, b):
    return [line for line in a if binary_search(b, line) >= 0]

def main():
    with open("benchmarks/datasets/b2_features/ailang/source.txt", "w") as f:
        f.write(SOURCE_TEXT)
    with open("benchmarks/datasets/b2_features/ailang/replica.txt", "w") as f:
        f.write(REPLICA_TEXT)
    source = read_lines("benchmarks/datasets/b2_features/ailang/source.txt")
    replica = read_lines("benchmarks/datasets/b2_features/ailang/replica.txt")
    source.sort()
    replica.sort()
    print("=== Files only in source ===")
    for line in find_unique(source, replica):
        print(f"- {line}")
    print("=== Files only in replica ===")
    for line in find_unique(replica, source):
        print(f"- {line}")
    print("=== Common lines ===")
    for line in find_common(source, replica):
        print(f"- {line}")
    return 0

if __name__ == "__main__":
    main()
