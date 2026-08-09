import os

path="./"
wordlist=list()
for filename in os.listdir(path):
    my_file = open(f"{path}{filename}", "r")
    lines=my_file.readlines()
    for line in lines:
        wordlist.append(line.replace("\n",""))
    my_file.close()

print(wordlist)

with open(r'/Users/daniel/Desktop/FYP_tools/Wordlists/filter_wordlists.txt', 'w') as fp:
    for item in wordlist:
        if item.find(".") != -1:
        # write each item on a new line
            fp.write("%s\n" % item)
    print('Done')

    print(filename)