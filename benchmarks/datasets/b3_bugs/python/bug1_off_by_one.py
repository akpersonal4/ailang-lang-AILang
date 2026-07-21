def sum_even(numbers):
    result = 0
    i = 0
    while i < len(numbers):
        if numbers[i] % 2 == 0:
            result += numbers[i]
        i += 1
    return result


def main():
    test = [1, 2, 3]
    result = sum_even(test)
    print(result)
    return 0


if __name__ == "__main__":
    main()
