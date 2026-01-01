from partition_system import *
from MBR import *

class EBR:
    pass

class EBR_entry(MBR_entry):
    # type_int: int

    # drive_attributes: int
    # # CHS_address_of_partition_start: int
    # # CHS_address_of_last_partition_sector: int
    # # LBA_of_partition_start: int
    # # number_of_sectors_in_partition: int

    # partition_type_whitelist: list[str]
    # # has_a_partition: bool

    # def __init__(self, filesystem: MBR, entry_value: int):
    #     super().__init__(filesystem, entry_value)
    #     self.partition_type_whitelist = filesystem.partition_type_whitelist
    #     self.type_int = 0
    #     self.drive_attributes = 0

    #     self.content = self.parent_filesystem.get_partition_entry(self.entry_value)

    #     self.process_data()
    
    # def check_if_exist(self):
    #     if convert_bytes_to_int(self.content, 8, 4, "le") != 0:
    #         return True
    #     else:
    #         return False
    #     # pass
    
    def process_data(self):
        # self.partition_type_GUID = convert_bytes_to_bytes(self.content, 0, 16)
        # self.unique_partition_GUID = convert_bytes_to_bytes(self.content, 16, 16)
        # self.first_LBA = convert_bytes_to_int(self.content, 32, 8, "le")
        # self.last_LBA = convert_bytes_to_int(self.content, 40, 8, "le")
        # self.attribute_flags = convert_bytes_to_int(self.content, 48, 8, "le")
        # self.partition_name = convert_bytes_to_bytes(self.content, 56, 72).decode(encoding="utf-16")

        # self.partition = exFAT(self.filesystem.input_path, self.first_LBA*512)
        # self.partition.analyse_boot_sector()
        # pass

        self.drive_attributes = convert_bytes_to_int(self.content, 0, 1, "le")
        # self.CHS_address_of_partition_start = convert_bytes_to_int(self.content, 1, 3, "le")
        self.type_int = convert_bytes_to_int(self.content, 4, 1, "le")
        # self.CHS_address_of_last_partition_sector = convert_bytes_to_int(self.content, 5, 3, "le")
        self.start = convert_bytes_to_int(self.content, 8, 4, "le")
        self.length = convert_bytes_to_int(self.content, 12, 4, "le")

        self.type = MBR_EBR_partition_type_int_to_str(self.type_int)
        
        self.element = None
        if self.type == "Extended CHS" or self.type == "Extended LBA":
            self.element = EBR(self.parent_filesystem.input_path, self.partition_type_whitelist, self.parent_filesystem.ebr_offset + self.start, self.parent_filesystem.ebr_offset)
            # self.has_a_partition = True
            # self.partition.analyse_boot_sector()
            self.start += self.parent_filesystem.ebr_offset
            # print(len(self.filesystem.elements))
            # self.filesystem.elements += self.partition.elements
            # print(len(self.filesystem.elements))
            # self.partition.display_header_data()
        else:
            self.start += self.parent_filesystem.offset

        # elif self.partition_type_str == "HPFS/NTFS/exFAT":
        #     jump_code = bytes()
        #     with open(self.filesystem.input_path, "rb") as f:
        #         f.seek(self.LBA_of_partition_start*512, 0)
        #         jump_code = convert_bytes_to_bytes(f.read(512), 0, 3)
            
        #     if jump_code == bytes([0xeb, 0x76, 0x90]):
        #         self.partition = exFAT(self.filesystem.input_path, self.LBA_of_partition_start*512)
        #         self.has_a_partition = True
        #         self.partition.analyse_boot_sector()
        # elif self.partition_type_str == "FAT16":
        #     self.partition = FAT16(self.filesystem.input_path, self.LBA_of_partition_start*512)
        #     self.has_a_partition = True
        #     self.partition.analyse_boot_sector()
        # elif self.partition_type_str == "FAT32":
        #     self.partition = FAT32(self.filesystem.input_path, self.LBA_of_partition_start*512)
        #     self.has_a_partition = True
        #     self.partition.analyse_boot_sector()
    
    # def get_self_data(self):
    #     # return f"{self.partition_name} : {self.first_LBA} : {self.last_LBA}\n"
    #     pass

    # def is_readable(self):
    #     if self.type in self.partition_type_whitelist and self.element != None:
    #         return True
    #     else:
    #         return False
    
    # def display_self_data(self):
    #     # print(self.get_self_data(), end="")
    #     # pass
    #     # print(f"Drive attributes : {self.drive_attributes}")
    #     # print(f"CHS address of partition start : {self.CHS_address_of_partition_start}")
    #     # print(f"Partition type : {self.partition_type} : {self.partition_type_str}")
    #     # print(f"CHS address of last partition sector : {self.CHS_address_of_last_partition_sector}")
    #     # print(f"LBA of partition start : {self.LBA_of_partition_start}")
    #     # print(f"Number of sectors in partition : {self.number_of_sectors_in_partition}")
    #     print(f"{self.partition_type} : {self.partition_type_str} : {hex(self.LBA_of_partition_start*512)} : {self.LBA_of_partition_start} : {self.number_of_sectors_in_partition} : {self.is_readable()}")

