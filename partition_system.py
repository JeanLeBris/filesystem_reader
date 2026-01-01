from partition import *

class partitionsystem:
    pass

class partitionsystem_element:
    parent_filesystem: partitionsystem
    entry_value: int
    content: bytes

    name: str
    type: str
    start: int
    length: int

    element: partition

    def __init__(self, filesystem: partitionsystem, entry_value: int):
        self.parent_filesystem = filesystem
        self.entry_value = entry_value
        # self.content = None
        self.element = None

        self.name = "part name"
        self.type = "part type"
        self.start = 0
        self.length = 0

        self.content = self.parent_filesystem.get_partition_entry(self.entry_value)

        # self.process_data()
    
    def check_if_exist(self):
        pass

    def is_readable(self):
        pass
    
    def process_data(self):
        pass
    
    def get_self_data(self):
        return f"{self.type} : {self.name} : {self.start} : {self.length}"
    
    def display_self_data(self):
        print(self.get_self_data())
    
class partitionsystem(partition):
    elements: list[partitionsystem_element]

    def __init__(self, file_path: str, offset: int = 0):
        super().__init__(file_path, offset)
        self.partition_type = "default partition system"
        self.elements = []
        
        # self.analyse_boot_sector()
    
    def analyse_boot_sector(self):
        pass

    def flatten_elements(self):
        pass
    
    def display_data(self):
        print(f"{self.partition_type} :")
        print(f"  Source : {self.input_path}")
        print(f"  Offset : {self.offset}")
        print(f"  Bytes per sector : {self.bytes_per_sector}")
        print(f"  Structure :")
        print(f"    Boot sector : {self.boot_sector_offset} : {self.boot_sector_length}")
        print(f"    Data area : {self.data_area_offset} : {self.data_area_length}")
        if len(self.elements) > 0:
            print(f"  Content :")
            for element in self.elements:
                print(f"    {element.get_self_data()}")
        print()
    
    def get_partition_entry(self, entry_value: int):
        pass

if __name__ == "__main__":
    test_part = partitionsystem("test_name.iso", 100)
    test_part.elements.append(partitionsystem_element(test_part, 1))
    test_part.elements.append(partitionsystem_element(test_part, 2))
    test_part.elements.append(partitionsystem_element(test_part, 3))
    test_part.display_data()
    # test_part.display_files()