from financial.currency import (
    currency_convert,
    currency_format,
    currency_get_rate,
    currency_list,
    currency_set_rate,
)


def test_currency_convert():
    tcResult = currency_convert(100, "USD", "EUR")
    if tcResult != 92:
        print("FAIL: expected 92 (100 USD to EUR), got " + str(tcResult))
        return False
    print("PASS: currency_convert")
    return True


def test_currency_convert_same():
    tcResult = currency_convert(50, "USD", "USD")
    if tcResult != 50:
        print("FAIL: expected 50 (USD to USD), got " + str(tcResult))
        return False
    print("PASS: currency_convert_same")
    return True


def test_currency_format():
    tcFormatted = currency_format(100, "USD")
    if tcFormatted != "$100":
        print("FAIL: expected '$100', got " + tcFormatted)
        return False
    tcEuro = currency_format(100, "EUR")
    if tcEuro != "€100":
        print("FAIL: expected '€100', got " + tcEuro)
        return False
    print("PASS: currency_format")
    return True


def test_currency_list():
    tcList = currency_list()
    tcLen = len(tcList)
    if tcLen != 5:
        print("FAIL: expected 5 currencies, got " + str(tcLen))
        return False
    print("PASS: currency_list (" + str(tcLen) + " codes)")
    return True


def test_currency_set_get_rate():
    currency_set_rate("USD", "GBP", 75 / 100)
    tcRate = currency_get_rate("USD", "GBP")
    if tcRate != 75 / 100:
        print("FAIL: expected 0.75, got " + str(tcRate))
        return False
    tcConverted = currency_convert(200, "USD", "GBP")
    if tcConverted != 150:
        print("FAIL: expected 150 (200 USD to GBP at 0.75), got " + str(tcConverted))
        return False
    print("PASS: currency_set_get_rate")
    return True


def main():
    tc1 = test_currency_convert()
    if tc1 == False:
        return 1
    tc2 = test_currency_convert_same()
    if tc2 == False:
        return 1
    tc3 = test_currency_format()
    if tc3 == False:
        return 1
    tc4 = test_currency_list()
    if tc4 == False:
        return 1
    tc5 = test_currency_set_get_rate()
    if tc5 == False:
        return 1
    print("ALL CURRENCY TESTS PASSED")
    return 0


if __name__ == "__main__":
    exit(main())
