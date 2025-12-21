import argparse
import math
from utils import *

class FAT16_filesystem_entry:
    content: bytes
    # filesystem: exFAT
    no_FAT_chain: bool

    name: str
    type: str
    first_cluster: int
    data_byte_length: int

    # allocation_bitmap: bytes
    # up_case_table: bytes
    # volume_label: str
    # elements: list


    def __init__(self, cluster_value: int, filesystem, contiguous: bool = False, size: int = 0):
        self.first_cluster = cluster_value
        self.filesystem = filesystem
        self.elements: list[FAT16_filesystem_entry] = []
        self.content = bytes()
        self.data_byte_length = None
        self.no_FAT_chain = contiguous
        if cluster_value == -1:
            self.content = filesystem.get_cluster_value(cluster_value)
            self.name = convert_bytes_to_str(self.content, 0, 11)
            self.type = "dir"
            cluster_value = convert_bytes_to_int(self.content, 26, 2, "le")
            self.first_cluster = cluster_value
            self.content = bytes()
        if cluster_value == 0:
            self.content = filesystem.get_cluster_value(cluster_value)
            # self.name = convert_bytes_to_str(self.content, 0, 11)
            # self.type = "dir"
            cluster_value = convert_bytes_to_int(self.content, 26, 2, "le")
            self.first_cluster = cluster_value
            self.content = bytes()
        if size == 0:
            size = self.filesystem.bytes_per_sector_shift * self.filesystem.sectors_per_cluster_shift
        if self.no_FAT_chain:
            for i in range(math.ceil(size / (self.filesystem.bytes_per_sector_shift * self.filesystem.sectors_per_cluster_shift))):
                self.content += filesystem.get_cluster_value(cluster_value + i)
        else:
            while True:
                # print(filesystem.get_FAT_value(cluster_value))
                self.content += filesystem.get_cluster_value(cluster_value)
                if filesystem.get_FAT_value(cluster_value) == 0xffff: # EOF
                    break
                elif filesystem.get_FAT_value(cluster_value) == 0xfff8: # Media descriptor
                    break
                elif filesystem.get_FAT_value(cluster_value) == 0xfff7: # Bad cluster
                    break
                # elif filesystem.get_FAT_value(cluster_value) == 0x0001: # Undefined
                #     break
                # elif filesystem.get_FAT_value(cluster_value) == 0x0000: # Undefined
                #     break
                else:
                    cluster_value = filesystem.get_FAT_value(cluster_value)
        # print("done")
    
    def process_data(self):
        if convert_bytes_to_str(self.content, 0, 11).replace(" ", "") == ".":
            i = 2
        else:
            i = 1
        str_buffer = ""
        while convert_bytes_to_int(self.content, i * 32, 1, "le") != 0x00:
            strand = convert_bytes_to_bytes(self.content, i * 32, 32)
            cluster_buffer = convert_bytes_to_int(strand, 26, 2, "le")

            if cluster_buffer == 0:
                str_buffer = self.get_name_bytes_from_entry(strand).decode(encoding="utf-16").replace(bytes([0xff, 0xff]).decode(encoding="utf-16"), '').replace(bytes([0, 0]).decode(encoding="utf-16"), '') + str_buffer
            else:
                data_length_buffer = convert_bytes_to_int(strand, 28, 4, "le")
                type_buffer = "dir" if ((convert_bytes_to_int(strand, 11, 1, "le") >> 4) & 1) == 1 else "file"
                self.elements.append(FAT16_filesystem_entry(cluster_buffer, self.filesystem, False, data_length_buffer))
                self.elements[-1].name = str_buffer
                self.elements[-1].type = type_buffer
                if type_buffer == "dir":
                    self.elements[-1].process_data()
                elif type_buffer == "file":
                    self.elements[-1].data_byte_length = data_length_buffer
                self.elements[-1].no_FAT_chain = False
                str_buffer = ""

            i+=1
    
    def get_name_bytes_from_entry(self, strand: bytes):
        sanitized_bytes = bytes()
        sanitized_bytes += convert_bytes_to_bytes(strand, 1, 10)
        sanitized_bytes += convert_bytes_to_bytes(strand, 14, 12)
        sanitized_bytes += convert_bytes_to_bytes(strand, 28, 4)
        return sanitized_bytes
    
    def get_self_data(self):
        return f"{self.type} : {self.name} : {self.first_cluster} : {self.no_FAT_chain}\n"
    
    def get_tree_data(self, level: int):
        value = ""
        for element in self.elements:
            for i in range(level):
                value += "  "
            value += f"{element.type} : {element.name} : {element.first_cluster} : {element.no_FAT_chain}\n"
            value += element.get_tree_data(level + 1)
        return value
    
    def display_self_data(self):
        print(self.get_self_data(), end="")
    
    def display_tree_data(self, level: int):
        print(self.get_tree_data(level), end="")
    
    def get_filesystem_entry(self, input_path: list):
        for filesystem_entry in self.elements:
            if input_path[0] == filesystem_entry.name:
                if len(input_path) == 1:
                    return filesystem_entry
                else:
                    return filesystem_entry.get_filesystem_entry(input_path[1:])
        return None
    
    def get_file_content(self):
        # content = bytes()
        # if self.type == "file":
        #     while True:
        #         self.content += self.filesystem.get_cluster_value(cluster_value)
        #         if self.filesystem.get_FAT_value(cluster_value) == 0xffffffff: # EOF
        #             break
        #         elif self.filesystem.get_FAT_value(cluster_value) == 0xfffffff8: # Media descriptor
        #             break
        #         elif self.filesystem.get_FAT_value(cluster_value) == 0xfffffff7: # Bad cluster
        #             break
        #         elif self.filesystem.get_FAT_value(cluster_value) == 0x00000001: # Undefined
        #             break
        #         elif self.filesystem.get_FAT_value(cluster_value) == 0x00000000: # Undefined
        #             break
        # return None
        return self.content

