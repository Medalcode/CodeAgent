"""Encoding forensics for desktop_app.py"""
import os

# Direct absolute path - proven to be the correct location
filepath = r'C:\Users\Jonatthan\Documents\Github\CodeAgent\tests\desktop_app.py'
absolute_path = os.path.abspath(filepath)
print('Filepath:', filepath)
print('Absolute path:', absolute_path)
print('File exists:', os.path.exists(filepath))

with open(filepath, 'rb') as f:
    content = f.read()

print('File size:', len(content))
print('First 20 bytes (hex):', content[:20].hex())
print('Last 20 bytes (hex):', content[-20:].hex())

if content[:3] == b'\xef\xbb\xbf':
    print('UTF-8 BOM present')
elif content[:2] == b'\xff\xfe':
    print('UTF-16 LE BOM present')
elif content[:2] == b'\xfe\xff':
    print('UTF-16 BE BOM present')
else:
    print('No BOM detected')

lines = content.split(b'\n')
print('Total lines:', len(lines))

if len(lines) > 110:
    line111 = lines[110]
    print('Line 111 bytes:', line111[:100])
    print('Line 111 hex:', line111[:100].hex())

    fffd = b'\xef\xbf\xbd'
    if fffd in line111:
        print('U+FFFD replacement character FOUND in line 111')
        pos = line111.index(fffd)
        print('Position of U+FFFD in line 111:', pos)
        start = max(0, pos - 10)
        end = min(len(line111), pos + 10)
        print('Surrounding bytes:', line111[start:end].hex())
    else:
        print('U+FFFD NOT found in line 111')
else:
    print('Line 110 does not exist - file has', len(lines), 'lines')

print()
print('File ends with:', content[-10:].hex())