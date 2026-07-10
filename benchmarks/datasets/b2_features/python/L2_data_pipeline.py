import json

def main():
    with open("benchmarks/datasets/b2_features/ailang/test_data.json") as f:
        records = [json.loads(line.strip()) for line in f if line.strip()]
    filtered = [r for r in records if r[2] >= 50]
    sorted_records = sorted(filtered, key=lambda r: r[2], reverse=True)
    for r in sorted_records:
        print(json.dumps(r))
    return 0

if __name__ == "__main__":
    main()
