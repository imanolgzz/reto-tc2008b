import os

def from_txt_to_desc(file_path, output_path):
    try:
        with open(file_path, 'r') as file:
            desc = [line.strip() for line in file.readlines()]
        
        with open(output_path, 'w') as output_file:
            # Escribe las líneas del archivo en orden inverso
            for line in desc:
                output_file.write(f"{line}\n")
            
            # Encuentra la posición de 'I' y escribe en el archivo
            for row_index, line in enumerate(desc):
                col_index = line.find('I')
                if col_index != -1:
                    output_file.write(f"Position of 'I': Row={row_index}, Col={col_index}\n")
        
        return desc
    except Exception as e:
        print(f"Error reading the file: {e}")
        return None

@staticmethod
def from_txt_to_desc1(file_path, output_path):
    try:
        with open(file_path, 'r') as file:
            desc = [line.strip() for line in file.readlines()][::-1]
        
        with open(output_path, 'w') as output_file:
            # Escribe las líneas del archivo en orden inverso
            for line in desc:
                output_file.write(f"{line}\n")
            
            # Encuentra la posición de 'I' y escribe en el archivo
            for row_index, line in enumerate(desc):
                col_index = line.find('I')
                if col_index != -1:
                    output_file.write(f"Position of 'I': Row={row_index}, Col={col_index}\n")
        
        return desc
    except Exception as e:
        with open(output_path, 'w') as output_file:
            output_file.write(f"Error reading the file: {e}\n")
        return None

@staticmethod
def from_txt_to_desc2(file_path, output_path):
    try:
        with open(file_path, 'r') as file:
            desc = [line.strip()[::-1] for line in file.readlines()]
        
        with open(output_path, 'w') as output_file:
            # Escribe las líneas invertidas
            for line in desc:
                output_file.write(f"{line}\n")
            
            # Encuentra la posición de 'I' y escribe en el archivo
            for row_index, line in enumerate(desc):
                col_index = line.find('I')
                if col_index != -1:
                    output_file.write(f"Position of 'I': Row={row_index}, Col={col_index}\n")
        
        return desc
    except Exception as e:
        with open(output_path, 'w') as output_file:
            output_file.write(f"Error reading the file: {e}\n")
        return None

@staticmethod
def from_txt_to_desc3(file_path, output_path):
    try:
        with open(file_path, 'r') as file:
            desc = [line.strip()[::-1] for line in file.readlines()][::-1]
        
        with open(output_path, 'w') as output_file:
            # Escribe las líneas procesadas
            for line in desc:
                output_file.write(f"{line}\n")
            
            # Encuentra la posición de 'I' y escribe en el archivo
            for row_index, line in enumerate(desc):
                col_index = line.find('I')
                if col_index != -1:
                    output_file.write(f"Position of 'I': Row={row_index}, Col={col_index}\n")
        
        return desc
    except Exception as e:
        with open(output_path, 'w') as output_file:
            output_file.write(f"Error reading the file: {e}\n")
        return None
    
def read_map():
    desc_file = "maze.txt"
    root_path = os.path.dirname(os.path.abspath(__file__))
    output_file = root_path + "/output1.txt"
    desc = from_txt_to_desc1(root_path + "/" + desc_file, output_file)
    output_file = root_path + "/output2.txt"
    desc = from_txt_to_desc2(root_path + "/" + desc_file, output_file)
    output_file = root_path + "/output3.txt"
    desc = from_txt_to_desc3(root_path + "/" + desc_file, output_file)
    output_file = root_path + "/output.txt"
    descV = from_txt_to_desc(root_path + "/" + desc_file, output_file)

    return descV
#read_map()


grid = [[1 if char in {'M', 'S', 'U', 'J', 'I', 'O'} else 0 for char in row] for row in read_map()]
# write grid to file
with open("grid.txt", "w") as file:
    for row in grid:
        file.write(f"{row}\n")