class EBR(MBR):
    ebr_offset: int

    # MBR_bootstrap: bytes
    # unique_disk_id: bytes
    # reserved: bytes
    # first_partition_entry: bytes
    # second_partition_entry: bytes
    # third_partition_entry: bytes
    # fourth_partition_entry: bytes
    # valid_bootsector: bytes

    # # elements: list[MBR_entry]

    # partition_type_whitelist: list[str]

    def __init__(self, file_path: str, partition_type_whitelist: list[str], offset: int = 0, ebr_offset: int = 0):
        self.ebr_offset = ebr_offset
        super().__init__(file_path, partition_type_whitelist, offset)

        # self.analyse_boot_sector()
    
    def analyse_boot_sector(self):
        boot_sector = None
        with open(self.input_path, "br") as f:
            f.seek(self.offset*self.bytes_per_sector, 0)
            boot_sector = f.read(512)
        
        self.EBR_bootstrap = convert_bytes_to_bytes(boot_sector, 0, 446)
        self.first_partition_entry = convert_bytes_to_bytes(boot_sector, 446, 16)
        self.second_partition_entry = convert_bytes_to_bytes(boot_sector, 462, 16)
        self.third_partition_entry = convert_bytes_to_bytes(boot_sector, 478, 16)
        self.fourth_partition_entry = convert_bytes_to_bytes(boot_sector, 494, 16)
        self.valid_bootsector = convert_bytes_to_bytes(boot_sector, 510, 2)

        partition_entry = EBR_entry(self, 1)
        self.elements.append(partition_entry)
        # partition_entry.process_data()
        # if not(partition_entry.check_if_exist()):
        #     # self.elements.append(partition_entry)
        #     self.elements.pop(-1)
        partition_entry = EBR_entry(self, 2)
        self.elements.append(partition_entry)
        # partition_entry.process_data()
        # if not(partition_entry.check_if_exist()) or partition_entry.partition_type_str == "Extended LBA" or partition_entry.partition_type_str == "Extended CHS":
        #     # self.elements.append(partition_entry)
        #     self.elements.pop(-1)
        # partition_entry = EBR_entry(self.third_partition_entry, self)
        # partition_entry.process_data()
        # if partition_entry.check_if_exist():
        #     self.elements.append(partition_entry)
        # partition_entry = EBR_entry(self.fourth_partition_entry, self)
        # partition_entry.process_data()
        # if partition_entry.check_if_exist():
        #     self.elements.append(partition_entry)
    
    def flatten_elements(self):
        new_elements = []

        for element in self.elements:
            if element.type != "undefined":
                if element.type == "Extended LBA" or element.type == "Extended CHS":
                    new_elements += element.element.flatten_elements()
                else:
                    new_elements.append(element)
        # print(new_elements)
        return new_elements

    # def display_header_data(self):
    #     print(f"MBR bootstrap : {self.MBR_bootstrap}")
    #     print(f"Unique Disk ID / Signature : {self.unique_disk_id}")
    #     print(f"Reserved : {self.reserved}")
    #     print(f"First partition entry : {self.first_partition_entry}")
    #     print(f"Second partition entry : {self.second_partition_entry}")
    #     print(f"Third partition entry : {self.third_partition_entry}")
    #     print(f"Fourth partition entry : {self.fourth_partition_entry}")
    #     print(f"Valid bootsector : {self.valid_bootsector}")

    #     print()
    #     for i in range(len(self.elements)):
    #         # print(i)
    #         self.elements[i].display_self_data()
    #         # print()
    
    # def get_partition_entry(self, entry_value: int):
    #     match entry_value:
    #         case 1:
    #             return self.first_partition_entry
    #         case 2:
    #             return self.second_partition_entry
    #         case 3:
    #             return self.third_partition_entry
    #         case 4:
    #             return self.fourth_partition_entry
    #         case _:
    #             return None

if __name__=="__main__":
    partition_whitelist = ["FAT16", "FAT32", "HPFS/NTFS/exFAT"]

    parser = argparse.ArgumentParser(prog="fs_reader",
                                     description="read a GPT file system")
    
    subparser1 = parser.add_subparsers(dest="action")

    parser1 = subparser1.add_parser("analyse")
    parser1.add_argument("-i", "--input", action="store", required=True, help="input iso file")

    parser1 = subparser1.add_parser("tree")
    parser1.add_argument("-i", "--input", action="store", required=True, help="input iso file")

    parser1 = subparser1.add_parser("export")
    parser1.add_argument("-i", "--input", action="store", required=True, help="input iso file")
    parser1.add_argument("-p", "--path", action="store", required=True, help="input iso file")
    parser1.add_argument("-o", "--output", action="store", required=True, help="output file")

    args = parser.parse_args()

    if args.action == "analyse":
        # read_fs(args.input)
        filesystem = MBR(args.input, partition_whitelist)
        # filesystem.analyse_header()
        filesystem.display_data()
    elif args.action == "tree":
        # read_fs(args.input)
        filesystem = MBR(args.input, partition_whitelist)
        # partition.root_dir.display_self_data()
        # partition.root_dir.display_tree_data(1)
        for partition in filesystem.elements:
            if partition.is_readable():
                partition.partition.root_dir.display_self_data()
                partition.partition.root_dir.display_tree_data(1)
    elif args.action == "export":
        # read_fs(args.input)
        filesystem = MBR(args.input, partition_whitelist)
        filesystem.analyse_header()
        # content = partition.get_filesystem_entry_content(args.path)
        for partition in filesystem.elements:
            if partition.is_readable():
                content = partition.partition.get_filesystem_entry_content(args.path)
                if content != None:
                    break
        if content != None:
            if isinstance(content, str):
                content = content.encode(encoding="utf-8")
            with open(args.output, "bw") as f:
                f.write(content)
        else:
            print("Path doesn't exist")