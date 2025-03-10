"""
Autorzy:
    - Piotr Janiszek 247678
    - Aliaksei Vishniavetski 249518
"""

H_ROWS = 4
H_COLUMNS = 12

# Macierz parzystości
H = [[1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 0, 0],
     [1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 0],
     [1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 1, 0],
     [0, 1, 1, 1, 0, 0, 1, 1, 0, 0, 0, 1]]


def txt_to_int(text):
    """Konwertuje tekst na listę liczb całkowitych"""
    if not text.isdigit():
        raise ValueError("Wiadomość powinna składać się tylko z cyfr 0 i 1")
    return [int(char) for char in text]


def get_C(msg, r):
    """Oblicza bit parzystości dla danego wiersza"""
    return sum(H[r][j] * msg[j] for j in range(len(msg))) % 2


def encoding(msg):
    """Koduje wiadomość, dodając bity parzystości"""
    msg.extend(get_C(msg, r) for r in range(H_ROWS))


def swap(bit):
    """Zamienia wartość bitu"""
    return 1 if bit == 0 else 0


def correct(msg, error):
    """Poprawia błędnie odebraną wiadomość"""
    for k in range(H_COLUMNS):
        # Sprawdza, czy błąd odpowiada wzorcowemu wzorcowi błędu w macierzy H
        if all(error[r] == H[r][k] for r in range(H_ROWS)):
            # Jeśli tak, to zamienia bit na przeciwny
            msg[k] = swap(msg[k])
            break


def check(msg):
    """Sprawdza poprawność wiadomości i dokonuje ewentualnej korekty"""
    if len(msg) != H_COLUMNS:
        raise ValueError("Niepoprawna długość wiadomości")

    # Oblicza błędy w wiadomości
    errors = [get_C(msg, i) for i in range(H_ROWS)]
    # Jeśli istnieją błędy, to dokonuje korekty
    if any(errors):
        correct(msg, errors)


if __name__ == "__main__":
    try:
        # Wprowadzenie wiadomości do kodowania
        text = input("Podaj wiadomość do zakodowania: ")
        msg = txt_to_int(text)
        encoding(msg)
        print("\nZakodowana wiadomość:", "".join(map(str, msg)))

        # Wprowadzenie błędnej wiadomości
        text = input("\nPodaj błędną wiadomość: ")
        wrong_msg = txt_to_int(text)
        check(wrong_msg)
        print("\nPoprawiona wiadomość:", "".join(map(str, wrong_msg)))

    except ValueError as e:
        print("Wystąpił błąd:", e)
