"""
Programmer: Chris Tralie
Purpose: Some utilities to help with debugging, including conversion to
JFLAP and a method to test all strings up to a certain size in an alphabet
against Python's built-in regular expression evaluator
"""

import numpy as np

def get_state_info(delta, width):
    """
    Determine the states and their ids/positions

    Parameters
    ----------
    delta: Dictionary: (String, String) -> String
        Transition function from (state, character) -> state
        Assumed to follow the naming conventions in HW4
    width: float
        Width in which to put states
    
    Returns
    -------
    pos: string->(float, float)
        Positions of each state
    ids: string->int
        IDs of each state
    """
    states = set([key[0] for key in delta.keys()])
    for v in delta.values():
        states.update(v)
    if not "Finish" in states:
        raise KeyError("JFLAP renderer expects a state called 'Finish' in the transitions")
    if not "Start" in states:
        raise KeyError("JFLAP renderer expects a state called 'Start' in the transitions")
    counts = [sum([c == "_" for c in key]) for key in states]
    ## Step 1: Figure out order of singleton keys
    keys_single = [key for (key, count) in zip(states, counts) if count == 1]
    keys_single = sorted(keys_single, key=lambda x: int(x[2::]))
    following = {k:[] for k in keys_single}

    for k in keys_single:
        for k2 in states:
            if len(k2) > len(k) and k2[0:len(k)] == k:
                following[k].append(k2)
    
    ids = {}
    idx = 1
    for k in keys_single:
        ids[k] = idx
        idx += 1
        for k2 in sorted(following[k], key=lambda x: -len(x)):
            ids[k2] = idx
            idx += 1
    ids["Start"] = 0
    ids["Finish"] = len(ids)+1
    pos = {}
    for k, id in ids.items():
        theta = np.pi*id/len(ids)
        pos[k] = (width*(1-np.cos(theta)), width*np.sin(theta))
    return pos, ids
    


def write_dfa_jflap(delta, filename):
    """
    Programmer: Chris Tralie
    Convert a python dictionary describing DFA transitions into
    XML that JFLAP understands

    Parameters
    ----------
    delta: Dictionary: (String, String) -> String
        Transition function from (state, character) -> state
        Assumed to follow the naming conventions in HW4
    filename: string
        Path to which to write JFLAP file
    """
    import numpy as np
    BEGIN_JFF = """<?xml version="1.0" encoding="UTF-8" standalone="no"?><!--Created with substring.py in Ursinus College CS 373--><structure>
        <type>fa</type>
        <automaton>"""
    ## Step 1: Setup the states
    jff_string = "" + BEGIN_JFF
    states_xml = ""

    delta_orig = delta
    # Convert to (State):(Character:State)
    delta = {}
    for (state, c), state_to in delta_orig.items():
        if not state in delta:
            delta[state] = {}
        delta[state][c] = state_to
    pos, ids = get_state_info(delta_orig, width=400)
    states = list(pos.keys())

    ## Step 1b: Setup state positions
    for state in states:
        id = ids[state]
        (x, y) = pos[state]
        d = ""
        if state == "Start":
            d = "<initial/>"
        if state == "Finish":
            d = "<final/>"
        states_xml += "<state id=\"{}\" name=\"{}\">\n    <x>{}</x>    <y>{}</y>\n{}</state>".format(id, state, x, y, d)
    ## Step 2: Setup the transitions
    jff_string += states_xml
    for state_from in delta.keys():
        state_from_id = ids[state_from]
        for c in delta[state_from].keys():
            for state_to in delta[state_from][c]:
                state_to = ids[state_to]
                jff_string += "<transition>\n    <from>{}</from>\n    <to>{}</to>\n    ".format(state_from_id, state_to)
                if c:
                    jff_string += "<read>{}</read>".format(c)
                else:
                    # Lambda arrow
                    jff_string += "<read/>"
                jff_string += "</transition>\n"
    jff_string += "</automaton></structure>"
    fout = open(filename, "w")
    fout.write(jff_string)
    fout.close()


def cmp_python(rexp, Sigma, max_len):
    """
    Compare the results of evaluating a regular expression
    on all strings using an alphabet up to a particular length

    Parameters
    ----------
    rexp: string
        The regular expression
    Sigma: list of char
        The alphabet
    max_len: int
        Maximum length of string
    """
    from re import fullmatch # Python's version
    from mygrep import eval_regexp
    queue = [""]
    finished = False
    # Go through strings in lexicographic order, as per the order in Sigma
    correct = 0
    tried = 0
    while not finished:
        s = queue.pop(0)
        if len(s) > max_len:
            finished = True
        else:
            tried += 1
            myres = eval_regexp(rexp, s)
            pyres = fullmatch(rexp, s) is not None
            if myres != pyres:
                print("Wrong on {}: Mine {}, Python {}".format(s, myres, pyres))
            else:
                correct += 1
            for c in Sigma:
                queue.append(s+c)
    print("{} / {} Correct on {} up to length {}".format(correct, tried, rexp, max_len))