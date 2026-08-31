"""Import forensics - identify collection errors"""
import subprocess
result = subprocess.run(
    ['python', '-m', 'pytest', '--collect-only', '-v'],
    capture_output=True, text=True, cwd=r'C:\Users\Jonatthan\Documents\Github\CodeAgent'
)
print('=== STDOUT ===')
for line in result.stdout.split('\n')[:50]:
    print(line)
print('=== STDERR ===')
for line in result.stderr.split('\n')[:50]:
    print(line)
print('=== RETURN CODE ===')
print(result.returncode)