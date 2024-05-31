import os
from os import listdir, chdir
from os.path import isfile, join
import json
from typing import List, Any, Dict
from scripts.ponyge.txt_individuals_from_json import txt_population
import ast
from scripts.imports_and_prompt import extract_prompt_info_with_keybert, extract_numbers_from_string

from models.GrammarGeneratorLLM import GrammarGeneratorLLM

# def create_txt_population_foreach_json(jsons_dir_path: str, task_llm_grammar_generator: str | None = None) -> Any:
def create_txt_population_foreach_json(jsons_dir_path: str, task_llm_grammar_generator = None) -> Any:
    impr_filenames: List[str] = []
    grammars_filenames: List[str] = []
    if task_llm_grammar_generator is not None:
        grammarGenerator = GrammarGeneratorLLM(grammar_task = task_llm_grammar_generator)
    for filename in [f for f in listdir(jsons_dir_path) if isfile(join(jsons_dir_path, f))]:
        bnf_filename: str = create_grammar_from(jsons_dir_path + '/' + filename, grammarGenerator)
        try:
            txt_population(jsons_dir_path + '/' + filename,
                           "dynamic/" + jsons_dir_path.split('/')[-1] + "/" + filename.replace(".json", ".bnf"),
                           jsons_dir_path.split('/')[-1] + '_' + filename.replace(".json", ''))
            print(f"'{filename}' leads to a valid seed for improvement")
            impr_filenames.append(filename)
            grammars_filenames.append(bnf_filename)
        except:
            print(f"'{filename}' raises an exception; no population generated")
    if len(impr_filenames) == 0:
        e: str = "\nNone of given jsons lead to a valid seed for improvement"
        raise Exception(e)
    return impr_filenames, grammars_filenames


# def create_grammar_from(json_path: str, task_llm_grammar_generator: str | None) -> str:
def create_grammar_from(json_path: str, grammarGenerator) -> str:
    cwd: str = os.getcwd()
    chdir("./PonyGE2/grammars")
    if not os.path.isdir("dynamic"):
        os.mkdir("dynamic")
    chdir("dynamic")
    dir_name: str = json_path.split('/')[-2]
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)
    chdir(dir_name)
    with open(json_path, 'r') as json_file:
        json_file: Any = json.load(json_file)
    data: List[Dict[str, Any]] = json_file["data_preprocess"]
    extracted_functions_from_individuals: List[List[str]] = []
    extracted_strings_from_individuals: List[List[str]] = []
    variables: List[List[str]] = []
    imports: List[List[str]] = []
    nums = [[0, 1, 2, 3, 4, 5, 6, 7, 8, 9]]
    for e in data:
        extracted_functions_from_individuals.append(
            extract_functions_and_methods(e["main_func"]))
        res_strings = extract_strings(e["main_func"])
        prompt_info_strings = extract_prompt_info_with_keybert(json_file["problem_description"])
        extracted_strings_from_individuals.append(res_strings + prompt_info_strings)
        nums.append(extract_numbers_from_string(json_file["problem_description"]))
        variables.append(e["variables_names"])
        imports.append(e["imports"])
    temp0: str = ""
    temp: str = ""
    flat_list = [item for sublist in extracted_functions_from_individuals for item in sublist]
    for i in flat_list:
        if "." in i and i not in temp0:
            temp0 += f'"{i}" | '
        elif "." not in i and i not in temp:
            temp += f'"{i}" | '
    temp0 = temp0[:-2]
    temp = temp[:-2]
    temp1: str = []
    flat_list1 = [item for sublist in extracted_strings_from_individuals for item in sublist]
    for i in flat_list1:
        if f'"\'{i}\'"' not in temp1:
            temp1.append(f'"\'{i}\'"')
            temp1.append(" | ")
    temp1 = temp1[:-1]
    temp2: str = ""
    flat_list2 = [item for sublist in variables for item in sublist]
    for i in flat_list2:
        if i not in temp2:
            temp2 += f'"{i}" | '
    temp2 = temp2[:-2]
    temp2 += '| "a0" | "a1" | "a2"'
    temp3: str = ""
    flat_list3 = [item for sublist in imports for item in sublist]
    for i in flat_list3:
        if i not in temp3:
            temp3 += i + '#'
    temp4: str = ""
    flat_list4 = [item for sublist in nums for item in sublist]
    for i in flat_list4:
        if str(i) not in temp4:
            temp4 += f'"{i}" | '
    temp4 = temp4[:-2]
    with open("../dynamic.bnf", 'rb') as source_file, open(json_path.split('/')[-1].replace(".json", ".bnf"), 'wb') as dest_file:
        dest_file.write(source_file.read())
    with open(json_path.split('/')[-1].replace(".json", ".bnf"), 'a') as bnf:
        if temp != "":
            bnf.write("<FUNC> ::= " + temp + '\n')
        else:
            bnf.write("<FUNC> ::= " + '""' + '\n')
        if temp0 != "":
            bnf.write("<METHOD> ::= " + temp0 + '\n')
        else:
            bnf.write("<METHOD> ::= " + '""' + '\n')
        if temp1 != []:
            bnf.write("<STRINGS> ::= " + ''.join(temp1) + '\n')
        else:
            bnf.write("<STRINGS> ::= " + '""' + '\n')
        if temp2 != "":
            bnf.write("<var> ::= " + temp2 + '\n')
        else:
            bnf.write("<var> ::= " + '""' + '\n')
        bnf.write("<num> ::= " + temp4 + '\n')
        bnf.write('<IMPORTS> ::= "' + temp3 + '"' + ' | ' + '""' + '\n')
    if grammarGenerator is not None:
        for i, e in enumerate(data): # where data = json_file["data_preprocess"]
           generated_bnfs = grammarGenerator.ask_just_grammar(prompt=json_file["problem_description"], code=e["main_func"], grammar_path=os.path.join(cwd, "PonyGE2/grammars/dynamic", dir_name, json_path.split('/')[-1].replace(".json", ".bnf")))
           with open(json_path.split('/')[-1].replace(".json", f"_generated_iteration{i}.bnf"), 'w') as bnf_generated: # ! add a folder where put the files
                bnf_generated.write(generated_bnfs)
    
    chdir(cwd)
    return json_path.split('/')[-2] + '/' + json_path.split('/')[-1].replace(".json", ".bnf")


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
BNF_GRAMMAR_TAG: str = "<bnf>"


def create_params_file(jsons_dir_path: str, impr_filenames: List[str], grammars_filenames) -> str:
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
    for (impr_filename, grammar_filename) in zip(impr_filenames, grammars_filenames):
        impr_file: str = impr_base_file.replace(
            SEED_FOLDER_TAG,
            jsons_dir_name + '_' + impr_filename.replace(".json", ''))
        impr_file = impr_file.replace(BNF_GRAMMAR_TAG, grammar_filename)
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
