import os

path = './'
dirs = os.listdir(path)
dirs.sort()

for dir in dirs:
    if not os.path.isdir(os.path.join(path, dir)) or dir.startswith('img') or dir.startswith('.'):
        continue
    files = os.listdir(os.path.join(path, dir))
    files.sort()
    with open(os.path.join(path, dir, 'README.md'), 'w') as f:
        f.write("# " + dir + "\n\n")
        for file in files:
            if file.startswith('README'):
                continue
            f.write("- [" + file.replace('.md', '') + "](./" + file.replace(' ', '%20') + ")" + "\n")

