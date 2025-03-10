"""
Autorzy:
    - Piotr Janiszek 247678
    - Aliaksei Vishniavetski 249518
"""

import time
import serial

# Funkcja do obliczania sumy kontrolnej
def calculate_checksum(data):
    print(len(data))
    print(data)
    checksum = 0
    for byte in data:
        checksum = (checksum + byte) & 0xFF
    return checksum


# Funkcja do obliczania CRC
def calculate_crc(data):
    print(len(data))
    print(data)
    crc = 0xFFFF
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
    return crc & 0xFFFF



# Funkcja do wysyłania danych za pomocą protokołu XMODEM
def send_data(ser, filename):
    try:
        with open(filename, 'rb') as file:
            while True:
                isFree = ser.read(1)
                # Oczekiwanie na wolny port
                if isFree == b'\x15':
                    checksum = True
                    print("Przesyłanie danych...")
                    break
                if isFree == b'\x43':
                    checksum = False
                    print("Przesyłanie danych...")
                    break

            data = file.read()
            total_bytes = len(data)
            block_number = 1
            # Wysyłanie danych
            i = 0
            while i < total_bytes:
                print("i: "+str(i))
                packet_data = data[i:i+128]
                # Uzupełnienie danych do wielkości pakietu
                if len(packet_data) < 128:
                    packet_data += b'\x1A' * (128 - len(packet_data))  # Użycie znaku SUB (0x1A w ASCII) dla wypełnienia do pełnego bloku
                # Nagłówek
                header = bytes([0x01, block_number, 255 - block_number])
                if checksum:
                    checksum_value = calculate_checksum(packet_data)
                    packet = header + packet_data + bytes([checksum_value])
                else:
                    crc_value = calculate_crc(packet_data)
                    packet = header + packet_data + bytes([(crc_value >> 8) & 0xFF, crc_value & 0xFF])

                ser.reset_input_buffer()
                ser.write(packet)
                start_time = time.time()  # rozpoczęcie liczenia czasu
                needToSend = False
                while True:
                    if ser.in_waiting > 0:
                        answer = ser.read(1)
                        if (answer == b'\x15'):
                            print("NAK, POWTARZAMY")
                            needToSend = True
                            break
                        elif (answer == b'\x06'):
                            print("ACK")
                            break
                        elif (answer == b'\x18'):
                            print("Odbiorca zakończył połączenie")
                            return
                    else:
                        if time.time() - start_time > 60:  # sprawdzenie, czy minęło 60 sekund
                            print("Czas minął. Ponowne wysyłanie pakietu.")
                            needToSend = True
                            break  # zakończenie pętli
                        time.sleep(0.1)
                        continue
                if needToSend:
                    continue
                i+=128
                block_number = block_number + 1  # Zwiększenie numeru bloku, z użyciem modulo 256
                if block_number == 256:
                    block_number = 1
        # Wysyłanie końca transmisji EOT
        ser.write(b'\x04')
        start_time = time.time()  # rozpoczęcie liczenia czasu
        while True:
            if ser.in_waiting > 0:
                answer = ser.read(1)
                if (answer == b'\x06'):
                    print("ACK, Kończymy transmisję")
                    break
            else:
                if time.time() - start_time > 60:  # sprawdzenie, czy minęło 60 sekund
                    print("Czas minął. Siłowo kończymy połączenie.")
                    ser.write(b'\x18')
                    break  # zakończenie pętli
        print("Dane zostały pomyślnie wysłane.")


    except FileNotFoundError:
        print("Plik nie został znaleziony.")


