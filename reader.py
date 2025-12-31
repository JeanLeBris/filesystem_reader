import argparse
from MBR_reader import *
from GPT_reader import *
from utils import *

def get_ps_from_file(input: str, partition_whitelist: list[str]):
    filesystem = MBR(args.input, partition_whitelist)
    filesystem.analyse_header()
    if len(filesystem.elements) == 1:
        if filesystem.elements[0].partition_type_str == "GPT protective MBR":
            filesystem = GPT(args.input)
            filesystem.analyse_header()
    return filesystem

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
        filesystem = get_ps_from_file(args.input, partition_whitelist)
        filesystem.display_header_data()
    elif args.action == "tree":
        # read_fs(args.input)
        filesystem = get_ps_from_file(args.input, partition_whitelist)
        # partition.root_dir.display_self_data()
        # partition.root_dir.display_tree_data(1)
        for partition in filesystem.elements:
            if partition.partition != None:
                if not isinstance(partition.partition, EBR):
                    partition.partition.root_dir.display_self_data()
                    partition.partition.root_dir.display_tree_data(1)
    elif args.action == "export":
        # read_fs(args.input)
        filesystem = get_ps_from_file(args.input, partition_whitelist)
        # content = partition.get_filesystem_entry_content(args.path)
        content = None
        for partition in filesystem.elements:
            if partition.partition != None:
                if not isinstance(partition.partition, EBR):
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