import argparse
from utils import *
from exFAT_reader import *
from FAT16_reader import *
from FAT32_reader import *

class EBR_entry:
    partition_entry: bytes
    # content: bytes

    drive_attributes: int
    CHS_address_of_partition_start: int
    partition_type: int
    partition_type_str: str
    CHS_address_of_last_partition_sector: int
    LBA_of_partition_start: int
    number_of_sectors_in_partition: int

    partition_type_whitelist: list[str]
    has_a_partition: bool

    def __init__(self, partition_entry: bytes, filesystem):
        self.filesystem = filesystem
        self.partition_entry = partition_entry
        self.partition_type_whitelist = filesystem.partition_type_whitelist
        self.partition_type_str = None
        self.has_a_partition = False

        # self.content = self.filesystem.get_partition_entry(self.entry_value)
    
    def check_if_exist(self):
        if convert_bytes_to_int(self.partition_entry, 8, 4, "le") != 0:
            return True
        else:
            return False
        # pass
    
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

        self.drive_attributes = convert_bytes_to_int(self.partition_entry, 0, 1, "le")
        self.CHS_address_of_partition_start = convert_bytes_to_int(self.partition_entry, 1, 3, "le")
        self.partition_type = convert_bytes_to_int(self.partition_entry, 4, 1, "le")
        self.CHS_address_of_last_partition_sector = convert_bytes_to_int(self.partition_entry, 5, 3, "le")
        self.LBA_of_partition_start = convert_bytes_to_int(self.partition_entry, 8, 4, "le")
        self.number_of_sectors_in_partition = convert_bytes_to_int(self.partition_entry, 12, 4, "le")

        self.partition_type_str = MBR_EBR_partition_type_int_to_str(self.partition_type)
        
        if self.partition_type_str == "Extended CHS" or self.partition_type_str == "Extended LBA":
            self.partition = EBR(self.filesystem.input_path, self.filesystem.ebr_offset + self.LBA_of_partition_start, self.filesystem.ebr_offset, self.partition_type_whitelist)
            self.has_a_partition = True
            self.partition.analyse_header()
            self.LBA_of_partition_start += self.filesystem.ebr_offset
            # print(len(self.filesystem.elements))
            # self.filesystem.elements += self.partition.elements
            # print(len(self.filesystem.elements))
            # self.partition.display_header_data()
        else:
            self.LBA_of_partition_start += self.filesystem.gen_offset

        if self.partition_type_str == "HPFS/NTFS/exFAT":
            jump_code = bytes()
            with open(self.filesystem.input_path, "rb") as f:
                f.seek(self.LBA_of_partition_start*512, 0)
                jump_code = convert_bytes_to_bytes(f.read(512), 0, 3)
            
            if jump_code == bytes([0xeb, 0x76, 0x90]):
                self.partition = exFAT(self.filesystem.input_path, self.LBA_of_partition_start*512)
                self.has_a_partition = True
                self.partition.analyse_boot_sector()
        elif self.partition_type_str == "FAT16":
            self.partition = FAT16(self.filesystem.input_path, self.LBA_of_partition_start*512)
            self.has_a_partition = True
            self.partition.analyse_boot_sector()
        elif self.partition_type_str == "FAT32":
            self.partition = FAT32(self.filesystem.input_path, self.LBA_of_partition_start*512)
            self.has_a_partition = True
            self.partition.analyse_boot_sector()
    
    def get_self_data(self):
        # return f"{self.partition_name} : {self.first_LBA} : {self.last_LBA}\n"
        pass

    def is_readable(self):
        if self.partition_type_str in self.partition_type_whitelist and self.has_a_partition:
            return True
        else:
            return False
    
    def display_self_data(self):
        # print(self.get_self_data(), end="")
        # pass
        # print(f"Drive attributes : {self.drive_attributes}")
        # print(f"CHS address of partition start : {self.CHS_address_of_partition_start}")
        # print(f"Partition type : {self.partition_type} : {self.partition_type_str}")
        # print(f"CHS address of last partition sector : {self.CHS_address_of_last_partition_sector}")
        # print(f"LBA of partition start : {self.LBA_of_partition_start}")
        # print(f"Number of sectors in partition : {self.number_of_sectors_in_partition}")
        print(f"{self.partition_type} : {self.partition_type_str} : {hex(self.LBA_of_partition_start*512)} : {self.LBA_of_partition_start} : {self.number_of_sectors_in_partition} : {self.is_readable()}")

