from partition import *

class filesystem:
    pass

class filesystem_element:
    parent_filesystem: filesystem
    is_root: bool

    name: str
    type: str
    start: int
    length: int # in case it is a file

    elements: list  # in case it is a dir

    def __init__(self, filesystem: filesystem, start: int, size: int = 0, is_root: bool = False):
        self.parent_filesystem = filesystem
        self.start = start
        self.size = size
        self.is_root = is_root
        self.elements: list[filesystem_element] = []

        self.name = "unknown name"
        self.type = "file or dir"
        self.length = 0

        # self.process_data()
    
    def process_data(self):
        pass
    
    def get_self_data(self):
        return f"{self.type} : {self.name} : {self.start}"
    
    def get_tree_data(self, level: int):
        value = ""
        for element in self.elements:
            for i in range(level):
                value += "  "
            value += element.get_self_data() + "\n"
            value += element.get_tree_data(level + 1)
        return value
    
    def display_self_data(self):
        print(self.get_self_data())
    
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

class filesystem(partition):
    root_dir: filesystem_element
    root_dir_start: int
    root_dir_length: int

    def __init__(self, file_path: str, offset: int = 0):
        super().__init__(file_path, offset)
        self.partition_type = "default file system"
        
        # self.analyse_boot_sector()
    
    def analyse_boot_sector(self):
        self.root_dir = filesystem_element(self, 0, 0, True)
        self.root_dir_start = 0
        self.root_dir_length = 0
    
    def display_data(self):
        print(f"{self.partition_type} :")
        print(f"  Source : {self.input_path}")
        print(f"  Offset : {self.offset}")
        print(f"  Bytes per sector : {self.bytes_per_sector}")
        print(f"  Root dir : {self.root_dir_start} : {self.root_dir_length}")
        print(f"  Structure :")
        print(f"    Boot sector : {self.boot_sector_offset} : {self.boot_sector_length}")
        print(f"    Data area : {self.data_area_offset} : {self.data_area_length}")
        # print(f"  Content :")
        # print(f"    {self.root_dir.get_self_data()}\n{self.root_dir.get_tree_data(level=3)}")
        print()
    
    def display_files(self):
        self.root_dir.display_self_data()
        self.root_dir.display_tree_data(1)
        print()

if __name__ == "__main__":
    test_part = filesystem("test_name.iso", 100)
    test_part.root_dir.elements.append(filesystem_element(test_part, 0, 0, False))
    test_part.root_dir.elements.append(filesystem_element(test_part, 0, 0, False))
    test_part.root_dir.elements[0].elements.append(filesystem_element(test_part, 0, 0, False))
    test_part.display_data()
    test_part.display_files()