class FAT16:
    input_path: str
    offset: int

    # Boot sector data
    fs_name: str
    partition_offset: int
    volume_length: int
    boot_fat_offset: int
    boot_fat_length: int
    boot_cluster_heap_offset: int
    boot_cluster_count: int
    boot_first_cluster_of_root_directory: int
    volume_serial_number: int
    fs_revision_minor: int
    fs_revision_major: int
    fs_revision: str
    volume_flags: int
    bytes_per_sector_shift: int
    sectors_per_cluster_shift: int
    boot_number_of_fats: int
    drive_select: int
    percent_in_use: int
    reserved: bytes
    boot_code: bytes
    boot_signature: bytes

    sectors_in_reserved_area: int
    root_entry_count: int
    sectors_in_16bit_field: int
    bpb_media: int
    number_of_sectors_per_track: int
    number_of_heads: int
    hidden_sectors: int
    sectors_in_32bit_field: int

    # FAT region
    number_of_fats: int
    first_fat_offset: int
    first_fat_length: int
    second_fat_offset: int
    second_fat_length: int

    # Root dir
    root_dir_offset: int
    root_dir_length: int

    # Data region
    data_area_offset: int
    data_area_length: int

    # Root directory
    first_cluster_of_root_directory: int
    root_dir: FAT16_filesystem_entry

    def __init__(self, file_path: str, offset: int = 0):
        self.input_path = file_path
        self.offset = offset
        # self.partition_offset = offset
    
    def analyse_boot_sector(self):
        boot_sector = None
        with open(self.input_path, "br") as f:
            f.seek(self.offset, 0)
            boot_sector = f.read(512)
        
        self.bytes_per_sector_shift = convert_bytes_to_int(boot_sector, 11, 2, "le")
        self.sectors_per_cluster_shift = convert_bytes_to_int(boot_sector, 13, 1, "le")
        self.sectors_in_reserved_area = convert_bytes_to_int(boot_sector, 14, 2, "le")
        self.boot_number_of_fats = convert_bytes_to_int(boot_sector, 16, 1, "le")
        self.root_entry_count = convert_bytes_to_int(boot_sector, 17, 2, "le")
        self.sectors_in_16bit_field = convert_bytes_to_int(boot_sector, 19, 2, "le")
        self.bpb_media = convert_bytes_to_int(boot_sector, 21, 1, "le")
        self.boot_fat_length = convert_bytes_to_int(boot_sector, 22, 2, "le")
        self.number_of_sectors_per_track = convert_bytes_to_int(boot_sector, 24, 2, "le")
        self.number_of_heads = convert_bytes_to_int(boot_sector, 26, 2, "le")
        self.hidden_sectors = convert_bytes_to_int(boot_sector, 28, 4, "le")
        self.sectors_in_32bit_field = convert_bytes_to_int(boot_sector, 32, 4, "le")
        
        self.fs_name = convert_bytes_to_bytes(boot_sector, 3, 8).decode(encoding="utf-8")
        self.partition_offset = convert_bytes_to_int(boot_sector, 64, 8, "le") # Offset of the exFAT volume origin from top of the hosting physical drive in unit of sector (1 unit of sector = 512 bytes)
        self.volume_length = convert_bytes_to_int(boot_sector, 72, 8, "le")
        self.boot_fat_offset = convert_bytes_to_int(boot_sector, 80, 4, "le")
        self.boot_cluster_heap_offset = convert_bytes_to_int(boot_sector, 88, 4, "le")
        self.boot_cluster_count = convert_bytes_to_int(boot_sector, 92, 4, "le")
        self.boot_first_cluster_of_root_directory = convert_bytes_to_int(boot_sector, 96, 4, "le")
        self.volume_serial_number = convert_bytes_to_int(boot_sector, 100, 4, "le")
        self.fs_revision_minor = convert_bytes_to_int(boot_sector, 104, 1, "le")
        self.fs_revision_major = convert_bytes_to_int(boot_sector, 105, 1, "le")
        self.fs_revision = str(self.fs_revision_major) + "." + str(self.fs_revision_minor)
        self.volume_flags = convert_bytes_to_int(boot_sector, 106, 2, "le")
        self.drive_select = convert_bytes_to_int(boot_sector, 111, 1, "le")
        self.percent_in_use = convert_bytes_to_int(boot_sector, 112, 1, "le")
        self.reserved = convert_bytes_to_bytes(boot_sector, 113, 7)
        self.boot_code = convert_bytes_to_bytes(boot_sector, 120, 390)
        self.boot_signature = convert_bytes_to_bytes(boot_sector, 510, 216)

        self.number_of_fats = self.boot_number_of_fats
        self.first_fat_offset = self.sectors_in_reserved_area
        self.first_fat_length = self.boot_fat_length
        self.second_fat_offset = self.first_fat_offset+self.first_fat_length
        self.second_fat_length = self.first_fat_length*(self.number_of_fats-1)

        self.root_dir_offset = self.first_fat_offset+self.number_of_fats*self.boot_fat_length
        self.root_dir_length = int((32 * self.root_entry_count) / self.bytes_per_sector_shift)

        self.data_area_offset = self.root_dir_offset + self.root_dir_length
        if self.sectors_in_16bit_field != 0:
            self.data_area_length = self.sectors_in_16bit_field - self.data_area_offset
        else:
            self.data_area_length = self.sectors_in_32bit_field - self.data_area_offset

        # self.first_cluster_of_root_directory = self.boot_first_cluster_of_root_directory

        self.root_dir = FAT16_filesystem_entry(-1, self)
        self.root_dir.process_data()
    
    def display_boot_sector_data(self):
        print("File system name : ", self.fs_name)
        print("Partition offset : " + str(self.partition_offset))
        print("Volume length : " + str(self.volume_length))
        print("Fat offset : " + str(self.boot_fat_offset))
        print("Fat length : " + str(self.boot_fat_length))
        print("Cluster heap offset : " + str(self.boot_cluster_heap_offset))
        print("Cluster count : " + str(self.boot_cluster_count))
        print("Sector count : " + str(self.sectors_per_cluster_shift * self.boot_cluster_count))
        print("Byte count : " + str(self.bytes_per_sector_shift * self.sectors_per_cluster_shift * self.boot_cluster_count))
        print("First cluster of root directory : " + str(self.boot_first_cluster_of_root_directory))
        print("First sector of root directory : " + str(self.sectors_per_cluster_shift * self.boot_first_cluster_of_root_directory))
        print("First byte of root directory : " + str(self.bytes_per_sector_shift * self.sectors_per_cluster_shift * self.boot_first_cluster_of_root_directory))
        print("Volume serial number : " + str(self.volume_serial_number))
        print("File system revision : " + self.fs_revision)
        print("Volume flags : " + str(self.volume_flags))
        print("Bytes per sector shift : " + str(self.bytes_per_sector_shift))
        print("Sectors per cluster shift : " + str(self.sectors_per_cluster_shift))
        print("Number of fats : " + str(self.boot_number_of_fats))
        print("Drive select : " + str(self.drive_select))
        print("Percent in use : " + str(self.percent_in_use))
        print("Reserved : " + str(self.reserved))
        print("Boot code : " + str(self.boot_code))
        print("Boot signature : " + str(self.boot_signature))
        print("Number of sectors in reserved area : " + str(self.sectors_in_reserved_area))
        print("Number of entries in root directory : " + str(self.root_entry_count))
        print("Total number of sectors in 16 bit field : " + str(self.sectors_in_16bit_field))
        print("BPB Media : " + str(self.bpb_media))
        print("Number of sectors per track : " + str(self.number_of_sectors_per_track))
        print("Number of heads : " + str(self.number_of_heads))
        print("Number of hidden sectors : " + str(self.hidden_sectors))
        print("Total number of sectors in 32 bit field : " + str(self.sectors_in_32bit_field))
        print()
        print("Areas :")
        print("Main boot region :")
        print(f"Boot sector :\t\t\t{0}\t{1}")
        print(f"Reserved sectors :\t\t{1}\t{self.sectors_in_reserved_area-1}")
        print("FAT region :")
        print(f"First FAT :\t\t\t{self.first_fat_offset}\t{self.first_fat_length}")
        print(f"Second FAT :\t\t\t{self.second_fat_offset}\t{self.second_fat_length}")
        print("Root region :")
        print(f"Root directory :\t\t{self.root_dir_offset}\t{self.root_dir_length}")
        print("Data region :")
        print(f"Data areas :\t\t\t{self.data_area_offset}\t{self.data_area_length}")
    
    def get_FAT_value(self, cluster_value: int):
        data = None
        if cluster_value >= 0:
            with open(self.input_path, "br") as f:
                f.seek(self.offset + self.first_fat_offset * self.bytes_per_sector_shift, 0)
                data = f.read((self.first_fat_length + self.second_fat_length) * self.bytes_per_sector_shift)
            data = convert_bytes_to_int(data, cluster_value * 2, 2, "le")
            # address = self.first_fat_offset * self.bytes_per_sector_shift
            # address += cluster_value * 4
        else:
            data = -1
        return data
    
    def get_cluster_value(self, cluster_value: int):
        data = None
        if cluster_value >= 0:
            with open(self.input_path, "br") as f:
                f.seek(self.offset + (self.data_area_offset + (cluster_value - 2) * self.sectors_per_cluster_shift) * self.bytes_per_sector_shift, 0)
                data = f.read(self.sectors_per_cluster_shift * self.bytes_per_sector_shift)
            # address = self.first_fat_offset * self.bytes_per_sector_shift
            # address += cluster_value * 4
        else:
            with open(self.input_path, "br") as f:
                f.seek(self.offset + self.root_dir_offset * self.bytes_per_sector_shift, 0)
                data = f.read(self.root_dir_length * self.bytes_per_sector_shift)
        return data
    
    def get_filesystem_entry(self, input_path: str):
        separated_path = input_path.split("/")
        filesystem_entry: FAT16_filesystem_entry = self.root_dir
        if separated_path[0] == filesystem_entry.name:
            if len(separated_path) == 1:
                return filesystem_entry
            else:
                return filesystem_entry.get_filesystem_entry(separated_path[1:])
        else:
            return None
    
    def get_filesystem_entry_content(self, input_path: str):
        filesystem_entry = self.get_filesystem_entry(input_path)
        # value = ""
        if filesystem_entry == None:
            return None
        elif filesystem_entry.type == "dir":
            return filesystem_entry.get_self_data() + filesystem_entry.get_tree_data(1)
        elif filesystem_entry.type == "file":
            return filesystem_entry.get_file_content()
        else:
            return None

