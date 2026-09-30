import os
import shutil

# Define the directory where the files are located
dir_path = "/Users/rafaelviegas/XXX"
pornstars = "pornstars.txt"

# Define a list of common persons names and close the file
person_names = []
file = open(pornstars)
for linha in file:
    person_names.append(linha.strip().title())
file.close()

#print(person_names)

os.remove(os.path.join(os.getcwd(),pornstars))
person_names.sort()
file = open(pornstars, 'w')
for linha in person_names:
    file.write(linha + "\n")
file.close()

# Loop through all files in the directory
for filename in os.listdir(dir_path):

    # Check if the file is a valid file (not a directory)
    if os.path.isfile(os.path.join(dir_path, filename)):
        
        def fileSorting(person_names, dir_path):
        
        # Extract the name of the file (without the extension)
        name, ext = os.path.splitext(filename)
        broken = name.replace(".", " ").replace("_", " ").replace("-", " ")
        print(f'Broken = {broken}, ext = {ext}')
        # Loop through all person names
        if (ext == ".mp4" or ext == ".avi" or ext == ".mkv"):
            for person_name in person_names:
                # If the person name is found in the file name (ignoring case)
                if person_name.lower() in broken.lower():     
                    # Create a directory for the person (if it doesn't exist)
                    person_dir = os.path.join(dir_path, person_name)
                    if not os.path.exists(person_dir):
                        os.mkdir(person_dir)
                    # Move the file to the person's directory
                    shutil.move(os.path.join(dir_path, filename), os.path.join(person_dir, filename))
                    # Break out of the loop (assuming each file only matches one person name)
                    break
    else:
        dir_path_sub = dir_path + '/' + filename