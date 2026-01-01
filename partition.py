import argparse
from utils import *

class partition:
    input_path: str
    offset: int

    partition_type: str

    bytes_per_sector: int

    boot_sector_offset: int # by sectors
    boot_sector_length: int # by sectors
    data_area_offset: int   # by sectors
    data_area_length: int   # by sectors

    def __init__(self, file_path: str, offset: int = 0):
        self.input_path = file_path
        self.offset = offset
        self.partition_type = "default partition"
        self.bytes_per_sector = 512
        self.boot_sector_offset = -1
        self.boot_sector_length = -1
        self.data_area_offset = -1
        self.data_area_length = -1
        
        # self.analyse_boot_sector()
    
    def analyse_boot_sector(self):
        pass
    
    def display_data(self):
        print(f"{self.partition_type} :")
        print(f"\tSource : {self.input_path}")
        print(f"\tOffset : {self.offset}")
        print(f"\tBytes per sector : {self.bytes_per_sector}")
        print(f"\tStructure :")
        print(f"\t\tBoot sector : {self.boot_sector_offset} : {self.boot_sector_length}")
        print(f"\t\tData area : {self.data_area_offset} : {self.data_area_length}")
        print()

if __name__ == "__main__":
    test_part = partition("test_name.iso", 100)
    test_part.display_data()