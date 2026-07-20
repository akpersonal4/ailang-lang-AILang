def count_passing(scores):
    return sum(1 for s in scores if s >= 50)


def main():
    scores = [70, 50, 30, 85, 49]
    result = count_passing(scores)
    print(result)
    return 0


if __name__ == "__main__":
    main()
