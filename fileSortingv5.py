import os, shutil

def return_list(input_file):
    list_of_names = []
    file = open(input_file)
    for linha in file:
        list_of_names.append(linha.strip().title())
        #print(f'person = {linha.strip().title()}')
    file.close()

    os.remove(os.path.join(os.getcwd(),input_file))
    list_of_names.sort()
    list_of_names.pop(list_of_names.index(pmv))
    list_of_names.insert(0,pmv)
    #print(list_of_names)
    
    file = open(input_file, 'w')
    for linha in list_of_names:
        file.write(linha + "\n")
    file.close()

    del linha
    del input_file
    return(list_of_names)

# Detect if there is a file to be moved and move it 
def fileSorting(personNames, srcPath, dstPath, filename):    
     
    # Extract the name of the file (without the extension) and remove . _ - 
    name, ext = os.path.splitext(filename)
    nameSimplified = name.replace(".", " ").replace("_", " ").replace("-", " ").replace("+", " ")
    
    # Loop through all person names
    if (ext == ".mp4" or ext == ".avi" or ext == ".mkv" or ext == ".icloud" or ext == ".m4v"):
        for personName in personNames:
            
            # If the person name is found in the file name (ignoring case)
            if personName.lower() in nameSimplified.lower():     
                  
                # Create a directory for the person (if it doesn't exist)         
                personDir = os.path.join(dstPath, personName)
                if not os.path.exists(personDir):
                    os.mkdir(personDir)
                    
                # Move the file to the person's directory
                print(f'Person Name = {personName}')
                
                src = os.path.join(srcPath, filename)
                dst = os.path.join(personDir, filename)
                shutil.move(src, dst)
              
                # Break out of the loop (assuming each file only matches one person name)
                break

def log_source_files(srcPath):
    """Display all files found in the source directory"""
    print(f"\n{'='*60}")
    print(f"Source directory: {srcPath}")
    print(f"{'='*60}")
    
    file_count = 0
    for root, dirs, files in os.walk(srcPath):
        for filename in files:
            file_count += 1
            file_path = os.path.join(root, filename)
            print(f"{file_path}")
    
    print(f"\nTotal files found: {file_count}")
    print(f"{'='*60}\n")

# Loop through all files in the directory
def browsing(srcPath, dstPath, personNames):
    for filename in os.listdir(srcPath):   
        # Check if the file is a valid file (not a directory)
        if os.path.isfile(os.path.join(srcPath, filename)):
            # If file, then sort file
            fileSorting(personNames, srcPath, dstPath, filename)  
        else:
            # If folder, then run recursevely run browsing again on sub-folder
            srcPath_sub = os.path.join(srcPath, filename)
            browsing(srcPath_sub, dstPath, personNames)

# Define the directory where the files are located
default_src = r"E:\7_XYZ\_TO_BE_CAT"
default_dst = r"E:\7_XYZ"

# Get user input for source and destination paths
srcPath = input(f"Enter source directory (default: {default_src}): ").strip()
if not srcPath:
    srcPath = default_src

dstPath = input(f"Enter destination directory (default: {default_dst}): ").strip()
if not dstPath:
    dstPath = default_dst

# Check if paths exist
if not os.path.exists(srcPath):
    print(f"Error: Source path does not exist: {srcPath}")
    exit(1)

if not os.path.exists(dstPath):
    print(f"Error: Destination path does not exist: {dstPath}")
    exit(1)

pornstars = os.path.join(os.getcwd(), "pornstars.txt")
pmv = "Pmv Compilation"
_3d = "3D"

# Log the source files to terminal
log_source_files(srcPath)

# Run Script
browsing(srcPath, dstPath, return_list(pornstars))