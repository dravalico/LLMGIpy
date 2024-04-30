# !pip install psb2
import psb2
import os

def devide_i_form_o(data):
  input_dict = {}
  output_dict = {}

  for key, value in data.items():
      if key.startswith('input'):
          input_dict[key] = value
      elif key.startswith('output'):
          output_dict[key] = value
  return input_dict, output_dict

def dict_to_list_of_values(data):
  # Extract the values from the dictionary and create a list of values
  list_of_values = [value for value in data.values()]

  if len(list_of_values) > 1:
    # Flatten the list
    #flattened_list = [item for sublist in list_of_values for item in sublist]
    flattened_list = [item for sublist in list_of_values for item in (sublist if isinstance(sublist, list) else [sublist])]
    return flattened_list
  else:
    return list_of_values

def create_data_for_problem(name: str):
  folder_name = name
  (train_data, test_data) = psb2.fetch_examples("path/to/PSB2/datasets/", name, 1000, 1000)

  list_train_in = []
  list_train_out = []
  for i in train_data:
    inp, out = devide_i_form_o(i)

    list_train_in.append(dict_to_list_of_values(inp))
    list_train_out.append(dict_to_list_of_values(out))

  list_test_in = []
  list_test_out = []
  for i in test_data:
    inp, out = devide_i_form_o(i)
    list_test_in.append(dict_to_list_of_values(inp))
    list_test_out.append(dict_to_list_of_values(out))

  folder_name = os.path.join('progsys', folder_name)
  os.makedirs(folder_name, exist_ok=True)

  # Create the 'train.txt' file inside the folder
  with open(os.path.join(folder_name, 'Train.txt'), 'w') as train_file:
      train_file.write(f"inval = {list_train_in}\noutval = {list_train_out}")

  # Create the 'test.txt' file inside the folder
  with open(os.path.join(folder_name, 'Test.txt'), 'w') as test_file:
      test_file.write(f"inval = {list_test_in}\noutval = {list_test_out}")

  print(f"End for {name}")

if __name__ == "__main__":
  problem_names = psb2.PROBLEMS
  for name in problem_names:
  create_data_for_problem(name)

#import shutil
#import zipfile

# Replace 'your_folder' with the name of the folder you want to zip
#folder_to_zip = 'progsys'

# Replace 'output.zip' with the name of the output zip file
#output_zip = 'progsys.zip'

# Create a zip archive of the folder and its contents
#shutil.make_archive(output_zip, 'zip', folder_to_zip)

#print(f'{folder_to_zip} has been zipped to {output_zip}.zip')
