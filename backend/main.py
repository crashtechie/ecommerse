def main():
    test_str = "(0.T|00|911|411|422|611|811|*671[2-9]XX[2-9]XXXXXX|*67[2-9]XX[2-9]XXXXXX|*67[2-9]XXXXXX.T|*67[2-9]XXXXXX.#|*721[2-9]XX[2-9]XXXXXX|*72[2-9]XX[2-9]XXXXXX|*72[2-9]XXXXXX.#|*72[2-9]XXXXXX.T|*74[2-9][2-9]XXXXXXXXX|*75[2-9][2-9][2-9]XXXXXXXXX|*90[2-9]XXXXXXXXX|*92[2-9]XXXXXXXXX|*3XX|*15|*23|*27|*91|*93|*7[3-9]|*[5-6][0-9].T|*8[0-9]|*99|1[2-9]XX[2-9]XXXXXX|[2-9]XX[2-9]XXXXXX|011[0-9].T|[2-9]XXXXXX.T)"
    expected_str = "(0.T|00|911|411|422|611|811|*671[2-9]XX[2-9]XXXXXX|*67[2-9]XX[2-9]XXXXXX|*67[2-9]XXXXXX.T|*67[2-9]XXXXXX.#|*721[2-9]XX[2-9]XXXXXX|*72[2-9]XX[2-9]XXXXXX|*72[2-9]XXXXXX.#|*72[2-9]XXXXXX.T|*74[2-9][2-9]XXXXXXXXX|*75[2-9][2-9][2-9]XXXXXXXXX|*90[2-9]XXXXXXXXX|*92[2-9]XXXXXXXXX|*3XX|*15|*23|*27|*91|*93|*7[3-9]|*[5-6][0-9].T|*8[0-9]|*99|1[2-9]XX[2-9]XXXXXX|[2-9]XX[2-9]XXXXXX|011[0-9].T|[2-9]XXXXXX.T)"
    if test_str == expected_str:
        print("Test passed!")
    else:
        print("Test failed!")


if __name__ == "__main__":
    main()
