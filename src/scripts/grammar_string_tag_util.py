import string
import re
from transformers import AutoTokenizer
import nltk
from nltk.probability import FreqDist
from nltk.corpus import brown
from typing import List, Dict, Union, Optional, Any

# --- NLTK Resource Download Utility (Conditional Verbosity) ---
def download_nltk_resources(verbose: bool = False):
    """
    Checks and downloads necessary NLTK resources if not already present.
    Prints messages only if verbose is True.
    """
    resources_to_check = {
        'words': 'corpora/words',
        'brown': 'corpora/brown',
        'punkt': 'tokenizers/punkt'
    }
    if verbose:
        print("\n--- Checking NLTK Resources ---")
    for name, path in resources_to_check.items():
        try:
            nltk.data.find(path)
            if verbose:
                print(f"NLTK resource '{name}' already present.")
        except nltk.downloader.DownloadError:
            if verbose:
                print(f"NLTK resource '{name}' not found. Downloading...")
            nltk.download(name, quiet=not verbose) # Show NLTK download output if verbose
            if verbose:
                print(f"Download of '{name}' complete.")
    if verbose:
        print("--- NLTK Resource Check Complete ---")


# --- Word Frequency Calculation (Conditional Verbosity) ---
def get_word_frequencies(corpus: nltk.corpus.CorpusReader, verbose: bool = False) -> FreqDist:
    """
    Calculates word frequencies from a given NLTK corpus.
    Prints messages only if verbose is True.
    """
    if verbose:
        corpus_name = corpus.readme().splitlines()[0] if hasattr(corpus, 'readme') else 'selected NLTK corpus'
        print(f"\nCalculating word frequencies from '{corpus_name}'...")
    
    # Consider only alphabetic words, converted to lowercase
    words_in_corpus = [word.lower() for word in corpus.words() if word.isalpha()]
    fdist = FreqDist(words_in_corpus)
    
    if verbose:
        print(f"Calculated frequencies for {len(fdist)} unique words (alphabetic only, lowercase).")
    return fdist

# --- Tokenizer and Vocabulary Loading (Conditional Verbosity) ---
def load_tokenizer_and_vocab(model_name: str, verbose: bool = False) -> tuple[Optional[Any], Optional[Dict[str, int]]]:
    """
    Loads the tokenizer and returns its vocabulary.
    Prints messages only if verbose is True.
    """
    if verbose:
        print(f"\nLoading tokenizer: {model_name}...")
    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        vocab = tokenizer.get_vocab()  # Token string -> ID
        if verbose:
            print(f"Vocabulary loaded with {len(vocab)} tokens.")
        return tokenizer, vocab
    except Exception as e:
        print(f"Error loading tokenizer '{model_name}': {e}") # Errors should generally be reported
        return None, None

# --- Token Type Checkers ---
def is_punctuation(token: str) -> bool:
    """Checks if the token consists entirely of punctuation."""
    return all(char in string.punctuation for char in token) and bool(token)

def is_number_token(token: str) -> bool:
    """Checks if the token represents a number (not starting with ##)."""
    if token.startswith("##"):
        return False
    try:
        float(token)
        return True
    except ValueError:
        return False

# --- Token Categorization (Conditional Verbosity) ---
def categorize_tokens(vocab_tokens: List[str], special_tokens_list: List[str], 
                      english_alphabet_set: set, verbose: bool = False) -> Dict[str, List[str]]:
    """
    Categorizes tokens from the vocabulary.
    Prints messages only if verbose is True.
    """
    if verbose:
        print("\nCategorizing tokens...")
    
    categories = {
        "special": [],
        "single_letters": [],
        "hash_prefixed": [],
        "punctuation": [],
        "numbers": [],
        "normal_words": [],
        "other": []
    }

    for token in vocab_tokens:
        if token in special_tokens_list:
            categories["special"].append(token)
        elif len(token) == 1 and token.lower() in english_alphabet_set:
            categories["single_letters"].append(token)
        elif token.startswith("##"):
            categories["hash_prefixed"].append(token)
        elif is_punctuation(token):
            categories["punctuation"].append(token)
        elif is_number_token(token):
            categories["numbers"].append(token)
        elif token.isalpha():
            # Ensure single letters already caught aren't re-added here
            if not (len(token) == 1 and token.lower() in english_alphabet_set):
                 categories["normal_words"].append(token)
        else:
            categories["other"].append(token)
    
    if verbose:
        print("Token categorization complete.")
    return categories

