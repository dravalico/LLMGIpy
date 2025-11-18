import pandas as pd
from tqdm import tqdm
import re
import os


from scripts.python_code_arranger import properly_arrange_code_with_imports_functions
from scripts.ponyge.individual_formatter import convert_main_func_to_pony_ind
from scripts.ponyge.txt_individuals_from_json import parse_genotypes
from scripts.ponyge.improvement_files_generator import extract_functions_and_methods


ROOT_GRAMMARS_PATH = "/share/malelab/LLMGIpy/PonyGE2/grammars/dynamic/dynamicbnf/L/humaneval_text/CodeGemma7B/iter10_rep0/train20_test1000"
HUMANE_EVAL_JSON_PATH = "/share/malelab/LLMGIpy/PonyGE2/datasets/progsys/humaneval.json"
BASE_GRAMMAR_PATH = "/share/malelab/LLMGIpy/PonyGE2/grammars/dynamic/dynamicbnf/L/humaneval_text_base"
# BASE_GRAMMAR_PATH = "/share/malelab/LLMGIpy/PonyGE2/grammars/dynamic/dynamicbnf/L/humaneval_text"

def extract_variables_from_file(file_path, start_token: str = '<var> ::='):
    with open(file_path, 'r') as file:
        for line in file:
            if line.strip().startswith(start_token): # ! attenzione al doppio spazio
                # Extract everything between double quotes
                variables = re.findall(r'"(.*?)"', line)
                return variables
    return []  # If the line is not found

# Example usage
# variable_list = extract_variables_from_file('/share/malelab/LLMGIpy/PonyGE2/grammars/dynamic/dynamicbnf/L/humaneval_text/CodeGemma7B/iter10_rep0/train20_test1000/problem1_complete_dynamic.bnf')
# print(variable_list)

# def compare_and_map_lists(list1, list2):
#     difference = abs(len(list1) - len(list2))

#     # If difference is greater than 3
#     if difference > 3:
#         print("Attention: difference between lists is greater than 3")

#     # If the difference is negative (list1 shorter than list2), do nothing
#     if len(list1) < len(list2):
#         return None

#     # Remove common elements
#     unique_list1 = [item for item in list1 if item not in list2]
#     unique_list2 = [item for item in list2 if item not in list1]

#     # Build dictionary
#     result = dict(zip(unique_list2, unique_list1))
#     return result

def compare_and_map_lists(list1, list2):
    difference = abs(len(list1) - len(list2))

    # If difference is greater than 3
    if difference > 3:
        print("Attention: difference between lists is greater than 3")

    # If the difference is negative (list1 shorter than list2), do nothing
    if len(list1) < len(list2):
        return None

    # Remove common elements
    unique_list1 = [item for item in list1 if item not in list2]
    unique_list2 = [item for item in list2 if item not in list1]
    prioritized = [x for x in unique_list1 if x.startswith(('v', 'a'))]
    others = [x for x in unique_list1 if not x.startswith(('v', 'a'))]
    ordered_list1 = prioritized + others
    
    # Build dictionary
    result = dict(zip(unique_list2, ordered_list1))
    return result

# list1 = ['v0', 'v1', 'v2', 'v3', 'a0', 'a1', 'a2']
# list2 = ['v0', 'v1', 'v2', 'v3', 'v4', 'v5', 'v6']

# output = compare_and_map_lists(list1, list2)
# print(output)



def list_subdirectories(path):
    try:
        # List only directories inside the given path
        folders = [name for name in os.listdir(path) if os.path.isdir(os.path.join(path, name))]
        return folders
    except FileNotFoundError:
        return f"Error: The path '{path}' does not exist."
    except PermissionError:
        return f"Error: Permission denied for the path '{path}'."

# folder_list = list_subdirectories("/share/malelab/LLMGIpy/PonyGE2/grammars/dynamic/dynamicbnf/L/humaneval_text/CodeGemma7B/iter10_rep0/train20_test1000")
# print(folder_list)


def file_exists(file_path):
    return os.path.isfile(file_path)

# path = "/share/malelab/LLMGIpy/PonyGE2/grammars/dynamic/dynamicbnf/L/humaneval_text/CodeGemma7B/iter10_rep0/train20_test1000/problem0_complete_dynamic.bnf"
# if file_exists(path):
#     print("File exists.")
# else:
#     print("File does not exist.")


def replace_from_dict(text, replacements):
    if replacements is not None:
        for key, value in replacements.items():
            text = text.replace(key, value)
    return text


