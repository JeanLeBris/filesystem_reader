import argparse
from utils import *
from FAT16_reader import *
from FAT32_reader import *
from exFAT_reader import *

class GPT_entry:
    entry_value: int
    content: bytes

    partition_type_GUID: bytes
    unique_partition_GUID: bytes
    first_LBA: int
    last_LBA: int # Inclusive
    attribute_flags: int
    partition_name: str

    def __init__(self, entry_value: int, filesystem):
        self.filesystem = filesystem
        self.entry_value = entry_value

        self.content = self.filesystem.get_partition_entry(self.entry_value)
    
    def check_if_exist(self):
        if convert_bytes_to_int(self.content, 32, 8, "le") != 0:
            return True
        else:
            return False
    
    def process_data(self):
        self.partition_type_GUID = convert_bytes_to_bytes(self.content, 0, 16)
        self.unique_partition_GUID = convert_bytes_to_bytes(self.content, 16, 16)
        self.first_LBA = convert_bytes_to_int(self.content, 32, 8, "le")
        self.last_LBA = convert_bytes_to_int(self.content, 40, 8, "le")
        self.attribute_flags = convert_bytes_to_int(self.content, 48, 8, "le")
        self.partition_name = convert_bytes_to_bytes(self.content, 56, 72).decode(encoding="utf-16")

        # self.partition = exFAT(self.filesystem.input_path, self.first_LBA*512)
        # self.partition.analyse_boot_sector()
        self.partition = None

        with open(self.filesystem.input_path, "br") as f:
            f.seek(self.first_LBA*512, 0)
            boot_sector = f.read(512)
        
        fs_type = guess_fs_from_sector(boot_sector)
        if fs_type == "FAT12":
            # print("FAT12 : " + str(self.first_LBA))
            pass
        elif fs_type == "FAT16":
            # print("FAT16 : " + str(self.first_LBA))
            self.partition = FAT16(self.filesystem.input_path, self.first_LBA*512)
            self.partition.analyse_boot_sector()
        elif fs_type == "FAT32":
            # print("FAT32 : " + str(self.first_LBA))
            self.partition = FAT32(self.filesystem.input_path, self.first_LBA*512)
            self.partition.analyse_boot_sector()
        elif fs_type == "exFAT":
            # print("exFAT : " + str(self.first_LBA))
            self.partition = exFAT(self.filesystem.input_path, self.first_LBA*512)
            self.partition.analyse_boot_sector()
    
    def get_self_data(self):
        return f"{self.partition_name} : {self.first_LBA} : {self.last_LBA}\n"
    
    def display_self_data(self):
        print(self.get_self_data(), end="")

class GPT:
    input_path: str

    fs_name: str
    fs_revision_minor: int
    fs_revision_major: int
    fs_revision: str
    header_size: int
    header_crc_32: bytes
    current_LBA: int
    backup_LBA: int
    first_usable_LBA_for_partitions: int
    last_usable_LBA_for_partitions: int
    disk_GUID: bytes
    starting_LBA_of_array_of_partition_entries: int
    number_of_partition_entries_in_array: int
    size_of_partition_entry: int
    partition_entries_array_crc_32: bytes

    elements: list[GPT_entry]

    def __init__(self, file_path: str):
        self.input_path = file_path
        self.elements = []
    
    def analyse_header(self):
        boot_sector = None
        with open(self.input_path, "br") as f:
            f.seek(512, 0)
            boot_sector = f.read(512)

        self.fs_name = convert_bytes_to_bytes(boot_sector, 0, 8).decode(encoding="utf-8")
        self.fs_revision_minor = convert_bytes_to_int(boot_sector, 8, 2, "le")
        self.fs_revision_major = convert_bytes_to_int(boot_sector, 10, 2, "le")
        self.fs_revision = str(self.fs_revision_major) + "." + str(self.fs_revision_minor)
        self.header_size = convert_bytes_to_int(boot_sector, 12, 4, "le")
        self.header_crc_32 = convert_bytes_to_bytes(boot_sector, 16, 4) # Check what CRC-32 is
        self.current_LBA = convert_bytes_to_int(boot_sector, 24, 8, "le")
        self.backup_LBA = convert_bytes_to_int(boot_sector, 32, 8, "le")
        self.first_usable_LBA_for_partitions = convert_bytes_to_int(boot_sector, 40, 8, "le")
        self.last_usable_LBA_for_partitions = convert_bytes_to_int(boot_sector, 48, 8, "le")
        self.disk_GUID = convert_bytes_to_bytes(boot_sector, 56, 16)
        self.starting_LBA_of_array_of_partition_entries = convert_bytes_to_int(boot_sector, 72, 8, "le")
        self.number_of_partition_entries_in_array = convert_bytes_to_int(boot_sector, 80, 4, "le")
        self.size_of_partition_entry = convert_bytes_to_int(boot_sector, 84, 4, "le")
        self.partition_entries_array_crc_32 = convert_bytes_to_bytes(boot_sector, 88, 4)

        keep_going = True
        i = 0
        while keep_going:
            element = GPT_entry(i, self)
            if element.check_if_exist():
                element.process_data()
                # test.display_self_data()
                self.elements.append(element)
            else:
                keep_going = False
            # i+=self.size_of_partition_entry
            i+=1

    def display_header_data(self):
        print(f"File system name : {self.fs_name}")
        print(f"File system revision : {self.fs_revision}")
        print(f"Header size : {self.header_size}")
        print(f"CRC-32 of header : {self.header_crc_32}")
        print(f"Current LBA location : {self.current_LBA}")
        print(f"Backup LBA location : {self.backup_LBA}")
        print(f"First usable LBA for partitions : {self.first_usable_LBA_for_partitions}")
        print(f"Last usable LBA for partitions : {self.last_usable_LBA_for_partitions}")
        print(f"Disk GUID : {self.disk_GUID}")
        print(f"Starting LBA of array of partition entries : {self.starting_LBA_of_array_of_partition_entries}")
        print(f"Number of partition entries in array : {self.number_of_partition_entries_in_array}")
        print(f"Size of a single partition entry : {self.size_of_partition_entry}")
        print(f"CRC-32 of partition entries array : {self.partition_entries_array_crc_32}")

        print()
        print("Filesystems :")
        for element in self.elements:
            element.display_self_data()
            if element.partition != None:
                element.partition.display_boot_sector_data()
    
    def get_partition_entry(self, entry_value: int):
        content = None
        with open(self.input_path, "br") as f:
            f.seek(self.starting_LBA_of_array_of_partition_entries*512 + entry_value*self.size_of_partition_entry, 0)
            content = f.read(self.size_of_partition_entry)
        return content

if __name__=="__main__":
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
        filesystem = GPT(args.input)
        filesystem.analyse_header()
        filesystem.display_header_data()
    elif args.action == "tree":
        # read_fs(args.input)
        filesystem = GPT(args.input)
        filesystem.analyse_header()
        # partition.root_dir.display_self_data()
        # partition.root_dir.display_tree_data(1)
        for partition in filesystem.elements:
            if partition.partition != None:
                partition.partition.root_dir.display_self_data()
                partition.partition.root_dir.display_tree_data(1)
    elif args.action == "export":
        # read_fs(args.input)
        filesystem = GPT(args.input)
        filesystem.analyse_header()
        # content = partition.get_filesystem_entry_content(args.path)
        for partition in filesystem.elements:
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