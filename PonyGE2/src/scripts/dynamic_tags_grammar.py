import re
import os

def is_sublist(list1, list2):
    set1, set2 = set(list1), set(list2)
    return set1.issubset(set2)

def split_file_by_pattern(file_path, pattern = r'<.*?> ::='):
    try:
        with open(os.path.join('..', 'grammars', file_path), 'r') as file:
            content = file.read()
        find_content = re.findall(pattern, content)
        split_content = re.split(pattern, content)[1:]
        final_content = [(f[: -3], s) for f, s in zip(find_content, split_content)]
        return final_content
    except FileNotFoundError:
        return "File not found."
    except Exception as e:
        return f"An error occurred: {str(e)}"

def process_tuples(tuple_list, check_list):
    processed_tuples = []
    for tup in tuple_list:
        first_elem, second_elem = tup
        for i in check_list:
          if i in first_elem:
            split_second_elem = second_elem.split('|')
            valid_second_elem = []
            for item in split_second_elem:
              if is_sublist(re.findall(r'<.*?>', item), check_list):
                for tag_to_keep in check_list:
                  if tag_to_keep in item or ('<' not in item and '>' not in item) or ('"<"' in item or '">"' in item or '">="' in item or '"<="' in item):
                    valid_second_elem.append(item) 
            if first_elem != '<STRINGS> ': 
                processed_tuples.append((first_elem, '|'.join(list(set(valid_second_elem)))))
            else:
                processed_tuples.append((first_elem, second_elem))
    return processed_tuples

def join_tuples(tuple_list):
    joined_content = '\n'.join([f"{tup[0]} ::= {tup[1]}" for tup in tuple_list])
    return joined_content

def save_string_to_file(string_to_save, file_path):
    try:
        with open(file_path, 'w') as file:
            file.write(string_to_save)
        print("String saved to file successfully.\n")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        
def clean_string(input_string):
    cleaned = re.sub(r'\s+\n\|', ' |', input_string)
    cleaned = re.sub(r'\|\n+\s+', '| ', cleaned)
    cleaned = re.sub(r'\n\s+', '\n ', cleaned)
    cleaned = re.sub(r'::= \n\s*', '::= ', cleaned)
    cleaned = re.sub(r'\n+', '\n', cleaned)
    cleaned = re.sub(r'^\s+|\n\s+', '\n', cleaned)
    return cleaned

def create_tag_dynamic_bnf(file_path, tags_to_keep, print_result = False):
  split_content = split_file_by_pattern(file_path)
  processed_tuples = process_tuples(split_content, tags_to_keep)
  final_bnf = join_tuples(processed_tuples)
  final_bnf = clean_string(final_bnf)
  save_string_to_file(final_bnf, os.path.join('..', 'grammars', file_path.replace('.bnf', '_complete_dynamic.bnf')))
  if print_result:
    print(final_bnf)