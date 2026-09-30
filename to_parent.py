import os
import shutil
import subprocess

def all_to_parent(folder_path):
    """Move all video files back to the root directory, removing empty resolution folders."""
    valid_extensions = ('.jpeg', '.jpg', '.png', '.mov', '.flv', '.wmv')

    for root, dirs, files in os.walk(folder_path, topdown=False):  # topdown=False para remover pastas vazias depois
        for file in files:
            if file.startswith("."):  # Skip hidden files
                continue
            if file.lower().endswith(valid_extensions):
                file_path = os.path.join(root, file)
                
                # Move de volta para o diretório raiz
                target_path = os.path.join(folder_path, file)
                shutil.move(file_path, target_path)

                print(f"Moved: {file} -> {folder_path}")

        # Depois de mover todos os arquivos, remove a pasta vazia
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            if not os.listdir(dir_path):  # Se a pasta estiver vazia, remove
                os.rmdir(dir_path)
                print(f"Removed empty folder: {dir_path}")
                
directory = f'/Volumes/rafavcc1TB/1_fotos/2014/12 - OK/25'
all_to_parent(directory)