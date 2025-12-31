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
    value += word.decode(encoding="utf-8")
    value = value.replace(bytes([0, ]).decode(encoding="utf-8"), '')
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
            result = "HPFS/NTFS/exFAT"
        case 11:
            result = "FAT32"
        case 15:
            result = "Extended LBA"
        case 131:
            result = "Linux"
        case _:
            result = "undefined"
    return result

def guess_fs_from_sector(input: bytes):
    signature = convert_bytes_to_int(input, 510, 2, "le")
    if signature == 0xaa55: # FAT-like filesystem
        if convert_bytes_to_str(input, 3, 8).replace(" ", "") == "EXFAT":
            return "exFAT"
        if convert_bytes_to_str(input, 3, 8).replace(" ", "") == "NTFS":
            return "NTFS"
        
        BPB_SecPerClus = convert_bytes_to_int(input, 13, 1, "le")
        totsec16 = convert_bytes_to_int(input, 19, 2, "le")
        totsec32 = convert_bytes_to_int(input, 32, 4, "le")
        BPB_TotSec = totsec16 if totsec16 > 0 else totsec32
        BPB_BytsPerSec = convert_bytes_to_int(input, 11, 2, "le")
        BPB_RootEntCnt = convert_bytes_to_int(input, 17, 2, "le")
        fatsz16 = convert_bytes_to_int(input, 22, 2, "le")
        fatsz32 = convert_bytes_to_int(input, 36, 4, "le")
        BPB_FATSz = fatsz16 if fatsz16 > 0 else fatsz32
        BPB_NumFATs = convert_bytes_to_int(input, 16, 1, "le")
        BPB_ResvdSecCnt = convert_bytes_to_int(input, 14, 2, "le")


        FatStartSector = BPB_ResvdSecCnt
        FatSectors = BPB_FATSz * BPB_NumFATs
        RootDirStartSector = FatStartSector + FatSectors
        RootDirSectors = (32 * BPB_RootEntCnt + BPB_BytsPerSec - 1) / BPB_BytsPerSec
        DataStartSector = RootDirStartSector + RootDirSectors
        DataSectors = BPB_TotSec - DataStartSector
        CountofClusters = DataSectors / BPB_SecPerClus

        if CountofClusters <= 4085:
            return "FAT12"
        elif CountofClusters <= 65525:
            return "FAT16"
        else:
            return "FAT32"
    else:
        return "undefined"