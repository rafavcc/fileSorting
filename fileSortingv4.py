import os
import time
import shutil

# Define the directory where the files are located
docu_path = "/Volumes/1000g/7_XYZ"
down_path = "/Users/rafavcc/Downloads/mp4"
pornstars = "/Users/rafavcc/Library/Mobile Documents/com~apple~CloudDocs/Programming/from_me/fileSorting/pornstars.txt"
pmv = "Pmv Compilation"

# Define a list of common persons names and close the file

def return_list(input_file) -> list:
    """
    Read the pornstar txt file and returns a list containing the all the names
    """
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
    
    file = open(input_file, 'w')
    for linha in list_of_names:
        file.write(linha + "\n")
    file.close()

    del linha
    del input_file
    return(list_of_names)

def move_with_progress(src, dst, buffer_size=100*1024*1024):  # 256KB buffer size
    total_size = os.path.getsize(src)
    transferred = 0
    start_time = time.time()

    with open(src, 'rb') as src_file, open(dst, 'wb') as dst_file:
        while chunk := src_file.read(buffer_size):
            dst_file.write(chunk)
            dst_file.flush()
            os.fsync(dst_file.fileno())  # Ensure data is written before continuing
            transferred += len(chunk)

            elapsed_time = time.time() - start_time
            speed = transferred / elapsed_time / (1024 * 1024) if elapsed_time > 0 else 0
            percentage = (transferred / total_size) * 100

            print(f'Transferido: {transferred / (1024*1024):.2f}MB / {total_size / (1024 * 1024):.2f}MB | {percentage:.2f}% | Speed: {speed:.2f} MB/s', end='\r')
            time.sleep(0.1)

    # Close the source file first before deleting
    time.sleep(2)  # Allow system to release file lock
    os.remove(src)
    print("\nTransfer complete.")

# Detect if there is a file to be moved and move it 
def fileSorting(person_names, search_path, docu_path, filename):    
     
    # Extract the name of the file (without the extension) and remove . _ - 
    name, ext = os.path.splitext(filename)
    broken = name.replace(".", " ").replace("_", " ").replace("-", " ").replace("+", " ")
    
    # Loop through all person names
    if (ext == ".mp4" or ext == ".avi" or ext == ".mkv" or ext == ".icloud"):
        for person_name in person_names:
            
            # If the person name is found in the file name (ignoring case)
            if person_name.lower() in broken.lower():     
                
                #Check if file is already in correct folder
                check = docu_path.split("/")[-1]
                if (check == person_name):
                      break
                  
                # Create a directory for the person (if it doesn't exist)         
                person_dir = os.path.join(docu_path, person_name)                      
                if not os.path.exists(person_dir):
                    os.mkdir(person_dir)
                    
                # Move the file to the person's directory
                print(f'Person Name = {person_name}')
                #shutil.move(os.path.join(search_path, filename), os.path.join(person_dir, filename))
                
                
                src = os.path.join(search_path, filename)
                dst = os.path.join(person_dir, filename)

                shutil.copy2(src, dst)
                os.remove(src)
                #move_with_progress(os.path.join(search_path, filename), os.path.join(person_dir, filename))
                
                # Break out of the loop (assuming each file only matches one person name)
                break

# Loop through all files in the directory
def browsing(search_path, docu_path, person_names : list):
    for filename in os.listdir(search_path):   
        # Check if the file is a valid file (not a directory)
        if os.path.isfile(os.path.join(search_path, filename)):
            # If file, then sort file
            fileSorting(person_names, search_path, docu_path, filename)  
        else:
            # If folder, then run recursevely run browsing again on sub-folder
            search_path_sub = search_path + '/' + filename
            browsing(search_path_sub, docu_path, person_names)

# Run Script in Downloads Folder            
browsing(down_path, docu_path, return_list(pornstars))