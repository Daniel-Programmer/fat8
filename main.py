from cache import Cache
from virtual_drive import VirtualDrive
from fat8 import Fat8
from fat_dir_entry import FatDirEntry
from fat_file import FatFile

if __name__ == '__main__':
    short_data = """ABCDEFGHIJKLMNOPQRSTUVWXYZ"""

    medium_data = """Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Cras pede libero, dapibus nec, pretium sit amet, tempor quis. Nunc auctor. Mauris dictum facilisis augue. Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis doloribus asperiores repellat. 
    Curabitur vitae diam non enim vestibulum interdum. In laoreet, magna id viverra tincidunt, sem odio bibendum justo, vel imperdiet sapien wisi sed libero. Duis bibendum, lectus ut viverra rhoncus, dolor nunc faucibus libero, eget facilisis enim ipsum id lacus. Mauris tincidunt sem sed arcu. Sed elit dui, pellentesque a, faucibus vel, interdum nec, diam. 
    Nulla non lectus sed nisl molestie malesuada. Phasellus rhoncus. Aliquam erat volutpat.
    Nunc tincidunt ante vitae massa. Nullam dapibus fermentum ipsum. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos hymenaeos. Etiam ligula pede, sagittis quis, interdum ultricies, scelerisque eu. Integer in sapien. Duis sapien nunc, commodo et, interdum suscipit, sollicitudin et, dolor. Pellentesque pretium lectus id turpis. 
    Pellentesque ipsum. Etiam ligula pede, sagittis quis, interdum ultricies, scelerisque eu. Quisque tincidunt scelerisque libero. Duis condimentum augue id magna semper rutrum. Nulla accumsan, elit sit amet varius semper, nulla mauris mollis quam, tempor suscipit diam nulla vel leo. Etiam bibendum elit eget erat.
    Integer imperdiet lectus quis justo. Nullam eget nisl. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Vivamus luctus egestas leo. Etiam bibendum elit eget erat. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. 
    Fusce dui leo, imperdiet in, aliquam sit amet, feugiat eu, orci. Etiam egestas wisi a erat. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Sed ac dolor sit amet purus malesuada congue. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. 
    Maecenas lorem. Pellentesque ipsum. Aenean fermentum risus id tortor. Pellentesque pretium lectus id turpis. Morbi imperdiet, mauris ac auctor dictum, nisl ligula egestas nulla, et sollicitudin sem purus in lacus."""

    long_data = """Lorem ipsum dolor sit amet, consectetuer adipiscing elit. Cras pede libero, dapibus nec, pretium sit amet, tempor quis. Nunc auctor. Mauris dictum facilisis augue. Itaque earum rerum hic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur aut perferendis doloribus asperiores repellat. Curabitur vitae diam non enim vestibulum interdum. In laoreet, magna id viverra tincidunt, sem odio bibendum justo, vel imperdiet sapien wisi sed libero. Duis bibendum, lectus ut viverra rhoncus, dolor nunc faucibus libero, eget facilisis enim ipsum id lacus. Mauris tincidunt sem sed arcu. Sed elit dui, pellentesque a, faucibus vel, interdum nec, diam. Nulla non lectus sed nisl molestie malesuada. Phasellus rhoncus. Aliquam erat volutpat.
    Nunc tincidunt ante vitae massa. Nullam dapibus fermentum ipsum. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos hymenaeos. Etiam ligula pede, sagittis quis, interdum ultricies, scelerisque eu. Integer in sapien. Duis sapien nunc, commodo et, interdum suscipit, sollicitudin et, dolor. Pellentesque pretium lectus id turpis. Pellentesque ipsum. Etiam ligula pede, sagittis quis, interdum ultricies, scelerisque eu. Quisque tincidunt scelerisque libero. Duis condimentum augue id magna semper rutrum. Nulla accumsan, elit sit amet varius semper, nulla mauris mollis quam, tempor suscipit diam nulla vel leo. Etiam bibendum elit eget erat.
    Integer imperdiet lectus quis justo. Nullam eget nisl. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Vivamus luctus egestas leo. Etiam bibendum elit eget erat. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Fusce dui leo, imperdiet in, aliquam sit amet, feugiat eu, orci. Etiam egestas wisi a erat. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum. Sed ac dolor sit amet purus malesuada congue. Pellentesque habitant morbi tristique senectus et netus et malesuada fames ac turpis egestas. Maecenas lorem. Pellentesque ipsum. Aenean fermentum risus id tortor. Pellentesque pretium lectus id turpis. Morbi imperdiet, mauris ac auctor dictum, nisl ligula egestas nulla, et sollicitudin sem purus in lacus.
    Sed vel lectus. Donec odio tempus molestie, porttitor ut, iaculis quis, sem. Maecenas libero. Donec vitae arcu. Vestibulum erat nulla, ullamcorper nec, rutrum non, nonummy ac, erat. Nullam dapibus fermentum ipsum. Mauris metus. Integer rutrum, orci vestibulum ullamcorper ultricies, lacus quam ultricies odio, vitae placerat pede sem sit amet enim. In rutrum. Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos hymenaeos. Nulla est. Fusce aliquam vestibulum ipsum.
    Cum sociis natoque penatibus et magnis dis parturient montes, nascetur ridiculus mus. Etiam posuere lacus quis dolor. Aliquam erat volutpat. Duis sapien nunc, commodo et, interdum suscipit, sollicitudin et, dolor. Aenean vel massa quis mauris vehicula lacinia. Suspendisse sagittis ultrices augue. Quisque tincidunt scelerisque libero. Integer rutrum, orci vestibulum ullamcorper ultricies, lacus quam ultricies odio, vitae placerat pede sem sit amet enim. Cras pede libero, dapibus nec, pretium sit amet, tempor quis. Maecenas sollicitudin. Nullam feugiat, turpis at pulvinar vulputate, erat libero tristique tellus, nec bibendum odio risus sit amet ante. Integer rutrum, orci vestibulum ullamcorper ultricies, lacus quam ultricies odio, vitae placerat pede sem sit amet enim. Fusce suscipit libero eget elit. Sed elit dui, pellentesque a, faucibus vel, interdum nec, diam. Aenean id metus id velit ullamcorper pulvinar. Praesent in mauris eu tortor porttitor accumsan. Aenean fermentum risus id tortor. Curabitur vitae diam non enim vestibulum interdum. Mauris dolor felis, sagittis at, luctus sed, aliquam non, tellus. Nullam eget nisl."""

    # create a virtual drive of the size
    VirtualDrive.manufacture("drive", 1000)
    virtual_drive = VirtualDrive.open("drive")

    # assign cache to virtual drive
    drive = Cache(virtual_drive, 5)

    # create instance of file system
    fat = Fat8()

    # format file system
    fat.format(drive)

    # open file system (load data from file)
    fat.open(drive)
    print("FAT information:")
    print(fat)
    print("")

    # print all files
    print("All files: ")
    print(FatDirEntry.read_dir(fat))
    print("")

    # create variables with files
    file1 = FatFile(fat, "file1.txt")
    file2 = FatFile(fat, "file2.txt")
    file3 = FatFile(fat, "file3.txt")

    # open file and return file descriptor
    print("Create/Open files file1, file2 a file3 and get their sizes")
    fd1 = file1.open()
    fd2 = file2.open()
    fd3 = file3.open()

    print("file1 size: ", fd1.stat())
    print("file2 size: ", fd2.stat())
    print("file3 size: ", fd3.stat())
    print("")

    fd1.write(short_data)
    fd2.write(medium_data)
    fd3.write(long_data)

    print("file1: File size after data is inserted: ", fd1.stat())
    print("file2: File size after data is inserted: ", fd2.stat())
    print("file3: File size after data is inserted: ", fd3.stat())
    print("")

    print("All files: ")
    print(FatDirEntry.read_dir(fat))
    print("")

    print("Read 15 bytes from file1:")
    print(fd1.read(15))
    print("")

    print("Current positon in file1")
    print(fd1.tell())
    print("")

    inserted_string = "Inserted string"
    print(f"Write string from position: \"{inserted_string}\"")
    fd1.write(inserted_string)
    print("")

    print("Move to beggining of the file and read 50 bytes from file1:")
    fd1.seek(0)
    print(fd1.read(50))
    print("")

    print("Read byte 50 to 100 from file2:")
    fd3.seek(50)
    print(fd2.read(50))
    print("")

    print(f"Expand file1 from {fd1.stat()} to size: 6000")
    fd1.truncate(12000)
    print("Size of file1: ", fd1.stat())
    print("")

    print(f"Shrink file1 from {fd1.stat()} to size: 3000")
    fd1.truncate(3000)
    print("Size of file1: ", fd1.stat())
    print("")

    print("All files: ")
    print(FatDirEntry.read_dir(fat))
    print("")

    print("Delete file: file2")
    file2.delete()
    print("")

    print("All files after deleting file file2: ")
    print(FatDirEntry.read_dir(fat))
    print("")

    file4 = FatFile(fat, "file4.txt")

    print("Create/Open file4")
    fd4 = file4.open()
    print("")

    print("All files after creating/opening file4")
    print(FatDirEntry.read_dir(fat))
    print("")
