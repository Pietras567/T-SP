import heapq
import json
import socket
import struct

class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq


def stworz_drzewo_huffmana(freq_dict):
    heap = [Node(char, freq) for char, freq in freq_dict.items()]
    heapq.heapify(heap)

    while len(heap) > 1:
        node1 = heapq.heappop(heap)
        node2 = heapq.heappop(heap)

        merged = Node(None, node1.freq + node2.freq)
        merged.left = node1
        merged.right = node2

        heapq.heappush(heap, merged)

    return heap[0]  # zwraca korzeń drzewa Huffmana



def oblicz_czestosc_znakow(nazwa_pliku):
    with open(nazwa_pliku, 'r', encoding='utf-8') as plik:
        tekst = plik.read()

    total_chars = len(tekst)
    freq_dict = {}

    for char in tekst:
        if char in freq_dict:
            freq_dict[char] += 1
        else:
            freq_dict[char] = 1

    for char, count in freq_dict.items():
        freq_dict[char] = round((count / total_chars) * 100, 2)

    return freq_dict

def wyswietl_drzewo(node, prefix=""):
    if node is None:
        return

    if node.char is not None:
        print(f'Znak: {node.char}, Częstość: {node.freq}, Kod: {prefix}')

    wyswietl_drzewo(node.left, prefix + "0")
    wyswietl_drzewo(node.right, prefix + "1")

def generuj_kody(node, current_code="", code={}):
    if node is None:
        return

    if node.char is not None:
        code[node.char] = current_code

    generuj_kody(node.left, current_code + "0", code)
    generuj_kody(node.right, current_code + "1", code)

    return code

def skompresuj_plik(nazwa_pliku_wejsciowego, nazwa_pliku_wyjsciowego, kody):
    with open(nazwa_pliku_wejsciowego, 'r', encoding='utf-8') as plik:
        tekst = plik.read()

    skompresowany_tekst = ""
    for char in tekst:
        skompresowany_tekst += kody[char]

    padding = 8 - (len(skompresowany_tekst) % 8)
    skompresowany_tekst += '0' * padding

    bity = [skompresowany_tekst[i:i + 8] for i in range(0, len(skompresowany_tekst), 8)]
    bajty = bytearray([int(bity, 2) for bity in bity])

    with open(nazwa_pliku_wyjsciowego, 'wb') as plik:
        plik.write(bytes([padding]))
        plik.write(bajty)


def dekompresuj_plik(nazwa_pliku_wejsciowego, nazwa_pliku_wyjsciowego, drzewo):
    with open(nazwa_pliku_wejsciowego, 'rb') as plik:
        padding = ord(plik.read(1))
        bajty = plik.read()

    skompresowany_tekst = ''.join([bin(bajt)[2:].zfill(8) for bajt in bajty])
    skompresowany_tekst = skompresowany_tekst[:-padding]  # Usuń dodatkowe bity

    dekompresowany_tekst = ""
    current_node = drzewo
    for bit in skompresowany_tekst:
        if bit == '0':
            current_node = current_node.left
        else:  # bit == '1'
            current_node = current_node.right

        if current_node.char is not None:
            dekompresowany_tekst += current_node.char
            current_node = drzewo

    with open(nazwa_pliku_wyjsciowego, 'w', encoding='utf-8') as plik:
        plik.write(dekompresowany_tekst)

def serializuj_drzewo(node):
    if node is None:
        return None

    serialized_node = {
        'char': node.char,
        'freq': node.freq,
        'left': serializuj_drzewo(node.left),
        'right': serializuj_drzewo(node.right)
    }

    return serialized_node

def deserializuj_drzewo(serialized_node):
    if serialized_node is None:
        return None

    node = Node(serialized_node['char'], serialized_node['freq'])
    node.left = deserializuj_drzewo(serialized_node['left'])
    node.right = deserializuj_drzewo(serialized_node['right'])

    return node

def zapisz_drzewo(nazwa_pliku, drzewo):
    with open(nazwa_pliku, 'w') as plik:
        json.dump(serializuj_drzewo(drzewo), plik)

def wczytaj_drzewo(nazwa_pliku):
    with open(nazwa_pliku, 'r') as plik:
        serialized_tree = json.load(plik)

    return deserializuj_drzewo(serialized_tree)



def send_files(filenames, server_ip, server_port):
    s = socket.socket()
    s.connect((server_ip, server_port))
    for filename in filenames:
        with open(filename, 'rb') as f:
            data = f.read()
            # Wysyłanie rozmiaru pliku przed danymi
            s.sendall(struct.pack('<I', len(data)))
            s.sendall(data)
    s.close()

def receive_files(filenames, server_port):
    s = socket.socket()
    s.bind(('', server_port))
    s.listen(5)
    c, addr = s.accept()
    file_index = 0
    while True:
        # Odbieranie rozmiaru pliku
        file_size_data = b''
        while len(file_size_data) < 4:
            more_data = c.recv(4 - len(file_size_data))
            if not more_data:
                break
            file_size_data += more_data
        if not file_size_data:
            break
        file_size = struct.unpack('<I', file_size_data)[0]
        file_data = c.recv(file_size)
        with open(filenames[file_index], 'wb') as f:
            f.write(file_data)
        file_index += 1
    c.close()



work_mode = input("Podaj tryb pracy (o dla odbiornika/n dla nadajnika): ").lower()
if work_mode == 'o':
    no_port = int(input("Podaj numer portu: "))


    # Dekompresja
    print("Dekompresja")
    receive_files(['drzewo_rec.json', 'hof_rec.bin'], no_port)
    drzewo = wczytaj_drzewo('drzewo_rec.json')
    wyswietl_drzewo(drzewo)
    dekompresuj_plik('hof_rec.bin', 'decompressed.txt', drzewo)


elif work_mode == 'n':
    file = str(input("Podaj nazwę plik do kompresji: "))
    no_port = int(input("Podaj numer portu: "))
    ip_addr = str(input("Podaj adres docelowy: "))

    # Użycie początkowych funkcji
    print("Generacja kodów")
    czestosc_znakow = oblicz_czestosc_znakow(file)
    drzewo_huffmana = stworz_drzewo_huffmana(czestosc_znakow)
    zapisz_drzewo('drzewo.json', drzewo_huffmana)
    wyswietl_drzewo(drzewo_huffmana)

    # Kompresja
    print("Kompresja")
    kody = generuj_kody(drzewo_huffmana)
    skompresuj_plik(file, 'output.bin', kody)

    send_files(['drzewo.json', 'output.bin'], ip_addr, no_port)





