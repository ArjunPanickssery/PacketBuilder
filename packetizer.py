import os
import pandas as pd
from random import shuffle
import re

import sys
sys.setrecursionlimit(3000)

def get_lines_from_txt(filename):
    with open(filename, encoding='utf8') as f:
        content = f.readlines()
    return [x.strip() for x in content]
 
def get_settings_data():
    lines = get_lines_from_txt('settings.txt')
    file = lines[0].split(' ==> ')[1]
    set_name = lines[1].split(' ==> ')[1]
    return file, set_name

FILE, SET_NAME = get_settings_data()

# Certain categories (e.g. trash) are not acceptable fo
# the beginning or ending of a set
BAD_ENDS = ['geography', 'other', 'trash', 'current', 'geo', 'pop']

def extract_data(filename):
    lines = get_lines_from_txt(filename)
    tu_lines = []
    b_lines = []
    
    cutoff = 0
    for i in range(len(lines)):
        line = lines[i]
        if line == ',,,,,,,,,,,,,':
            cutoff = i + 1
            break
        tu_lines.append(line)
    for i in range(cutoff, len(lines)):
        line = lines[i]
        if line == ',,,,,,,,,,,,,':
            break
        b_lines.append(line)
        
    wp_t = open('tossups_' + FILE, 'w', encoding="utf8")
    wp_b = open('bonuses_' + FILE, 'w', encoding="utf8")
    
    wp_t.write('\n'.join(tu_lines))
    wp_b.write('\n'.join(b_lines))
    
    wp_t.close()
    wp_b.close()
    
    tossups_df = pd.read_csv('tossups_' + FILE)
    bonuses_df = pd.read_csv('bonuses_' + FILE)
    
    tossups = []
    for i in range(len(tossups_df)):
        tossups.append(dict(tossups_df.iloc[i]))
    bonuses = []
    for i in range(len(bonuses_df)):
        bonuses.append(dict(bonuses_df.iloc[i]))

    tossups = [{'question': t['Tossup Question'], 
                'answer': t['Answer'], 
                'category':t['Category']} for t in tossups]
    bonuses = [{'lead_in': b['Bonus Leadin'],
                'question1': b['Bonus Part 1'],
                'question2': b['Bonus Part 2'],
                'question3': b['Bonus Part 3'],
                'answer1': b['Bonus Answer 1'],
                'answer2': b['Bonus Answer 2'],
                'answer3': b['Bonus Answer 3'],
                'category': b['Category']} for b in bonuses]
    
    os.remove("tossups_sample_qems_output.csv")
    os.remove("bonuses_sample_qems_output.csv")

    return tossups, bonuses


