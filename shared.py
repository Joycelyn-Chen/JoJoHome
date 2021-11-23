import os
import random

MAIN_FONT = ('Comic Sans MS', 50, 'bold')
FONT = ('Comic Sans MS', 20, 'bold')

JOYFULNESS = """
 ^ ^
(·_·)
/| |\\
 - -
"""

def print_message(message):
    print("{}\n\n{}\n\n{}\n".format(message, patient_quote(), JOYFULNESS))

def patient_quote():
    quotes = ["Be patient when you are frustrated. \nBe silent when you are angry.\nBe brave when you are confronted with challenges.", 
    "Everything comes to you in the right moment. \n\nBe patient.\nBe grateful.", 
    "Be patient and tough;\nOne day this pain will be useful to you.", 
    "Be positive and trust the timing of everything. \nJust because it’s not happening right now doesn’t mean it never will.\nStay patient.", 
    "Have patient with all things.\nBut first of all, with YOURSELF.", 
    "Patient is a key element of success.", 
    "Patient is more than simply learning to wait.\nIt is having learned what is worth your time.", 
    "Be patient.\nThe best things happen unexpectedly.", 
    "Everything you deserve will be yours, be patient."]
    return quotes[random.randint(0, len(quotes) - 1)]

def check_folder(log_dir):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    return log_dir

def check_args(args):
    check_folder(os.path.join(args.root_dir))
    return args