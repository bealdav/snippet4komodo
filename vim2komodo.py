# -*- coding: utf-8 -*-

""" Convert vim snippets into komdo Edit/IDE snippets
http://www.activestate.com/komodo-edit
"""

"""
snippet browse
	self.browse(cr, uid, ${1:ids}, context=context)${2}
=======================================================
browse(cr, uid, [[%tabstop1:ids]], context=context)[[%tabstop2]]
"""

"""
TDDO : use class
fichiers:
- editor_komodo.py:
    snippet_format
- vim_snip.py

"""


import os
import re

mapping = {'xml.snippets': 'XML',
           'python.snippets': 'Python-common'}

MYFILE = 'xml.snippets'
MYFILE = 'python.snippets'

KOMODO_SNIPPET_FORMAT = """{
  "keyboard_shortcut": "",
  "name": "%s",
  "value": [
%s
    ],
  "set_selection": "true",
  "indent_relative": "true",
  "type": "snippet",
  "treat_as_ejs": "false",
  "auto_abbreviation": "true"
}
"""

MAIN_SNIPPETS = [
    'view', 'field', 'attribute', 'menu',
    'transient', 'widget', 'xpath', 'button'
]

# folder to store komodo snippets
FOLDER = './' + mapping[MYFILE] + '/erp/'
if not os.path.exists(FOLDER):
    os.makedirs(FOLDER)
    os.makedirs(FOLDER + 'sub/')


# file config management to ignore or rename snippets (not mandatory)
txt_message1 = "#puts 1 element by line in this file : %s"
txt_message2 = ("#this line is for example and isn't used by the program "
                "write your content in next line")

MESSAGES = [
    txt_message1 + "snippets that you don't want to convert into komodo.\nsnippet_name\t" + txt_message2,
    txt_message1 + "snippets which you want to change the name into komodo.\nold_snippet_name new_snippet_name\t" + txt_message2,
    "#snippets you want to add into komodo with the same format than normal 'langage.snippets' files\n" + txt_message2,
]


VALS_CONF = {}


def manage_file_config(file_type, msg_type):
    file_name = './' + MYFILE + '.4komodo.' + file_type + '.conf'
    if not os.path.exists(file_name):
        # file creation
        # try:
        f = open(file_name, 'w')
        print "'%s' file has been created in this directory" % file_name
        f.write(MESSAGES[msg_type])
        f.close()
        # except:
            # print ("Impossible to write '%s' file in this folder : check permissions" % (file_config)
    else:
        # extract datas from config files and insert in dict
        rows_config = open(file_name, 'r').readlines()
        if len(rows_config) > 2:
            del(rows_config[0:2])
            if file_type == 'add':
                return rows_config
            vals_line_file_config = []
            for row in rows_config:
                row = row[:-1]
                datas = ''
                if file_type == 'rename':
                    if row.find(' '):
                        datas = {}
                        datas[row[:row.find(' ')]] = row[row.find(' '):].strip()
                elif file_type == 'exclude':
                    datas = row
                vals_line_file_config.append(datas)
            VALS_CONF[file_type] = vals_line_file_config
        else:
            print ("No datas in files conf")

manage_file_config('exclude', 0)
manage_file_config('rename', 1)
custom_snippets = []
custom_snippets = manage_file_config('add', 2)

print 'VALS_CONF', VALS_CONF

# start of the main process
ROWS = open(MYFILE, 'r').readlines()
#if len(custom_snippets) > 0:
    #ROWS.extend(custom_snippets)
COMPOSITE_SNIP = {}

def convert_snippet_tag(line):
    # for match in re.findall('\$\{[a-z0-9(): ]+\}', line):
    for match in re.findall('\$\{[^!]+\}', line):
        line = line.replace(match, match.replace('${','[[%tabstop').replace('}',']]'))
    for match in re.findall('\$[0-9]*', line):
        line = line.replace(match, match.replace('$','[[%tabstop') + ']]')
    return line


def convert_snippet(start, end, sub_snippet_number=None):
    body = ''
    snip_name = ''
    lines = range(start, end+1)

    for line in lines:
        if ROWS[line][:7] == 'snippet':
            snip_name = ROWS[line][7:].strip()
            if VALS_CONF and snip_name in VALS_CONF['exclude']:
                return True
            if VALS_CONF and snip_name in VALS_CONF['rename']:
                #import pdb; pdb.set_trace()
                snip_name = VALS_CONF['rename'].get(snip_name, 'none')
            if VALS_CONF and snip_name.count(' ') > 0:
                if sub_snippet_number is None:
                    meta = {'sub': snip_name[snip_name.find(' '):].strip(), 'start': start, 'end': end}
                    if snip_name[:snip_name.find(' ')] in COMPOSITE_SNIP:
                        COMPOSITE_SNIP[snip_name[:snip_name.find(' ')]].append(meta)
                    else:
                        tmp = []
                        tmp.append(meta)
                        COMPOSITE_SNIP[snip_name[:snip_name.find(' ')]] = tmp
                    return True
                else:
                    snip_name = snip_name[:snip_name.find(' ')].strip() + str(sub_snippet_number)
        else:
            if ROWS[line][0] != '#':
                if ROWS[line][0] == '\t':
                    extracted_line = ROWS[line][1:]
                elif ROWS[line][0:4] == '    ':
                    extracted_line = ROWS[line][4:]
                else:
                    extracted_line = ROWS[line]
                extracted_line = extracted_line.replace('\t', '\\t').replace('"','\\"')
                body += convert_snippet_tag('    "' + extracted_line[:-1] + '",\n')
    if body != '':
        body = body[:-2]
    file_name = snip_name + '.komodotool'
    create_snippet_file(file_name, snip_name, body)
    return True

def create_snippet_file(file_name, snip_name, body):
    try:
        file_name = (file_name.replace('<', '_').replace('>', '_')
                         .replace('/', '-').replace('"', ''))
        folder = FOLDER
        if snip_name[-1].isdigit():
            folder += 'sub/'
        if snip_name in MAIN_SNIPPETS:
            snip_name = '0' + snip_name
            print snip_name
        f = open(folder + file_name, 'w')
        f.write( KOMODO_SNIPPET_FORMAT %(snip_name, body) )
        f.close()
    except:
        print ("Impossible to write '%s' file in '%s' folder : "
               "check permissions" % (file_name, FOLDER))

start = -1

for line, row in enumerate(ROWS):
    if row[:7] == 'snippet':
        end = line - 1
        if start > 0:
            convert_snippet(start, end)
        start = line

convert_snippet(start, line)

# root snippets creation
for snip_name, list_sub in COMPOSITE_SNIP.items():
    core = '\t"' + snip_name + '[[%tabstop:!@#_currentPos!@#_anchor'
    for index, elm in enumerate(list_sub):
        core += '' + str(index) + ' ' + elm['sub'] + '",\n\t"'
        convert_snippet(elm['start'], elm['end'], index)
    core = core[:-5] + ']]"'
    create_snippet_file(snip_name + '.komodotool', snip_name, core)

print 'nb COMPOSITE_SNIP', len(COMPOSITE_SNIP)
