def convert_bytes_to_int(input :bytes, offset :int, size :int, type :str):
    word = input[offset:offset+size]
    value = 0
    # for i in word:
    #     print(hex(i))
    if type == "le":
        for i in range(len(word)):
            value += word[i]*(256**i)
    elif type == "be":
        for i in range(len(word)):
            value += word[i]*(256**(size-i-1))
    return value

def convert_bytes_to_str(input :bytes, offset :int, size :int):
    word = input[offset:offset+size]
    value = ""
    # for i in word:
    #     print(hex(i))
    value += str(word)
    return value

def convert_bytes_to_bytes(input :bytes, offset :int, size :int):
    word = input[offset:offset+size]
    value = word
    return value

def MBR_EBR_partition_type_int_to_str(partition_type: int):
    result = ""
    match partition_type:
        case 5:
            result = "Extended CHS"
        case 6:
            result = "FAT16"
        case 7:
            result = "exFAT"
        case 11:
            result = "FAT32"
        case 15:
            result = "Extended LBA"
        case 34:
            result = "Reserved"
        case 131:
            result = "ext"
        case 198:
            result = "FAT16 again"
        case _:
            result = "undefined"
    return result