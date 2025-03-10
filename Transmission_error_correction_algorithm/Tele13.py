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


def encoding(msg):
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


def main():
    print("Wybierz 1 aby zakodować, wybierz 2 żeby zdekodować.")
    wybor = int(input())

    if wybor == 1:
        # Kodowanie
        with open("input.txt", "r") as wejscie, open("zakodowane.txt", "w") as wyjscie:
            for line in wejscie:
                line = line.strip()
                msg = [int(char) for char in line]
                encoding(msg)
                wyjscie.write("".join(map(str, msg)) + '\n')

    elif wybor == 2:
        # Dekodowanie
        with open("zakodowane.txt", "r") as wejscie, open("output.txt", "w") as wyjscie:
            for line in wejscie:
                line = line.strip()
                msg = [int(char) for char in line]
                errors = []
                check(msg, errors)
                correct(msg, errors)
                wyjscie.write("".join(map(str, msg[:8])) + '\n')

    else:
        print("Nie wybrałeś 1 ani 2.")

if __name__ == "__main__":
    main()