import os
from os import listdir, chdir
from os.path import isfile, join
import json
from typing import List, Any, Dict
from scripts.ponyge.txt_individuals_from_json import txt_population
import ast


def create_txt_population_foreach_json(jsons_dir_path: str) -> List[str]:
    impr_filenames: List[str] = []
    for filename in [f for f in listdir(jsons_dir_path) if isfile(join(jsons_dir_path, f))]:
        create_grammar_from(jsons_dir_path + '/' + filename)
        print("dynamic/" + jsons_dir_path.split('/')[-1] + "/" +  filename.replace(".json", '.bnf'))
        try:
            txt_population(jsons_dir_path + '/' + filename,
                           "dynamic/" + jsons_dir_path.split('/')[-1] + "/" +  filename.replace(".json", ".bnf"),  # FIXME hardcoded grammar
                           jsons_dir_path.split('/')[-1] + '_' + filename.replace(".json", ''))
            print(f"'{filename}' leads to a valid seed for improvement")
            impr_filenames.append(filename)
        except:
            print(f"'{filename}' raises an exception; no population generated")
    if len(impr_filenames) == 0:
        e: str = "\nNone of given jsons lead to a valid seed for improvement"
        raise Exception(e)
    return impr_filenames


def create_grammar_from(json_path: str) -> None:
    cwd: str = os.getcwd()
    chdir("../PonyGE2/grammars")
    if not os.path.isdir("dynamic"):
        os.mkdir("dynamic")
    chdir("dynamic")
    dir_name: str = json_path.split('/')[-2]
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)
    chdir(dir_name)
    with open(json_path, 'r') as json_file:
        json_file: Any = json.load(json_file)
    data: List[Dict[str, Any]] = json_file["data"]
    extracted_functions_from_individuals: List[List[str]] = []
    extracted_strings_from_individuals: List[List[str]] = []
    variables: List[List[str]] = []
    imports: List[List[str]] = []
    for e in data:
        extracted_functions_from_individuals.append(
            extract_functions_and_methods(e["code_no_imports_and_comments"]))
        extracted_strings_from_individuals.append(extract_strings(e["code_no_imports_and_comments"]))
        variables.append(e["variables_names"])
        imports.append(e["imports_predefined"])
    temp0: str = ""
    temp: str = ""
    flat_list = [item for sublist in extracted_functions_from_individuals for item in sublist]
    for i in flat_list:
        if "." in i:
            temp0 += f'"{i}" | '
        else:
            temp += f'"{i}" | '
    temp0 = temp0[:-2]
    temp = temp[:-2]
    temp1: str = ""
    flat_list1 = [item for sublist in extracted_strings_from_individuals for item in sublist]
    for i in flat_list1:
        temp1 += f'"{i}" | '
    temp1 = temp1[:-2]
    temp2: str = ""
    flat_list2 = [item for sublist in variables for item in sublist]
    for i in flat_list2:
        temp2 += f'"{i}" | '
    temp2 = temp2[:-2]
    temp3: str = ""
    flat_list3 = [item for sublist in imports for item in sublist]
    for i in flat_list3:
        temp3 += i + '#'
    with open("../dynamic.bnf", 'rb') as source_file, open(json_path.split('/')[-1].replace(".json", ".bnf"), 'wb') as dest_file:
        dest_file.write(source_file.read())
    with open(json_path.split('/')[-1].replace(".json", ".bnf"), 'a') as bnf:
        if temp != "":
            bnf.write("<FUNC> ::= " + temp + '\n')
        else:
             bnf.write("<FUNC> ::= " + "''" + '\n')
        if temp0 != "":
            bnf.write("<METHOD> ::= " + temp0 + '\n')
        else:
             bnf.write("<METHOD> ::= " + "''" + '\n')
        if temp1 != "":
            bnf.write("<STRINGS> ::= " + temp1 + '\n')
        else:
             bnf.write("<STRINGS> ::= " + "''" + '\n')
        if temp2 != "":
            bnf.write("<var> ::= " + temp2 + '\n')
        else:
             bnf.write("<var> ::= " + "''" + '\n')
        if temp3 != "":
            bnf.write('<IMPORTS> ::= "' + temp3 + '"' + ' | ' + '""' + '\n')
    chdir(cwd)


def extract_functions_and_methods(code: str) -> List[str]:
    function_and_method_names = []
    tree = ast.parse(code)
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
                function_and_method_names.append(func_name)
            elif isinstance(node.func, ast.Attribute):
                if isinstance(node.func.value, ast.Name):
                    # obj_name = node.func.value.id
                    method_name = node.func.attr
                    function_and_method_names.append(f".{method_name}")
                elif isinstance(node.func.value, ast.Subscript):
                    if isinstance(node.func.value.value, ast.Name):
                        # obj_name = node.func.value.value.id
                        method_name = node.func.attr
                        function_and_method_names.append(f".{method_name}")
    return function_and_method_names


def extract_strings(code: str) -> List[str]:
    strings = []
    tree = ast.parse(code)

    class StringExtractor(ast.NodeVisitor):
        def visit_Str(self, node):
            strings.append(node.s)
    string_extractor = StringExtractor()
    string_extractor.visit(tree)
    return list(set(strings))


# NOTE maybe ponyge related things can be enucleate
TRAIN_DATASET_TAG: str = "<train>"
TEST_DATASET_TAG: str = "<test>"
SEED_FOLDER_TAG: str = "<seedFolder>"


def create_params_file(jsons_dir_path: str, impr_filenames: List[str]) -> str:
    cwd: str = os.getcwd()
    chdir("../PonyGE2/parameters")
    jsons_dir_name: str = jsons_dir_path.split('/')[-1]
    improvement_dir: str = "improvements"
    with open(f"./{improvement_dir}/progimpr_base.txt", 'r') as file:
        impr_base_file: str = file.read()
    if not os.path.isdir(improvement_dir):
        os.mkdir(improvement_dir)
    params_dir_path: str = os.path.join(improvement_dir, jsons_dir_name)
    if not os.path.isdir(params_dir_path):
        os.mkdir(params_dir_path)
    for impr_filename in impr_filenames:
        impr_file: str = impr_base_file.replace(
            SEED_FOLDER_TAG,
            jsons_dir_name + '_' + impr_filename.replace(".json", ''))
        with open(os.path.join(jsons_dir_path, impr_filename), 'r') as read_file:
            extracted_json: Any = json.load(read_file)
        prob_name: List[Dict[str, Any]] = extracted_json["problem_name"]
        impr_file = impr_file.replace(
            TRAIN_DATASET_TAG,
            prob_name)
        impr_file = impr_file.replace(
            TEST_DATASET_TAG,
            prob_name)
        output_filepath: str = os.path.join(params_dir_path, impr_filename.replace(".json", ".txt"))
        output_file = open(output_filepath, 'w')
        output_file.write(impr_file)
        output_file.close()
    chdir(cwd)
    return "../PonyGE2/parameters/" + params_dir_path