def read_fs(input_path):
    partition = FAT16(input_path)
    partition.analyse_boot_sector()
    # partition.display_boot_sector_data()
    # print(hex(partition.get_FAT_value(4)))
    # partition.root_dir = exFAT_filesystem_entry(4, partition)
    # # print(convert_bytes_to_bytes(partition.root_dir.content, 0, 512))
    # partition.root_dir.process_data()
    # partition.root_dir.display_self_data()
    # partition.root_dir.display_tree_data(1)
    print(partition.get_filesystem_entry_content("CLE USB 4/CVs - Resumes/octobre 2023/CV.jpg"))
    return partition.get_cluster_value(4)

if __name__=="__main__":
    parser = argparse.ArgumentParser(prog="fs_reader",
                                     description="read a ExFat file system")
    
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
        partition = FAT16(args.input)
        partition.analyse_boot_sector()
        partition.display_boot_sector_data()
    elif args.action == "tree":
        # read_fs(args.input)
        partition = FAT16(args.input)
        partition.analyse_boot_sector()
        # partition.root_dir = exFAT_filesystem_entry(4, partition)
        # partition.root_dir.process_data()
        partition.root_dir.display_self_data()
        partition.root_dir.display_tree_data(1)
    elif args.action == "export":
        # read_fs(args.input)
        partition = FAT16(args.input)
        partition.analyse_boot_sector()
        # partition.root_dir = exFAT_filesystem_entry(4, partition)
        # partition.root_dir.process_data()
        content = partition.get_filesystem_entry_content(args.path)
        if isinstance(content, str):
            content = content.encode(encoding="utf-8")
        with open(args.output, "bw") as f:
            f.write(content)