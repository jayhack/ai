import re

f = open('pyproject.toml')
lines = f.readlines()
version_line = [l for l in lines if l.startswith('version')][0]
version = version_line.split('"')[1]
print(f'Using version {version}')

path = './src/ai/__init__.py'
read_file = open(path)
contents = read_file.read()
result = re.sub("__version__ = '.*'", f"__version__ = '{version}'", contents)
read_file.close()
write_file = open(path, 'w')
write_file.write(result)
write_file.close()