class EBR:
    input_path: str
    gen_offset: int
    ebr_offset: int

    EBR_bootstrap: bytes
    first_partition_entry: bytes
    second_partition_entry: bytes
    third_partition_entry: bytes
    fourth_partition_entry: bytes
    valid_bootsector: bytes

    elements: list[EBR_entry]

    partition_type_whitelist: list[str]

    def __init__(self, file_path: str, gen_offset: int, ebr_offset: int, partition_type_whitelist):
        self.input_path = file_path
        self.gen_offset = gen_offset
        self.ebr_offset = ebr_offset
        self.elements = []
        self.partition_type_whitelist = partition_type_whitelist
    
    def analyse_header(self):
        boot_sector = None
        with open(self.input_path, "br") as f:
            f.seek(self.gen_offset*512, 0)
            boot_sector = f.read(512)
        
        self.EBR_bootstrap = convert_bytes_to_bytes(boot_sector, 0, 446)
        self.first_partition_entry = convert_bytes_to_bytes(boot_sector, 446, 16)
        self.second_partition_entry = convert_bytes_to_bytes(boot_sector, 462, 16)
        self.third_partition_entry = convert_bytes_to_bytes(boot_sector, 478, 16)
        self.fourth_partition_entry = convert_bytes_to_bytes(boot_sector, 494, 16)
        self.valid_bootsector = convert_bytes_to_bytes(boot_sector, 510, 2)

        partition_entry = EBR_entry(self.first_partition_entry, self)
        self.elements.append(partition_entry)
        partition_entry.process_data()
        # if not(partition_entry.check_if_exist()):
        #     # self.elements.append(partition_entry)
        #     self.elements.pop(-1)
        partition_entry = EBR_entry(self.second_partition_entry, self)
        self.elements.append(partition_entry)
        partition_entry.process_data()
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
            if element.partition_type_str != "undefined":
                # new_elements.append(element)
                if element.partition_type_str == "Extended LBA" or element.partition_type_str == "Extended CHS":
                    new_elements += element.partition.flatten_elements()
                else:
                    new_elements.append(element)
        # print(new_elements)
        return new_elements

    def display_header_data(self):
        print(f"EBR bootstrap : {self.EBR_bootstrap}")
        print(f"Offset : {self.gen_offset}")
        print(f"First partition entry : {self.first_partition_entry}")
        print(f"Second partition entry : {self.second_partition_entry}")
        print(f"Third partition entry : {self.third_partition_entry}")
        print(f"Fourth partition entry : {self.fourth_partition_entry}")
        print(f"Valid bootsector : {self.valid_bootsector}")

        print()
        for i in range(len(self.elements)):
            # print(i)
            self.elements[i].display_self_data()
            # print()
    
    def get_partition_entry(self, entry_value: int):
        pass

# if __name__=="__main__":
#     parser = argparse.ArgumentParser(prog="fs_reader",
#                                      description="read a GPT file system")
    
#     subparser1 = parser.add_subparsers(dest="action")

#     parser1 = subparser1.add_parser("analyse")
#     parser1.add_argument("-i", "--input", action="store", required=True, help="input iso file")

#     # parser1 = subparser1.add_parser("tree")
#     # parser1.add_argument("-i", "--input", action="store", required=True, help="input iso file")

#     # parser1 = subparser1.add_parser("export")
#     # parser1.add_argument("-i", "--input", action="store", required=True, help="input iso file")
#     # parser1.add_argument("-p", "--path", action="store", required=True, help="input iso file")
#     # parser1.add_argument("-o", "--output", action="store", required=True, help="output file")

#     args = parser.parse_args()

#     if args.action == "analyse":
#         # read_fs(args.input)
#         filesystem = EBR(args.input)
#         filesystem.analyse_header()
#         filesystem.display_header_data()
#     # elif args.action == "tree":
#     #     # read_fs(args.input)
#     #     filesystem = EBR(args.input)
#     #     filesystem.analyse_header()
#     #     # partition.root_dir.display_self_data()
#     #     # partition.root_dir.display_tree_data(1)
#     #     for partition in filesystem.elements:
#     #         partition.partition.root_dir.display_self_data()
#     #         partition.partition.root_dir.display_tree_data(1)
#     # elif args.action == "export":
#     #     # read_fs(args.input)
#     #     filesystem = EBR(args.input)
#     #     filesystem.analyse_header()
#     #     # content = partition.get_filesystem_entry_content(args.path)
#     #     for partition in filesystem.elements:
#     #         content = partition.partition.get_filesystem_entry_content(args.path)
#     #         if content != None:
#     #             break
#     #     if content != None:
#     #         if isinstance(content, str):
#     #             content = content.encode(encoding="utf-8")
#     #         with open(args.output, "bw") as f:
#     #             f.write(content)
#     #     else:
#     #         print("Path doesn't exist")