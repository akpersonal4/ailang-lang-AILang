def is_even(n):
    return n % 2 == 0


def sum_even_numbers(numbers, threshold=0):
    return sum(n for n in numbers if is_even(n) and n > threshold)


def main():
    import sys

    test = [1, 2, 3, 4, 5, 6]
    threshold = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    result = sum_even_numbers(test, threshold=threshold)
    print(result)
    return 0


if __name__ == "__main__":
    main()
