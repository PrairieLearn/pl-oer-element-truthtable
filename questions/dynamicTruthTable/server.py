import random

def generate(data):
    q1Operator = random.choice(["and", "or"])
    q1TableData = {
        "and" : "[0,0,0,1]", 
        "or" : "[0,1,1,1]"
    }
    # Option 1: Setting correct_answers 
    data["params"]["q1-text"] = q1Operator
    data["correct_answers"]["q1"] = q1TableData[q1Operator]


    # Option 2: HTML injected parameters

    # For each operator, define number of inputs, textual connector, and table output
    q2TableData = random.choice([
        [3, " and ", "[0,0,0,0,0,0,0,1]"], 
        [3, " or ", "[0,1,1,1,1,1,1,1]"], 
        [2, " and ", "[0,0,0,1]"], 
        [2, " or ", "[0,1,1,1]"], 
        [2, " xor ", "[0,1,1,0]"]
    ])
    
    q2Inputs = random.sample(["X", "Y", "Z"], k=q2TableData[0])
    
    data["params"]["q2-input-names"] = f"[{','.join(q2Inputs)}]"
    data["params"]["q2-output-names"] = f"[{q2TableData[1].join(q2Inputs)}]"
    data["params"]["q2-correct-answer"] = q2TableData[2]

    return data