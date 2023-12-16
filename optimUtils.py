import os
import pandas as pd
import logging

def split_prompt(text):
    """
    grabs all text up to the first occurrence of ':'
    uses the grabbed text as a sub-prompt
    """
    try:
        if ":" in text:
            idx = text.index(":") # first occurrence from start
            # grab up to index as sub-prompt
            prompt = text[:idx]
            # remove from main text
            text = text[idx+1:]
        else: # no : found
            if len(text) > 0: # there is still text though
                # take remainder as weight 1
                prompt = text
                text = ""
        return prompt, text
    except Exception as e:
        logging.error(f"Error in split_prompt: {e}")
        raise

def get_weight(text):
    """
    takes the value following ':' as weight
    if ':' has no value defined, defaults to 1.0
    """
    try:
        if " " in text:
            idx = text.index(" ") # first occurence
        else: # no space, read to end
            idx = len(text)
        if idx != 0:
            try:
                weight = float(text[:idx])
            except: # couldn't treat as float
                logging.warning(f"Warning: '{text[:idx]}' is not a value, are you missing a space?")
                weight = 1.0
        else: # no value found
            weight = 1.0
        # remove from main text
        text = text[idx+1:]
        return weight, text
    except Exception as e:
        logging.error(f"Error in get_weight: {e}")
        raise

def split_weighted_subprompts(text):
    """
    grabs all text up to the first occurrence of ':'
    uses the grabbed text as a sub-prompt, and takes the value following ':' as weight
    if ':' has no value defined, defaults to 1.0
    repeats until no text remaining
    """
    try:
        remaining = len(text)
        prompts = []
        weights = []
        while remaining > 0:
            prompt, text = split_prompt(text)
            weight, text = get_weight(text)
            # append the sub-prompt and its weight
            prompts.append(prompt)
            weights.append(weight)
            remaining = len(text)
        return prompts, weights
    except Exception as e:
        logging.error(f"Error in split_weighted_subprompts: {e}")
        raise

def logger(params, log_csv):
    try:
        os.makedirs('logs', exist_ok=True)
        cols = [arg for arg, _ in params.items()]
        if not os.path.exists(log_csv):
            df = pd.DataFrame(columns=cols)
            df.to_csv(log_csv, index=False)

        df = pd.read_csv(log_csv)
        for arg in cols:
            if arg not in df.columns:
                df[arg] = ""
        df.to_csv(log_csv, index = False)

        li = {}
        cols = [col for col in df.columns]
        data = {arg:value for arg, value in params.items()}
        for col in cols:
            if col in data:
                li[col] = data[col]
            else:
                li[col] = ''

        df = pd.DataFrame(li,index = [0])
        df.to_csv(log_csv,index=False, mode='a', header=False)
    except Exception as e:
        logging.error(f"Error in logger: {e}")
        raise
# Unit tests for the refactored functions
def test_split_prompt():
    assert split_prompt("prompt:1.0") == ("prompt", "1.0")
    assert split_prompt("prompt") == ("prompt", "")

def test_get_weight():
    assert get_weight("1.0") == (1.0, "")
    assert get_weight("2.0 prompt") == (2.0, "prompt")

def test_split_weighted_subprompts():
    assert split_weighted_subprompts("prompt:1.0") == (["prompt"], [1.0])
    assert split_weighted_subprompts("prompt1:2.0 prompt2:3.0") == (["prompt1", "prompt2"], [2.0, 3.0])