# --- Filter for Hash-Prefixed Tokens by Form (Conditional Verbosity) ---
def filter_hash_prefixed_tokens_by_form(hash_tokens: List[str], verbose: bool = False) -> tuple[List[str], List[str]]:
    """
    Filters '##' prefixed tokens. Keeps only those where the sub-word is purely alphabetic.
    Prints messages only if verbose is True.
    """
    if verbose:
        print("\nFiltering 'hash_prefixed' tokens (Rule: sub-word after '##' must be purely alphabetic)...")
    
    kept_tokens = []
    removed_tokens = []
    for token in hash_tokens:
        if len(token) <= 2:  # Token is "##" or shorter
            removed_tokens.append(token + " (too short or just '##')")
            continue
        sub_word = token[2:]
        if not sub_word.isalpha():
            removed_tokens.append(token + f" (sub-word '{sub_word}' is not purely alphabetic)")
            continue
        kept_tokens.append(token)
        
    if verbose:
        print(f"Filtering 'hash_prefixed' by form complete: {len(kept_tokens)} kept, {len(removed_tokens)} removed.")
    return kept_tokens, removed_tokens

# --- Filter List by Frequency (Conditional Verbosity) ---
def filter_list_by_frequency(token_list: List[str], fdist: FreqDist, 
                             min_occurrences: int, is_hash_prefixed_list: bool = False, 
                             verbose: bool = False) -> tuple[List[str], List[str]]:
    """
    Filters a list of tokens based on word/sub-word frequency.
    Prints messages only if verbose is True and for high-level summary.
    """
    if not token_list:
        return [], []

    kept_tokens_freq = []
    removed_tokens_freq = []

    for token in token_list:
        string_to_check_freq = token[2:].lower() if is_hash_prefixed_list else token.lower()
        frequency = fdist.get(string_to_check_freq, 0)
        
        if frequency >= min_occurrences:
            kept_tokens_freq.append(token)
        else:
            if verbose: # Log individual removals only if verbose (can be many)
                 # For brevity, we won't print each removed token here to avoid flooding
                 # but we will store it for a summary later if needed.
                 pass
            removed_tokens_freq.append(token + f" (element: '{string_to_check_freq}' freq: {frequency} < {min_occurrences})")
            
    return kept_tokens_freq, removed_tokens_freq


