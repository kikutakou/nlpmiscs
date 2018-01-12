#!/usr/bin/env
import argparse
import os
import tempfile
import subprocess as sp
import re
import shutil


# get mecab tool and dict
indexer = sp.check_output("mecab-config --libexecdir", shell=True).decode("utf8").rstrip() + "/mecab-dict-index"
dicdir = sp.check_output("mecab-config --dicdir", shell=True).decode("utf8").rstrip() + "/ipadic"


def existingFile(filename):
    if not os.path.exists(filename):
        raise argparse.ArgumentTypeError("input file {} not exist".format(filename))
    return filename

# argparse
parser = argparse.ArgumentParser()
parser.add_argument("inputs", type=existingFile, nargs="+", help="list of user words")
parser.add_argument("-o", "--output", default="user.dic", help="output destination")
parser.add_argument("-d", "--dicdir", type=existingFile, help="mecab dictionary")
parser.add_argument("--csvout", help="csv file output to preserve")
group = parser.add_mutually_exclusive_group()
group.add_argument("-c", "--cost", default="10", help="cost")
group.add_argument("-m", "--model", help="model file to for cost estimation")
args = parser.parse_args()

if os.path.splitext(args.output)[1] != ".dic":
    args.output += ".dic"
if args.dicdir:
    dicdir = args.dicdir


# print
print("indexer: " + indexer)
print("dictionary: " + dicdir)
print("output to: " + args.output)

command_base = "{} -f utf-8 -t utf-8 -d {}".format(indexer, dicdir)

# create temp file then ouptut header
temp = open(args.csvout, "w") if args.csvout else tempfile.NamedTemporaryFile("w", delete=False)


# output contents
print("\n---converting word list to csv ...")
delimiter = re.compile(",|=>")
for file in args.inputs:
    for i,line in enumerate(open(file)):
        for word in [w.strip() for w in delimiter.split(line.rstrip())]:
            print("{}:{} {}".format(file, i, word))
            cost = "" if args.model else args.cost
            # ["表層形", "左文脈ID", "右文脈ID", "コスト", "品詞", "品詞細分類1", "品詞細分類2", "品詞細分類3", "活用形", "活用型", "原形", "読み", "発音"]
            data = [word, "", "", cost, "名詞", "固有名詞", "一般", "*", "*", "*", word, "", ""]
            temp.write(",".join(data) + "\n")
temp.close()


# cost estimation
if args.model:
    print("\n---estimating cost ...")
    temptemp = os.path.splitext(temp.name)[0] + "_tmp.csv"
    shutil.copyfile(temp.name, temptemp)
    command = command_base + " -u {} -a -m {} {}".format(temp.name, args.model, temptemp)
    print("+ " + command)
    print(sp.check_output(command, shell=True).decode("utf8"))


# convert
print("\n---generating dic ...")
command = command_base + " -u {} {}".format(args.output, temp.name)
print("+ " + command)
print(sp.check_output(command, shell=True).decode("utf8"))

