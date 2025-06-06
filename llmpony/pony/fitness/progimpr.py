import queue
from subprocess import Popen, PIPE
from multiprocessing import Queue, Process
import sys
import traceback
import numpy as np
from os import path
import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=FutureWarning)
from llmpony.llm.functions.json_data_io import read_json

from llmpony.pony.algorithm.parameters import params
from llmpony.pony.fitness.base_ff_classes.base_ff import base_ff


class progimpr(base_ff):
    """Fitness function for program improvement problems. Grammars and datasets
    for 29 benchmark problems from doi.org/10.1145/2739480.2754769 are
    provided. Evaluation is done in a separate python process."""

    # constants required for formatting the code correctly
    INSERTCODE = "<insertCodeHere>"
    INSERTIMPORTS = "<insertImports>"
    INSERTSUPPORTS = "<insertSupports>"
    INSERTFITNESSFUNCTION = "<insertFitnessFunction>"

    INDENTSPACE = "  "
    LOOPBREAK = "loopBreak"
    LOOPBREAKUNNUMBERED = "loopBreak%"
    LOOPBREAK_INITIALISE = "loopBreak% = 0"
    LOOPBREAK_IF = "if loopBreak% >"
    LOOPBREAK_INCREMENT = "loopBreak% += 1"
    FORCOUNTER = "forCounter"
    FORCOUNTERUNNUMBERED = "forCounter%"

    def __init__(self):
        # Initialise base fitness function class.
        super().__init__()

        self.default_fitness = progimpr.set_default_fitness(self.default_fitness)

        self.fitness_function = self.get_fitness_eval(params['FITNESS_FILE'])
        self.training, self.test, self.embed_header, self.embed_footer = \
            self.get_data(params['DATASET_TRAIN'], params['DATASET_TEST'],
                          params['GRAMMAR_FILE'])
        #self.eval = self.create_eval_process()
        if params['MULTICORE']:
            print("Warming: multi-core is not supported with progsys "
                  "as fitness function.\n"
                  "Fitness function only allows sequential evaluation.")

    def evaluate(self, ind, **kwargs):
        dist = kwargs.get('dist', None)
        timeout = kwargs.get('timeout', params['PROGRAM_EVAL_TIMEOUT'])
        if dist is None:
            raise ValueError(f'dist is None. It must be either training or test to select the correct dataset type.')
        n_actual_train_examples = params['NUM_TRAIN_EXAMPLES']
        n_actual_test_examples = params['NUM_TEST_EXAMPLES']
        program = self.format_program(ind.phenotype,
                                      self.embed_header, self.embed_footer)

        if dist == "training":
            data = self.training
            data = '\n'.join([ss_data for ss_data in data.split('\n')])
            data += '\n'
            data += 'import warnings\n'
            data += 'warnings.filterwarnings("ignore", category=SyntaxWarning)\n'
            data += 'warnings.filterwarnings("ignore", category=RuntimeWarning)\n'
            data += 'warnings.filterwarnings("ignore", category=FutureWarning)\n'
            data += 'import random\n'
            data += 'indices = list(range(len(inval)))\n'
            data += f'random.Random(24 + 31 * {params["RANDOM_SEED"]} * {params["RANDOM_SEED"]}).shuffle(indices)\n'
            data += 'new_inval = []\n'
            data += 'new_outval = []\n'
            data += f'indices = indices[:{n_actual_train_examples}]\n'
            data += f'for iii in indices:\n'
            data += '  new_inval.append(inval[iii])\n'
            data += '  new_outval.append(outval[iii])\n'
            data += 'inval = new_inval\n'
            data += 'outval = new_outval\n'
        elif dist == "test":
            data = self.test
            data = '\n'.join([ss_data + f"[:{n_actual_test_examples}]" for ss_data in data.split('\n')])
            data += '\n'
            data += 'import warnings\n'
            data += 'warnings.filterwarnings("ignore", category=SyntaxWarning)\n'
            data += 'warnings.filterwarnings("ignore", category=RuntimeWarning)\n'
            data += 'warnings.filterwarnings("ignore", category=FutureWarning)\n'
        else:
            raise ValueError(f'{dist} is not a valid dist. It must be either training or test.')

        program = "{}\n{}\n".format(data, program)

        result = {}
        args = (program, Queue())
        worker = Process(target=progimpr.exec_single_program, args=args)
        worker.start()
        try:
            worker.join(timeout=timeout)
            if worker.is_alive():
                worker.terminate()
                worker.join()
                worker.close()
                raise Exception('Process timed out')
            
            try:
                worker_res = args[1].get(block=True, timeout=2)
            except queue.Empty:
                result = {'exception': str(traceback.format_exc())}
            else:
                result = worker_res
                args[1].close()
        
        except Exception as e:
            result = {'exception': str(traceback.format_exc())}

        if 'quality' in result and 'caseQuality' in result:
            result['quality'] = progimpr.eventually_compute_penalty(result['quality'], result['caseQuality'])

        if 'quality' in result:
            result['quality'] = progimpr.cap_globally_very_large_fitness(result['quality'])

        if 'quality' not in result:
            result['quality'] = progimpr.set_globally_very_large_fitness()

        if dist == 'training':
            ind.levi_errors = result['caseQuality'] if 'caseQuality' in result else None
        return result['quality']

    @staticmethod
    def exec_single_program(*args):
        program = args[0]
        queue = args[1]
        try:
            exec(program, globals())
            result = {'quality': quality, 'caseQuality': caseQuality} # type: ignore
            queue.put(result)
        except Exception as e:
            result = {'exception': str(traceback.format_exc())}
            queue.put(result)

    @staticmethod
    def eventually_compute_penalty(base_fitness, errors):
        num_test_cases_not_passed = sum([int(error > 0) for error in errors])
        if params['FITNESS_FILE'].endswith('penalty.txt'):
            fitness = min(base_fitness, params['WORST_POSSIBLE_FITNESS'])
            fitness += params['WORST_POSSIBLE_FITNESS'] * num_test_cases_not_passed
            return fitness
        elif params['FITNESS_FILE'].endswith('lexi.txt'):
            return [num_test_cases_not_passed, base_fitness]
        else:
            return base_fitness

    @staticmethod
    def set_default_fitness(default_fitness):
        if params['FITNESS_FILE'].endswith('lexi.txt'):
            return [np.inf, np.inf]
        else:
            return default_fitness

    @staticmethod
    def set_globally_very_large_fitness():
        if params['FITNESS_FILE'].endswith('lexi.txt'):
            return [params['WORST_POSSIBLE_FITNESS_GLOBALLY_EVER'], params['WORST_POSSIBLE_FITNESS_GLOBALLY_EVER']]
        else:
            return params['WORST_POSSIBLE_FITNESS_GLOBALLY_EVER']

    @staticmethod
    def cap_globally_very_large_fitness(fitness):
        if params['FITNESS_FILE'].endswith('lexi.txt'):
            new_fitness = []
            for f in fitness:
                if f > params['WORST_POSSIBLE_FITNESS_GLOBALLY_EVER']:
                    new_fitness.append(params['WORST_POSSIBLE_FITNESS_GLOBALLY_EVER'])
                else:
                    new_fitness.append(f)
            return new_fitness
        else:
            if fitness > params['WORST_POSSIBLE_FITNESS_GLOBALLY_EVER']:
                return params['WORST_POSSIBLE_FITNESS_GLOBALLY_EVER']
            else:
                return fitness

    @staticmethod
    def create_eval_process():
        """create separate python process for evaluation"""
        return Popen([sys.executable, 'scripts/python_script_evaluation.py'],
                     stdout=PIPE, stdin=PIPE)

    def format_program(self, individual, header, footer):
        """formats the program by formatting the individual and adding
        a header and footer"""
        last_new_line = header.rindex('\n')
        #indent = header[last_new_line + len('\n'):len(header)]
        #individual1 = individual[3:]
        #individual1 = individual1[:-2]
        individual = individual.replace('#', '\n')
        individual = individual.replace("print", "") # HACK
        return header + self.format_individual(individual) + footer

    def format_individual(self, code, additional_indent=""):
        """format individual by adding appropriate indentation and loop break
        statements"""
        parts = code.split('\n')
        indent = 0
        string_builder = ""
        for_counter_number = 0
        first = True
        for part in parts:
            line = part.strip()
            # remove indentation if bracket is at the beginning of the line
            while line.startswith(":}"):
                indent -= 1
                line = line[2:].strip()

            # add indent
            if not first:
                string_builder += additional_indent
            else:
                first = False

            for i in range(0, indent):
                string_builder += self.INDENTSPACE

            # add indentation
            while line.endswith("{:"):
                indent += 1
                line = line[:len(line) - 2].strip()
            # remove indentation if bracket is at the end of the line
            while line.endswith(":}"):
                indent -= 1
                line = line[:len(line) - 2].strip()

            if self.LOOPBREAKUNNUMBERED in line:
                if self.LOOPBREAK_INITIALISE in line:
                    line = ""  # remove line
                elif self.LOOPBREAK_IF in line:
                    line = line.replace(self.LOOPBREAKUNNUMBERED,
                                        self.LOOPBREAK)
                elif self.LOOPBREAK_INCREMENT in line:
                    line = line.replace(self.LOOPBREAKUNNUMBERED,
                                        self.LOOPBREAK)
                else:
                    raise Exception("Python 'while break' is malformed.")
            elif self.FORCOUNTERUNNUMBERED in line:
                line = line.replace(self.FORCOUNTERUNNUMBERED,
                                    self.FORCOUNTER + str(for_counter_number))
                for_counter_number += 1

            # add line to code
            string_builder += line
            string_builder += '\n'
        return string_builder

    def get_data(self, train, test, grammar):
        """ Return the training and test data for the current experiment.
        A new get_data method is required to load from a sub folder and to
        read the embed file"""
        train_set = path.join("PonyGE2", "datasets", "progsys", train)
        test_set = path.join("PonyGE2", "datasets", "progsys", test)

        embed_file = path.join("PonyGE2", "fitness_eval", "base_eval.txt")
        with open(embed_file, 'r') as embed:
            embed_code = embed.read()
        embed_code = embed_code.replace(self.INSERTFITNESSFUNCTION, self.fitness_function)
        insert = embed_code.index(self.INSERTCODE)
        embed_header, embed_footer = "", ""
        if insert > 0:
            embed_header = embed_code[:insert]

            llm_data = read_json(
                full_path='llm_results/',
                model_name=params['MODEL_NAME'],
                problem_benchmark=params['BENCHMARK_NAME'],
                problem_benchmark_type=params['BENCHMARK_TYPE'],
                problem_id=params['PROBLEM_INDEX'],
                reask=False,
                iterations=params['LLM_ITERATIONS'],
                repeatitions=0,
                train_size=params['NUM_TRAIN_EXAMPLES'],
                test_size=params['NUM_TEST_EXAMPLES']
            )["data_preprocess"]
            llm_data_supports = []
            llm_data_imports = []
            for curr_data in llm_data:
                if "supports" not in curr_data:
                    curr_data["supports"] = []
                if "imports" not in curr_data:
                    curr_data["imports"] = []
                for lol in curr_data["supports"]:
                    lol = lol.replace('\t', self.INDENTSPACE)
                    if lol not in llm_data_supports:
                        llm_data_supports.append(lol)
                for lol in curr_data["imports"]:
                    if lol not in llm_data_imports:
                        llm_data_imports.append(lol)

            embed_header = embed_header.replace(self.INSERTIMPORTS, '\n'.join(llm_data_imports))
            embed_header = embed_header.replace(self.INSERTSUPPORTS, '\n'.join(llm_data_supports))

            embed_footer = embed_code[insert + len(self.INSERTCODE):]  # NOTE
        with open(train_set, 'r') as train_file, \
                open(test_set, 'r') as test_file:
            return train_file.read(), test_file.read(), \
                embed_header, embed_footer

    def get_fitness_eval(self, fitness_file):
        if fitness_file == None:
            s = "You must provide a file with a fitness function; " \
                "you can find some examples in fitness_eval folder."
            raise Exception(s)
        fitness_file = path.join(
            "PonyGE2", "fitness_eval", fitness_file)
        if not path.exists(fitness_file):
            s = "Invalid fitness function file"
            raise Exception(s)
        with open(fitness_file, 'r') as file:
            return file.read()