def arrange_packets(questions):
    number_of_questions = len(questions)
    number_of_packets = int(number_of_questions // 20)
    
    # If there are extra tossups beyond a multiple of 20, delete them I guess
    shuffle(questions)
    for i in range(number_of_questions % 20):
        questions.pop(0)
        
    cats_set = list(set([t['category'] for t in questions]))
    cat_counts = [[c, len([t for t in questions if t['category']==c])] for c in cats_set]
    major_cats_set = list(set([c.split()[0] for c in cats_set]))
    #major_cat_counts = [[c, len([t for t in questions if t['category'].split()[0]==c])] for c in major_cats_set]
        
    cats = {}
    for cat in cats_set:
        cats[cat] = [t for t in questions if t['category']==cat]
        shuffle(cats[cat])
    
    packets = []
    for i in  range(number_of_packets):
        packets.append([])
        
    for i in range(len(cat_counts)):
        cat = cat_counts[i][0]
        quantity = cat_counts[i][1]
        number_of_full_packets = quantity // number_of_packets
        
        for i in range(number_of_full_packets):
            for j in range(number_of_packets):
                packets[j].append(cats[cat].pop(0))
        
    major_cats = {}
    for major_cat in major_cats_set:
        major_cats[major_cat] = []
        
    for key in list(cats.keys()):
        cat = cats[key]
        major_cat = key.split()[0]
        major_cats[major_cat].extend(cat)
    
    excess_questions = []
    for key in list(major_cats.keys()):
        excess_questions.extend(major_cats[key])
    
    packet_number = 0
    for key in list(major_cats.keys()):
        for question in major_cats[key]:
            while len(packets[packet_number]) == 20:
                packet_number = packet_number + 1
                if packet_number == number_of_packets:
                    packet_number = 0
            packets[packet_number].append(question)
            packet_number = packet_number + 1
            if packet_number == number_of_packets:
                packet_number = 0
        
    return packets

def acceptable_config(tossups, bonuses, count):
    tc = [t['category'].split()[0] for t in tossups]
    bc = [b['category'].split()[0] for b in bonuses]
    
    # Tossup should not be the same as the bonus
    if count<2500:    
        for i in range(20):
            if tc[i] == bc[i]:
                return False

    # Tossup/Bonus should not appear twice in a row
    if count<2000:
        for i in range(19):
            if tc[i] == tc[i+1]:
                return False
            if bc[i] == bc[i+1]:
                return False
    
    # No geo/CE/trash in the last cycle
    if count<1500:
        for i in [19]:
            if tc[i].lower() in BAD_ENDS:
                return False
            if bc[i].lower() in BAD_ENDS:
                return False

    return True
        
def randomize_packet(tossups, bonuses, count):
    shuffle(tossups)
    shuffle(bonuses)
    
    if acceptable_config(tossups, bonuses, count):
        return tossups, bonuses
    return randomize_packet(tossups, bonuses, count+1)

# LaTex Part
def run_latex(tossups, bonuses, set_name, writers):
    import os, subprocess
    
    header = r'''\documentclass[]{article}
    \pagestyle{plain}
    \usepackage{multicol}
    \usepackage[margin=0.25in]{geometry}
    
    \setlength\parindent{0pt}
    
    \newcounter{tossupnumber}
    \newcounter{bonusnumber}
    
    \newcommand{\power}[1]{\textbf{#1}}
    \newcommand{\pronunciationguide}[1]{{\small \texttt{#1}}}
    \newcommand{\answer}[1]{\textbf{\underline{#1}}}
    \newcommand{\prompt}[1]{\underline{#1}}
    \newcommand{\tossup}[2]{
    	
    	\par
    	\refstepcounter{tossupnumber}
    		
    	\ifnum\thetossupnumber<21 
    		{\thetossupnumber} 
    	\else {TIEBREAKER}\fi . #1
    
    	ANSWER: #2
    	\newline
    }
    \newcommand{\bonus}[7]{
    	
    	\par
    	\refstepcounter{bonusnumber}
    	
    	\ifnum\thebonusnumber<21 
    		{\thebonusnumber} 
    	\else {TIEBREAKER}\fi . #1
    	
    	[10] #2
    	
    	ANSWER: #3
    	
    	[10] #4
    	
    	ANSWER: #5
    	
    	[10] #6
    	
    	ANSWER: #7
    	\newline
    }
    
    \title{''' + set_name + r'''}
    \author{''' + writers + r'''}
    \date{\vspace{-5ex}}
    
    \begin{document}
    	\maketitle
    	
    	\section*{Tossups}
    	\begin{multicols*}{2}'''
    
    footer = r'''	\end{multicols*}
    \end{document}	
    '''
    
    main = ''
    
    for tossup in tossups:
        if tossup['question'] != '':
            main = main + '\\tossup{'+ tossup['question'] +' }{'+ tossup['answer'] + '}' + '\n'
        
    main = main + '\n \\newpage \\section*{Bonuses} \n'
    
    for bonus in bonuses:
        if bonus['question1'] != '':
            main = main + '\\bonus{' + bonus['lead_in'] + '}{' + bonus['question1'] + '}{' + bonus['answer1'] + '}{' + bonus['question2'] + '}{' + bonus['answer2'] + '}{' + bonus['question3'] + '}{' + bonus['answer3'] + '}'+ '\n'
    
    content = header + main + footer
    
    filename = set_name.replace(' ', '_')
    #os.unlink(filename + '.pdf')
    with open(filename + '.tex','w', encoding='utf-8') as f:
         f.write(content)
    
    commandLine = subprocess.Popen(['pdflatex', filename + '.tex'])
    commandLine.communicate()
    
    os.unlink(filename + '.aux')
    os.unlink(filename + '.log')
    #os.unlink(filename + '.tex')

def format_question(question):
    for key in question.keys():
        if type(question[key]) != str:
            question[key] = "Missing"
        else:    
            if '(*)' in question[key]:
                question[key] = '\power{' + question[key].replace('(*)', '(*)}')
            
            #question[key] = re.sub("_([^_]*)_","\\\\answer{\\1}",re.sub("\_\_([^_]*)\_\_","\\prompt{\\1}",re.sub("\~([^_]*)\~","\\\\textit{\\1}",re.sub("\(([^_]*)\)","\\pronuciationguide{\\1}",str(question[key])))))
            question[key] = question[key].replace('%', '\\%')
            question[key] = re.sub("_([^_]*?)_","\\\\answer{\\1}",re.sub("\_\_([^_]*?)\_\_","\\prompt{\\1}",re.sub("\~([^_]*?)\~","\\\\textit{\\1}",re.sub('\"([^_]*?)\"','``\\1"',str(question[key])))))
    
    return question


tossups, bonuses = extract_data(FILE)

tossup_packets = arrange_packets(tossups)
bonus_packets = arrange_packets(bonuses)

for i in range(len(tossup_packets)):
#for i in range(1):
    tossups, bonuses = randomize_packet(tossup_packets[i], bonus_packets[i], 0)
    tossups = [format_question(t) for t in tossups]
    bonuses = [format_question(b) for b in bonuses]
    run_latex(tossups, bonuses, 'Packet ' + str(i+1), SET_NAME)











