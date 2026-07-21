def get_user_age(users, username):
    return users.get(username, -1)


def main():
    users = {"Alice": 30, "Bob": 25}
    age = get_user_age(users, "Charlie")
    print(age)
    return 0


if __name__ == "__main__":
    main()
