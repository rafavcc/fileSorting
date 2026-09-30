import os
import shutil

# Define the directory where the files are located
dir_path = "/Users/rafaelviegas/Documents/XYZ"
pornstars = "pornstars.txt"

# Define a list of common persons names and close the file
person_names = []
file = open(pornstars)
for linha in file:
    person_names.append(linha.strip().title())
    #print(f'person = {linha.strip().title()}')
file.close()



os.remove(os.path.join(os.getcwd(),pornstars))
person_names.sort()
file = open(pornstars, 'w')
for linha in person_names:
    file.write(linha + "\n")
file.close()

del linha
del pornstars


# Detect if there is a file to be moved and move it 
def fileSorting(person_names, dir_path, filename):     
    # Extract the name of the file (without the extension)
    name, ext = os.path.splitext(filename)
    broken = name.replace(".", " ").replace("_", " ").replace("-", " ")
    # Loop through all person names
    if (ext == ".mp4" or ext == ".avi" or ext == ".mkv" or ext == ".icloud"):
        for person_name in person_names:
            # If the person name is found in the file name (ignoring case)
            if person_name.lower() in broken.lower():     
                
                #Check if file is already in correct folder
                check = dir_path.split("/")[-1]
                #print(f'person_name = {person_name}')
                #print(f'broken = {broken}')
                print(f'filename = {filename}')
                if (check == person_name):
                      break
                  
                # Create a directory for the person (if it doesn't exist)         
                person_dir = os.path.join(dir_path, person_name)
                        
                if not os.path.exists(person_dir):
                    os.mkdir(person_dir)
                # Move the file to the person's directory
                # print(f'filename = {filename}')
                shutil.move(os.path.join(dir_path, filename), os.path.join(person_dir, filename))
                
                # Break out of the loop (assuming each file only matches one person name)
                break

# Loop through all files in the directory
def browsing(dir_path, person_names):
    for filename in os.listdir(dir_path):   
        # Check if the file is a valid file (not a directory)
        if os.path.isfile(os.path.join(dir_path, filename)):
            #print(f'Entrei no 1, filename {filename}')
            fileSorting(person_names, dir_path, filename)      
        else:
            #print(f'Entrei no 2, filename {filename}')
            dir_path_sub = dir_path + '/' + filename
            #print(f'DIR PATH SUB = {dir_path_sub}')
            browsing(dir_path_sub,person_names)
            
browsing(dir_path, person_names)