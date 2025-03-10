"""
Autorzy:
    - Piotr Janiszek 247678
    - Aliaksei Vishniavetski 249518
"""

H_ROWS = 8
H_COLUMNS = 16

H =    [[1, 1, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],
        [1, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
        [1, 1, 1, 0, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0],
        [1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 1, 1, 1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 1, 0],
        [1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1]]


def txt_to_int(msg, text):
    for char in text:
        msg.append(int(char))


def get_c(msg, r):
    suma = 0
    for j in range(len(msg)):
        suma += H[r][j] * msg[j]
    return suma % 2


def coding(msg):
    if len(msg) == 0:
        return
    for r in range(H_ROWS):
        c = get_c(msg, r)
        msg.append(c)


def swap(bit):
    if bit == 0:
        return 1
    else:
        return 0


def correct(msg, error):
    for i in range(16):
        for j in range(8):
            if H[j][i] != error[j]:
                break
            if j == 7:
                msg[i] = swap(msg[i])
                return
    for i in range(16):
        for j in range(i, 16):
            for k in range(8):
                if (H[k][i] ^ H[k][j]) != error[k]:
                    break
                if k == 7:
                    msg[i] = swap(msg[i])
                    msg[j] = swap(msg[j])
                    return


def check(msg, errors):
    for i in range(H_ROWS):
        e = 0
        for j in range(H_COLUMNS):
            e += H[i][j] * msg[j]
        errors.append(e % 2)


if __name__ == "__main__":
    msg = []
    text = input("Podaj 8 bitow wiadomosc do zakodowania:\n")
    txt_to_int(msg, text)
    coding(msg)

    print("\nZakodowana wiadomosc:")
    print(''.join(map(str, msg)))

    errors = []
    wrong_msg = []

    print("\nPodaj bledna wiadomosc:")
    text = input()
    txt_to_int(wrong_msg, text)

    check(wrong_msg, errors)

    print("\nWektor bledu:")
    print(''.join(map(str, errors)))

    correct(wrong_msg, errors)

    print("\nPoprawiona wiadomosc:")
    print(''.join(map(str, wrong_msg)))