# --- Main Function to Extract and Filter Tokenizer Vocabulary ---
def extract_and_filter_tokenizer_vocab(
    model_name: str,
    min_word_frequency: int,
    verbose: bool = False,
    return_lists: bool = True,
    categories_to_return: Optional[List[str]] = None,
    max_examples_to_print_verbose: int = 5
) -> Dict[str, Union[List[str], str]]:
    """
    Extracts, categorizes, and filters a tokenizer's vocabulary.

    Args:
        model_name (str): Name of the Hugging Face tokenizer model.
        min_word_frequency (int): Minimum frequency for a word/sub-word to be kept.
        verbose (bool): If True, prints detailed logs during processing.
        return_lists (bool): If True, returns lists of tokens. 
                             If False, returns pipe-separated strings of tokens.
        categories_to_return (Optional[List[str]]): Specific categories to return.
                                                   If None, returns a default set of processed categories.
        max_examples_to_print_verbose (int): Max examples to print for each category if verbose.

    Returns:
        Dict[str, Union[List[str], str]]: A dictionary where keys are category names
                                          and values are lists of tokens or pipe-separated strings.
    """

    download_nltk_resources(verbose=verbose)
    
    # Static resources
    english_alphabet_set = set(string.ascii_lowercase)
    word_freq_dist = get_word_frequencies(brown, verbose=verbose) # Using NLTK's Brown corpus

    tokenizer, vocab = load_tokenizer_and_vocab(model_name, verbose=verbose)
    if not tokenizer or not vocab:
        return {"error": f"Could not load tokenizer or vocabulary for {model_name}."}

    all_vocab_tokens = list(vocab.keys())
    special_tokens_list = tokenizer.all_special_tokens
    
    if verbose:
        print(f"\nIdentified special tokens from tokenizer ({len(special_tokens_list)}):")
        print(special_tokens_list[:max_examples_to_print_verbose], "..." if len(special_tokens_list) > max_examples_to_print_verbose else "")

    # 1. Initial Categorization
    categorized_tokens = categorize_tokens(all_vocab_tokens, special_tokens_list, english_alphabet_set, verbose=verbose)

    if verbose:
        print("\n--- Token Categories (Before Specific & Frequency Filters) ---")
        for cat_name, tk_list in categorized_tokens.items():
            label = cat_name.replace("_", " ").capitalize()
            print(f"\nCategory: {label} (Total: {len(tk_list)})")
            if tk_list:
                print(f"  Examples: {tk_list[:max_examples_to_print_verbose]}", "..." if len(tk_list) > max_examples_to_print_verbose else "")

    # 2. Specific filter for 'hash_prefixed' tokens (by form)
    original_hash_tokens = categorized_tokens["hash_prefixed"]
    valid_form_hash_tokens, removed_by_form_hash_tokens = filter_hash_prefixed_tokens_by_form(original_hash_tokens, verbose=verbose)
    
    # Prepare structure for final filtered lists
    final_lists = {
        "special": categorized_tokens["special"],
        "single_letters": categorized_tokens["single_letters"],
        "upper_single_letters": [ch.upper() for ch in categorized_tokens["single_letters"]],
        "punctuation": categorized_tokens["punctuation"],
        "numbers": categorized_tokens["numbers"],
        "other": categorized_tokens["other"],
        "normal_words_original": categorized_tokens["normal_words"], # For reference
        "normal_words_frequent": [],
        "hash_prefixed_original": categorized_tokens["hash_prefixed"], # For reference
        "hash_prefixed_valid_form": valid_form_hash_tokens, # After form filter
        "hash_prefixed_frequent_subword": [],
    }

    # Store details of removed tokens if verbose (for potential detailed logging)
    removed_tokens_log = {
        "hash_prefixed_invalid_form": removed_by_form_hash_tokens,
        "normal_words_infrequent": [],
        "hash_prefixed_infrequent_subword": [],
    }

    # 3. Frequency Filtering
    if verbose:
        print(f"\n--- Frequency Filtering (Threshold: >= {min_word_frequency} occurrences) ---")
    
    if verbose: print(f"  Filtering 'normal_words' by frequency...")
    frequent_normal_words, infrequent_normal_words = filter_list_by_frequency(
        final_lists["normal_words_original"], word_freq_dist, min_word_frequency, False, verbose=False # Verbose for sub-steps can be too much
    )
    final_lists["normal_words_frequent"] = frequent_normal_words
    removed_tokens_log["normal_words_infrequent"] = infrequent_normal_words
    if verbose: 
        print(f"    'normal_words': {len(frequent_normal_words)} kept, {len(infrequent_normal_words)} removed by frequency filter.")

    if verbose: print(f"  Filtering 'hash_prefixed_valid_form' by sub-word frequency...")
    frequent_hash_tokens, infrequent_hash_tokens = filter_list_by_frequency(
        final_lists["hash_prefixed_valid_form"], word_freq_dist, min_word_frequency, True, verbose=False
    )
    final_lists["hash_prefixed_frequent_subword"] = frequent_hash_tokens
    removed_tokens_log["hash_prefixed_infrequent_subword"] = infrequent_hash_tokens
    if verbose:
        print(f"    'hash_prefixed_valid_form': {len(frequent_hash_tokens)} kept, {len(infrequent_hash_tokens)} removed by sub-word frequency filter.")

    # Define default categories to return if not specified
    if categories_to_return is None:
        categories_to_return = [
            "special", "single_letters", "upper_single_letters", "punctuation", "numbers", "other",
            "normal_words_frequent", "hash_prefixed_frequent_subword"
        ]
    
    # Prepare the output dictionary
    result_output: Dict[str, Union[List[str], str]] = {}

    if verbose:
        print("\n\n--- FINAL TOKEN CATEGORY SUMMARY (Lists) ---")
        print(f"(Minimum frequency threshold used: {min_word_frequency})")
        for cat_name_key in categories_to_return:
            if cat_name_key in final_lists:
                tk_list = final_lists[cat_name_key]
                label = cat_name_key.replace("_", " ").capitalize()
                print(f"\nCategory: {label} (Total: {len(tk_list)})")
                if tk_list:
                    print(f"  Examples: {tk_list[:max_examples_to_print_verbose]}", "..." if len(tk_list) > max_examples_to_print_verbose else "")
                else:
                    print("  No tokens in this category (or category not populated).")
            else:
                 print(f"\nCategory: {cat_name_key.replace('_', ' ').capitalize()} (not available in final_lists)")


    for category_key in categories_to_return:
        if category_key in final_lists:
            token_list_for_category = final_lists[category_key]
            if return_lists:
                result_output[category_key] = token_list_for_category
            else:
                # Escape tokens if they are to be used in regex, otherwise simple join
                # For now, simple join. For regex, use: "|".join(map(re.escape, token_list_for_category))
                result_output[category_key] = "|".join(token_list_for_category)
        else:
            # If a requested category is not in final_lists (e.g., typo or intermediate list)
            result_output[category_key] = [] if return_lists else ""
            if verbose:
                print(f"Warning: Requested category '{category_key}' not found in processed lists. Returning empty.")
    
    if verbose:
        print("\n\n--- DETAILS OF REMOVED TOKENS (Examples) ---")
        for key, val_list in removed_tokens_log.items():
            label = key.replace('_', ' ').capitalize()
            print(f"\n{label} ({len(val_list)}):")
            if val_list:
                 print(f"  Example Removed Tokens: {val_list[:max_examples_to_print_verbose]}", "..." if len(val_list) > max_examples_to_print_verbose else "")
            else:
                print("  None removed in this step / category.")
        print("\n--- Processing Complete ---")
        
    return result_output