# Funkcja do odbierania danych za pomocą protokołu XMODEM
def receive_data(ser, filename, checksum=True):
    start = True
    try:
        with open(filename, 'wb') as file:
            if checksum:
                while start == True:
                    # Oczekiwanie na pierwszy nagłówek
                    if ser.in_waiting > 0:
                        header = ser.read(3)
                        if header == b'\x01\x01\xfe':
                            print("Odbieranie danych...")
                            ser.reset_output_buffer()
                            break
                    else:
                        ser.write(b'\x15')
                        time.sleep(10)
            else:
                while start == True:
                    # Oczekiwanie na pierwszy nagłówek
                    if ser.in_waiting > 0:
                        header = ser.read(3)
                        if header == b'\x01\x01\xfe':
                            print("Odbieranie danych...")
                            ser.reset_output_buffer()
                            break
                    else:
                        ser.write(b'\x43')
                        time.sleep(10)

            # Odbieranie danych
            while True:
                if(start==True):
                    start = False
                elif(start==False):
                    while True:
                        if ser.in_waiting > 0:
                            header = ser.read(3)
                            print(header)
                            break
                        else:
                            time.sleep(0.1)
                            continue
                if(header[0].to_bytes() == b'\x04'):
                    print("Natrafiono na EOT")
                    ser.write(b'\x06') # ACK
                    break
                if (header[0].to_bytes() == b'\x18'):
                    print("Natrafiono na CAN, kończymy połączenie")
                    break

                newPacket = False
                #print(header[0].to_bytes())
                #print(b'\x01')
                if (header[0].to_bytes() != b'\x01'):
                    ser.reset_input_buffer()
                    print("Brak znacznika początku nagłówka. Wymagana retransmisja pakietu.")
                    ser.write(b'\x15')  # NAK
                    start_time = time.time()  # rozpoczęcie liczenia czasu
                    while True:
                        if ser.in_waiting > 0:
                            newPacket = True
                            break
                        else:
                            if time.time() - start_time > 10:
                                print("Brak znacznika początku nagłówka. Wymagana retransmisja pakietu.")
                                ser.write(b'\x15')  # NAK
                                start_time = time.time()  # rozpoczęcie liczenia czasu
                            time.sleep(0.1)
                if newPacket:
                    continue

                if checksum:
                    packet = ser.read(129)  # 128 bytes danych + 1 bajt sumy kontrolnej/CRC + 3 bajty na nagłówek pobrany wcześniej
                    data = packet[:-1]  # Usunięcie sumy kontrolnej

                    received_checksum = packet[-1]
                    calculated_checksum = calculate_checksum(data)
                    print("Otrzymany checksum: " + str(received_checksum))
                    print("Obliczony checksum: " + str(calculated_checksum))
                    #print(header)
                    if(header[2] != 255 - header[1]):
                        print("Błąd dopełnienia. Ponowna transmisja pakietu.")
                        ser.write(b'\x15')  # NAK
                        start_time = time.time()  # rozpoczęcie liczenia czasu
                        while True:
                            if ser.in_waiting > 0:
                                break
                            else:
                                if time.time() - start_time > 10:
                                    print("Błąd dopełnienia. Ponowna transmisja pakietu.")
                                    ser.write(b'\x15')  # NAK
                                    start_time = time.time()  # rozpoczęcie liczenia czasu
                                time.sleep(0.1)

                    if received_checksum == calculated_checksum:
                        # Usuwanie wszystkich znaków b'\x1A' od końca aż do napotkania innego znaku
                        #data = data.rstrip(b'\x1A')
                        file.write(data)
                        ser.write(b'\x06')  # ACK
                        start_time = time.time()  # rozpoczęcie liczenia czasu
                        while True:
                            if ser.in_waiting > 0:
                                break
                            else:
                                if time.time() - start_time > 10:
                                    print("Ponowna transmisja ACK.")
                                    ser.write(b'\x06')  # ACK
                                    start_time = time.time()  # rozpoczęcie liczenia czasu
                                time.sleep(0.1)
                    else:
                        print("Błąd sumy kontrolnej. Ponowna transmisja pakietu.")
                        ser.write(b'\x15')  # NAK
                        start_time = time.time()  # rozpoczęcie liczenia czasu
                        while True:
                            if ser.in_waiting > 0:
                                break
                            else:
                                if time.time() - start_time > 10:
                                    print("Błąd sumy kontrolnej. Ponowna transmisja pakietu.")
                                    ser.write(b'\x15')  # NAK
                                    start_time = time.time()  # rozpoczęcie liczenia czasu
                                time.sleep(0.1)
                else:
                    packet = ser.read(130)  # 128 bytes danych + 2 bajty sumy CRC + 3 bajty na nagłówek pobrany wcześniej
                    data = packet[:-2]  # Usunięcie CRC

                    received_crc = int.from_bytes(packet[-2:], byteorder='big')
                    calculated_crc = calculate_crc(data)
                    print("Otrzymany crc: " + str(received_crc))
                    print("Obliczony crc: " + str(calculated_crc))

                    if (header[2] != 255 - header[1]):
                        print("Błąd dopełnienia. Ponowna transmisja pakietu.")
                        ser.write(b'\x15')  # NAK
                        start_time = time.time()  # rozpoczęcie liczenia czasu
                        while True:
                            if ser.in_waiting > 0:
                                break
                            else:
                                if time.time() - start_time > 10:
                                    print("Błąd dopełnienia. Ponowna transmisja pakietu.")
                                    ser.write(b'\x15')  # NAK
                                    start_time = time.time()  # rozpoczęcie liczenia czasu
                                time.sleep(0.1)

                    if received_crc == calculated_crc:
                        # Usuwanie wszystkich znaków b'\x1A' od końca aż do napotkania innego znaku
                        #data = data.rstrip(b'\x1A')
                        file.write(data)
                        ser.write(b'\x06')  # ACK
                        start_time = time.time()  # rozpoczęcie liczenia czasu
                        while True:
                            if ser.in_waiting > 0:
                                break
                            else:
                                if time.time() - start_time > 10:
                                    print("Ponowna transmisja ACK.")
                                    ser.write(b'\x06')  # ACK
                                    start_time = time.time()  # rozpoczęcie liczenia czasu
                                time.sleep(0.1)
                    else:
                        print("Błąd CRC. Ponowna transmisja pakietu.")
                        ser.write(b'\x15')  # NAK
                        start_time = time.time()  # rozpoczęcie liczenia czasu
                        while True:
                            if ser.in_waiting > 0:
                                break
                            else:
                                if time.time() - start_time > 10:
                                    print("Błąd CRC. Ponowna transmisja pakietu.")
                                    ser.write(b'\x15')  # NAK
                                    start_time = time.time()  # rozpoczęcie liczenia czasu
                                time.sleep(0.1)

        with open(filename, 'rb') as f:
            data = f.read()
        if len(data) > 128:
            # Rozdziel dane na pierwszą część i ostatnie 128 bajtów
            last_128_bytes = data[-128:]  # Ostatnie 128 bajtów
            first_part = data[:-128]  # Wszystko oprócz ostatnich 128 bajtów

            last_128_bytes = last_128_bytes.rstrip(b'\x1A')
            with open(filename, 'wb') as f:
                # Zapisz pierwszą część danych
                f.write(first_part)

                # Zapisz ostatnie 128 bajtów
                f.write(last_128_bytes)
                #print("test")
                #print(first_part)
                #print(len(first_part))
                #print(last_128_bytes)
                #print(len(last_128_bytes))
        else:
            bytes = data
            bytes = bytes.rstrip(b'\x1A')
            with open(filename, 'wb') as f:
                f.write(bytes)
    except IOError:
        print("Błąd podczas zapisu pliku.")
        ser.write(b'\x18') # CAN



if __name__ == "__main__":
    # Pobranie danych od użytkownika
    port = input("Podaj nazwę portu COM (np. COM1): ")
    operation = input("Wybierz operację (W - wysyłanie, O - odbieranie): ").upper()

    # Ustanowienie połączenia szeregowego
    try:
        ser = serial.Serial(port)
        ser.timeout = 1
        print("Połączenie z portem {} zostało ustanowione.".format(port))

        if operation == 'W':
            filename = input("Podaj nazwę pliku do wysłania: ")
            #checksum_option = input("Czy chcesz użyć sumy kontrolnej? (T/N): ").upper()
            #checksum = True if checksum_option == 'T' else False
            send_data(ser, filename)
        elif operation == 'O':
            filename = input("Podaj nazwę pliku do odebrania: ")
            checksum_option = input("Czy otrzymane dane zawierają sumę kontrolną? Czy CRC? (1 dla Sumy Kontrolnej/2 dla CRC): ").upper()
            checksum = True if checksum_option == '1' else False
            receive_data(ser, filename, checksum)
        else:
            print("Nieprawidłowa operacja.")

        ser.close()
    except serial.SerialException:
        print("Nie można nawiązać połączenia z portem {}.".format(port))
