import sys
import os

match = None

while True:
    search = input("> ")
    if ("Y" in search):
        if match:
            os.system("cp {} working.md".format(match))
        continue

    match = os.popen("grep -l -i \"{}\" ./archive/* | head -n 1".format(search)).read().rstrip()
    print("match: {}".format(match))
    if "archive" in match:
        os.system("cat {} | head -n -3".format(match))

