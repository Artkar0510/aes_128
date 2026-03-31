BLOCK_SIZE = 16

S_BOX = [
0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16
]

INV_S_BOX = [S_BOX.index(x) for x in range(256)]

RCON = [0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1B,0x36]

def sub_bytes(state):
    return [S_BOX[b] for b in state]

def inv_sub_bytes(state):
    return [INV_S_BOX[b] for b in state]

def shift_rows(state):
    return [
        state[0], state[5], state[10], state[15],
        state[4], state[9], state[14], state[3],
        state[8], state[13], state[2], state[7],
        state[12], state[1], state[6], state[11]
    ]

def inv_shift_rows(state):
    return [
        state[0], state[13], state[10], state[7],
        state[4], state[1], state[14], state[11],
        state[8], state[5], state[2], state[15],
        state[12], state[9], state[6], state[3]
    ]

def gmul(a, b):
    p = 0
    for _ in range(8):
        if b & 1:
            p ^= a
        hi = a & 0x80
        a = (a << 1) & 0xFF
        if hi:
            a ^= 0x1b
        b >>= 1
    return p

def mix_columns(state):
    res = []
    for i in range(4):
        col = state[i*4:(i+1)*4]
        res.extend([
            gmul(col[0],2)^gmul(col[1],3)^col[2]^col[3],
            col[0]^gmul(col[1],2)^gmul(col[2],3)^col[3],
            col[0]^col[1]^gmul(col[2],2)^gmul(col[3],3),
            gmul(col[0],3)^col[1]^col[2]^gmul(col[3],2)
        ])
    return res

def inv_mix_columns(state):
    res = []
    for i in range(4):
        col = state[i*4:(i+1)*4]
        res.extend([
            gmul(col[0],14)^gmul(col[1],11)^gmul(col[2],13)^gmul(col[3],9),
            gmul(col[0],9)^gmul(col[1],14)^gmul(col[2],11)^gmul(col[3],13),
            gmul(col[0],13)^gmul(col[1],9)^gmul(col[2],14)^gmul(col[3],11),
            gmul(col[0],11)^gmul(col[1],13)^gmul(col[2],9)^gmul(col[3],14)
        ])
    return res

def add_round_key(state, key):
    return [s ^ k for s, k in zip(state, key)]

def key_expansion(key):
    expanded = list(key)
    i = 16
    rcon_iter = 0

    while len(expanded) < 176:
        temp = expanded[-4:]

        if i % 16 == 0:
            temp = temp[1:] + temp[:1]
            temp = [S_BOX[b] for b in temp]
            temp[0] ^= RCON[rcon_iter]
            rcon_iter += 1

        for j in range(4):
            expanded.append(expanded[i - 16] ^ temp[j])
            i += 1

    return expanded

def encrypt_block(block, expanded_key):
    state = add_round_key(block, expanded_key[:16])

    for i in range(1, 10):
        state = sub_bytes(state)
        state = shift_rows(state)
        state = mix_columns(state)
        state = add_round_key(state, expanded_key[i*16:(i+1)*16])

    state = sub_bytes(state)
    state = shift_rows(state)
    state = add_round_key(state, expanded_key[160:176])

    return state

def decrypt_block(block, expanded_key):
    state = add_round_key(block, expanded_key[160:176])

    for i in range(9, 0, -1):
        state = inv_shift_rows(state)
        state = inv_sub_bytes(state)
        state = add_round_key(state, expanded_key[i*16:(i+1)*16])
        state = inv_mix_columns(state)

    state = inv_shift_rows(state)
    state = inv_sub_bytes(state)
    state = add_round_key(state, expanded_key[:16])

    return state

def pad(data):
    pad_len = BLOCK_SIZE - len(data) % BLOCK_SIZE
    return data + bytes([pad_len]*pad_len)

def unpad(data):
    return data[:-data[-1]]

def process_file(input_file, output_file, key, mode):
    with open(input_file, "rb") as f:
        data = f.read()

    if mode == "encrypt":
        data = pad(data)

    expanded_key = key_expansion(key)
    result = []

    for i in range(0, len(data), 16):
        block = list(data[i:i+16])

        if mode == "encrypt":
            processed = encrypt_block(block, expanded_key)
        else:
            processed = decrypt_block(block, expanded_key)

        result.extend(processed)

    result = bytes(result)

    if mode == "decrypt":
        result = unpad(result)

    with open(output_file, "wb") as f:
        f.write(result)

def main():
    mode = input("Enter:  encrypt / decrypt: \n")
    input_file = input("input file: ")
    output_file = input("output file: ")

    key_input = input("key (32 hex chars) (Example: 00112233445566778899aabbccddeeff): ").strip()

    key = bytes.fromhex(key_input)

    if len(key) != 16:
        raise ValueError("Key must be 16 bytes (32 hex chars)")

    key = list(key)
    process_file(input_file, output_file, key, mode)

    print("Done!")

if __name__ == "__main__":
    main()