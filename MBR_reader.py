import argparse
from utils import *
from exFAT_reader import *
from EBR_reader import *

class MBR_entry:
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

    def __init__(self, partition_entry: bytes, filesystem):
        self.filesystem = filesystem
        self.partition_entry = partition_entry
        self.partition_type_whitelist = ["exFAT"]
        self.partition_type_str = None

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
            self.partition = EBR(self.filesystem.input_path, self.LBA_of_partition_start, self.LBA_of_partition_start)
            self.partition.analyse_header()
            # print(len(self.filesystem.elements))
            self.filesystem.elements += self.partition.elements
            # print(len(self.filesystem.elements))
            # self.partition.display_header_data()
    
    def get_self_data(self):
        # return f"{self.partition_name} : {self.first_LBA} : {self.last_LBA}\n"
        pass
    
    def display_self_data(self):
        # print(self.get_self_data(), end="")
        # pass
        # print(f"Drive attributes : {self.drive_attributes}")
        # print(f"CHS address of partition start : {self.CHS_address_of_partition_start}")
        # print(f"Partition type : {self.partition_type} : {self.partition_type_str}")
        # print(f"CHS address of last partition sector : {self.CHS_address_of_last_partition_sector}")
        # print(f"LBA of partition start : {self.LBA_of_partition_start}")
        # print(f"Number of sectors in partition : {self.number_of_sectors_in_partition}")
        print(f"{self.partition_type} : {self.partition_type_str} : {self.LBA_of_partition_start} : {self.number_of_sectors_in_partition}")

class MBR:
    input_path: str

    MBR_bootstrap: bytes
    unique_disk_id: bytes
    reserved: bytes
    first_partition_entry: bytes
    second_partition_entry: bytes
    third_partition_entry: bytes
    fourth_partition_entry: bytes
    valid_bootsector: bytes

    elements: list[MBR_entry]

    def __init__(self, file_path: str):
        self.input_path = file_path
        self.elements = []
    
    def analyse_header(self):
        boot_sector = None
        with open(self.input_path, "br") as f:
            boot_sector = f.read(512)
        
        self.MBR_bootstrap = convert_bytes_to_bytes(boot_sector, 0, 440)
        self.unique_disk_id = convert_bytes_to_bytes(boot_sector, 440, 4)
        self.reserved = convert_bytes_to_bytes(boot_sector, 444, 2)
        self.first_partition_entry = convert_bytes_to_bytes(boot_sector, 446, 16)
        self.second_partition_entry = convert_bytes_to_bytes(boot_sector, 462, 16)
        self.third_partition_entry = convert_bytes_to_bytes(boot_sector, 478, 16)
        self.fourth_partition_entry = convert_bytes_to_bytes(boot_sector, 494, 16)
        self.valid_bootsector = convert_bytes_to_bytes(boot_sector, 510, 2)

        partition_entry = MBR_entry(self.first_partition_entry, self)
        self.elements.append(partition_entry)
        partition_entry.process_data()
        if not(partition_entry.check_if_exist()):
            # self.elements.append(partition_entry)
            self.elements.pop(-1)
        partition_entry = MBR_entry(self.second_partition_entry, self)
        self.elements.append(partition_entry)
        partition_entry.process_data()
        if not(partition_entry.check_if_exist()):
            # self.elements.append(partition_entry)
            self.elements.pop(-1)
        partition_entry = MBR_entry(self.third_partition_entry, self)
        self.elements.append(partition_entry)
        partition_entry.process_data()
        if not(partition_entry.check_if_exist()):
            # self.elements.append(partition_entry)
            self.elements.pop(-1)
        partition_entry = MBR_entry(self.fourth_partition_entry, self)
        self.elements.append(partition_entry)
        partition_entry.process_data()
        if not(partition_entry.check_if_exist()):
            # self.elements.append(partition_entry)
            self.elements.pop(-1)

    def display_header_data(self):
        print(f"MBR bootstrap : {self.MBR_bootstrap}")
        print(f"Unique Disk ID / Signature : {self.unique_disk_id}")
        print(f"Reserved : {self.reserved}")
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

if __name__=="__main__":
    parser = argparse.ArgumentParser(prog="fs_reader",
                                     description="read a GPT file system")
    
    subparser1 = parser.add_subparsers(dest="action")

    parser1 = subparser1.add_parser("analyse")
    parser1.add_argument("-i", "--input", action="store", required=True, help="input iso file")

    # parser1 = subparser1.add_parser("tree")
    # parser1.add_argument("-i", "--input", action="store", required=True, help="input iso file")

    # parser1 = subparser1.add_parser("export")
    # parser1.add_argument("-i", "--input", action="store", required=True, help="input iso file")
    # parser1.add_argument("-p", "--path", action="store", required=True, help="input iso file")
    # parser1.add_argument("-o", "--output", action="store", required=True, help="output file")

    args = parser.parse_args()

    if args.action == "analyse":
        # read_fs(args.input)
        filesystem = MBR(args.input)
        filesystem.analyse_header()
        filesystem.display_header_data()
    # elif args.action == "tree":
    #     # read_fs(args.input)
    #     filesystem = MBR(args.input)
    #     filesystem.analyse_header()
    #     # partition.root_dir.display_self_data()
    #     # partition.root_dir.display_tree_data(1)
    #     for partition in filesystem.elements:
    #         partition.partition.root_dir.display_self_data()
    #         partition.partition.root_dir.display_tree_data(1)
    # elif args.action == "export":
    #     # read_fs(args.input)
    #     filesystem = MBR(args.input)
    #     filesystem.analyse_header()
    #     # content = partition.get_filesystem_entry_content(args.path)
    #     for partition in filesystem.elements:
    #         content = partition.partition.get_filesystem_entry_content(args.path)
    #         if content != None:
    #             break
    #     if content != None:
    #         if isinstance(content, str):
    #             content = content.encode(encoding="utf-8")
    #         with open(args.output, "bw") as f:
    #             f.write(content)
    #     else:
    #         print("Path doesn't exist")