# --- Example Usage ---
# if __name__ == "__main__":
#     MODEL = "bert-base-uncased"
#     MIN_FREQ = 100 # Stricter frequency for this example
#     MAX_EXAMPLES = 3 # For verbose output during example run

#    print("--- Example 1: Get lists, verbose output ---")
#    results_lists_verbose = extract_and_filter_tokenizer_vocab(
#        model_name=MODEL,
#        min_word_frequency=MIN_FREQ,
#        verbose=True,
#        return_lists=True,
#        categories_to_return=["normal_words_frequent", "single_letters", "punctuation", "hash_prefixed_frequent_subword"],
#        max_examples_to_print_verbose=MAX_EXAMPLES
#    )
#    print("\n--- Results from Example 1 (Lists, Verbose) ---")
#    if "error" in results_lists_verbose:
#        print(results_lists_verbose["error"])
#    else:
#        for category, data in results_lists_verbose.items():
#            print(f"\nCategory: {category} (Type: {type(data)}, Count: {len(data)})")
#            if isinstance(data, list) and data:
#                print(f"  Examples: {data[:MAX_EXAMPLES]}", "..." if len(data) > MAX_EXAMPLES else "")
#            elif isinstance(data, str) and data: # Should not happen if return_lists=True
#                print(f"  Content (partial): {data[:70]}...")

#     print("\n\n--- Example 2: Get strings, non-verbose output, specific categories ---")
#     results_strings_quiet = extract_and_filter_tokenizer_vocab(
#         model_name=MODEL,
#         min_word_frequency=MIN_FREQ,
#         verbose=False,
#         return_lists=False,
#         categories_to_return=["normal_words_frequent", "single_letters", "punctuation"]
#     )
#     print("\n--- Results from Example 2 (Strings, Quiet) ---")
#     if "error" in results_strings_quiet:
#         print(results_strings_quiet["error"])
#     else:
#         for category, data_str in results_strings_quiet.items():
#             print(f"\nCategory: {category} (Type: {type(data_str)})")
#             if data_str: # Print only if not empty
#                 print(f"  Joined String (first 70 chars): {data_str[:70]}{'...' if len(data_str) > 70 else ''}")
#             else:
#                 print("  (Empty list or string)")

#    print("\n\n--- Example 3: Get all default categories as strings, non-verbose ---")
#    results_all_strings_quiet = extract_and_filter_tokenizer_vocab(
#        model_name=MODEL,
#        min_word_frequency=MIN_FREQ, # Using the same frequency
#        verbose=False,
#        return_lists=False,
#        categories_to_return=None # Request default set
#    )
#    print("\n--- Results from Example 3 (All Default Categories, Strings, Quiet) ---")
#    if "error" in results_all_strings_quiet:
#        print(results_all_strings_quiet["error"])
#    else:
#        for category, data_str in results_all_strings_quiet.items():
#            print(f"\nCategory: {category}")
#            if data_str:
#                 print(f"  Joined String (first 70 chars): {data_str[:70]}{'...' if len(data_str) > 70 else ''}")
#            else:
#                print("  (Empty list or string)")

    # Your specific usage from the end of the previous script:
#    if "normal_words_frequent" in results_lists_verbose and isinstance(results_lists_verbose["normal_words_frequent"], list):
#        print(f"\n\n--- Your specific output format example (from verbose list results) ---")
#        frequent_normal_list = results_lists_verbose["normal_words_frequent"]
#        print(f"Length of 'normal_words_frequent': {len(frequent_normal_list)}")
        # frequent_normal_str_quoted = ' | '.join([f"'{ch}'" for ch in frequent_normal_list]) # Careful with very long lists
        # print(f"Quoted Joined frequent_normal (first 100 chars): {frequent_normal_str_quoted[:100]}...")
    
#    if "hash_prefixed_frequent_subword" in results_lists_verbose and isinstance(results_lists_verbose["hash_prefixed_frequent_subword"], list):
#        frequent_hash_list = results_lists_verbose["hash_prefixed_frequent_subword"]
#        print(f"Length of 'hash_prefixed_frequent_subword': {len(frequent_hash_list)}")

#    if "single_letters" in results_lists_verbose and isinstance(results_lists_verbose["single_letters"], list):
#        single_letters_list = results_lists_verbose["single_letters"]
#        print(f"Length of 'single_letters': {len(single_letters_list)}")