# text = "Hello NAME bene comNAMEva, welcome to PLACE!"
# replacements = {
#     "NAME": "Alice",
#     "PLACE": "Wonderland"
# }

# result = replace_from_dict(text, replacements)
# print(result)


def replace_if_contains(original: str, target: str, replacement: str) -> str:
    if target in original:
        return original.replace(target, replacement)
    else:
        return original

def all_elements_covered(main_list, list2, list3): # ! no
    """
    Check if all elements in list2 and list3 are present in main_list.

    Parameters:
        main_list (list): The reference list.
        list2 (list): The second list to check.
        list3 (list): The third list to check.

    Returns:
        bool: True if all elements in list2 and list3 are in main_list, False otherwise.
    """
    return all(elem in main_list for elem in list2 + list3)

def all_elements_covered(main_list, list2, list3):
    """
    Check if every element in main_list is present in at least one of list2 or list3.

    Parameters:
        main_list (list): The list of elements to check.
        list2 (list): First reference list.
        list3 (list): Second reference list.

    Returns:
        bool: True if all elements of main_list are in list2 or list3, False otherwise.
    """
    list2.append('')
    list3.append('')
    list2.append("")
    list3.append("")
    return all(elem in list2 or elem in list3 for elem in main_list)


def remove_elements_from_list(main_list, list2, list3):
    """
    Remove all elements in list2 and list3 from main_list.

    Parameters:
        main_list (list): The list from which elements will be removed.
        list2 (list): Elements to remove.
        list3 (list): More elements to remove.

    Returns:
        list: A new list with the elements removed.
    """
    to_remove = set(list2 + list3)
    return [item for item in main_list if item not in to_remove]

# quit()
func_total = []
method_total = []
programs_total = []
print("Reading humanEval")
df_humaneval = pd.read_json(HUMANE_EVAL_JSON_PATH)
print("Creating complete solutions")
df_humaneval['complete_solution'] = df_humaneval['prompt'] + df_humaneval['canonical_solution']

print("Creating PonyGE individuals")
out = []
success = 0
fail = 0
error = 0
total = 0
big_error = 0
not_parsable = 0
potentially_parsable = 0
try:
    for i, solution in tqdm(enumerate(df_humaneval['complete_solution'])):
        try:
            ind = properly_arrange_code_with_imports_functions(s=df_humaneval['complete_solution'][i],
                                                            include_free_code=True,
                                                            replace_entry_point_with_this_name='evolve',
                                                            replace_vars=True,
                                                            remove_non_existing_import=True,
                                                            remove_syntax_errors=True)

            # print(ind) #entry_point
            # right key "renamed_main_func"
            # print(convert_main_func_to_pony_ind(ind['renamed_main_func']))
            # print(convert_main_func_to_pony_ind(ind['renamed_main_func'].replace("clear", "append").replace("v4", "v2")))

            final_ind = convert_main_func_to_pony_ind(ind['renamed_main_func'])
        except Exception as e:
            print(f"BIG_ERROR on ind -> {e}")
            big_error += 1
        try:
            for model_dir in list_subdirectories(BASE_GRAMMAR_PATH):
                print("="*30)
                base_model_grammar_path = os.path.join(BASE_GRAMMAR_PATH, model_dir)
                
                for iter_rep_dir in list_subdirectories(base_model_grammar_path):
                    print("="*15)
                    base_model_iter_grammar_path = os.path.join(base_model_grammar_path, iter_rep_dir)
                    try:
                        for train_test_dir in list_subdirectories(base_model_iter_grammar_path):
                            print("="*5)
                            base_model_iter_train_test_grammar_path = os.path.join(base_model_iter_grammar_path, train_test_dir)
                            # grammar_file = os.path.join(base_model_iter_train_test_grammar_path, f"problem{i}_complete_dynamic.bnf")
                            grammar_file = os.path.join(base_model_iter_train_test_grammar_path, f"problem{i}.bnf")
                            if file_exists(grammar_file):
                                func_and_met = extract_functions_and_methods(solution)
                                
                                print(f"original -> {func_and_met}")
                                print(f"METHOD -> {extract_variables_from_file(grammar_file, '<METHOD> ::=')}")
                                print(f"func -> {extract_variables_from_file(grammar_file, '<FUNC> ::=')}")
                                programs_total.extend(func_and_met)
                                func_total.extend(extract_variables_from_file(grammar_file, '<FUNC> ::='))
                                method_total.extend(extract_variables_from_file(grammar_file, '<METHOD> ::='))
                                print(all_elements_covered(func_and_met, extract_variables_from_file(grammar_file, '<METHOD> ::='), extract_variables_from_file(grammar_file, '<FUNC> ::=')))
                            
                                if all_elements_covered(func_and_met, extract_variables_from_file(grammar_file, '<METHOD> ::='), extract_variables_from_file(grammar_file, '<FUNC> ::=')):
                                    potentially_parsable += 1
                                    # if file_exists(grammar_file):
                                    print(f"Analysisng {grammar_file}")            
                                    extract_var_from_grammar = extract_variables_from_file(grammar_file)
                                    different_var = compare_and_map_lists(extract_var_from_grammar, ind['possible_vars'])
                                    if len(different_var) > 9:
                                        print(f"More than 9 Attention in iteration {i}")
                                    print(final_ind)
                                    print(df_humaneval['complete_solution'][i])
                                    print(ind['possible_vars'])
                                    print(extract_var_from_grammar)
                                    print(different_var)
                                    print("relacing....")
                                    final_ind = replace_from_dict(final_ind, different_var)
                                    final_ind = replace_if_contains(final_ind, ind['entry_point'], ind['new_entry_point'])
                                    print(final_ind)
                                    test_g = parse_genotypes(phenotypes=[final_ind],
                                                    grammar_file=grammar_file,
                                                    already_solved=False,
                                                    only_impr=False,
                                                    # dynamic_bnf='dynamicbnf'
                                                    dynamic_bnf='False'
                                                    )
                                    if len(test_g) > 0:
                                        print(f"test_g: {test_g}")
                                        print(f"SUCCESS: {grammar_file}\n") 
                                        out.append(f"SUCCESS: {grammar_file}") 
                                        success += 1
                                    else:
                                        print(f"test_g: {test_g}")
                                        print(f"FAIL: {grammar_file}\n")
                                        out.append(f"FAIL: {grammar_file}")
                                        fail += 1
                                    total += 1
                                else:
                                    not_parsable += 1
                                    total += 1
                            else:
                                print(f"File NOT EXIST: {grammar_file}")
                                # try:
                                #     del extract_var_from_grammar
                                #     del final_ind
                                #     del grammar_file
                                #     del different_var
                                # except:
                                #     pass
                    except Exception as e:
                        print("="*20)
                        print(f"ERROR in {grammar_file} -> {e}")
                        out.append(f"ERROR in {grammar_file} -> {e}")
                        error += 1
                        # total += 1
                        print("="*20)
                    # finally:
        except Exception as e:
            print(f"BIG_ERROR on model_dir -> {e}")
            big_error += 1
        
except Exception as e:
    print("="*20)
    print(f"BIG ERROR in {grammar_file} -> {e}")
    out.append(f"BIG ERROR in {grammar_file} -> {e}")
    big_error += 1
    print("="*20)

print("\n\n")
print(f"SUCCESS: {success}")
print(f"FAIL: {fail}")
print(f"ERROR: {error}")
print(f"BIG ERROR: {big_error}")
print(f"not_parsable: {not_parsable}")
print(f"potentially_parsable: {potentially_parsable}")
print(f"total: {total}")
print("\n")
print(f"diff in method and func {list(set(remove_elements_from_list(programs_total, func_total, method_total)))}")

with open("gramamr_gold_parser.txt", "w", encoding="utf-8") as file:
    for el in out:    
        file.write(el + "\n")
# print(test_g)

# /share/malelab/LLMGIpy/PonyGE2/src


# import os

# if __name__ == "__main__":

#     def process_bnf_files(root_path):
#         for dirpath, _, filenames in os.walk(root_path):
#             for i in range(165):  # Da 0 a 164 incluso
#                 base_file = f"problem{i}.bnf"
#                 complete_file = f"problem{i}_complete_dynamic.bnf"

#                 base_path = os.path.join(dirpath, base_file)
#                 complete_path = os.path.join(dirpath, complete_file)

#                 if os.path.exists(base_path):
#                     if os.path.exists(complete_path):
#                         os.remove(complete_path)
#                         print(f"Cancellato: {complete_path}")
#                     else:
#                         os.remove(base_path)
#                         print(f"Cancellato: {base_path}")

#     process_bnf_files("/share/malelab/LLMGIpy/PonyGE2/grammars/dynamic/dynamicbnf/L/humaneval_text_base")
