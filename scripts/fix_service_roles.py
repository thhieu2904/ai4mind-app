"""
Quick fix script for role comparisons
"""
import re

file_path = 'app/services/counselor_chat_service.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Count occurrences first
count_student = len(re.findall(r'user_role == "student"', content))
count_counselor = len(re.findall(r'user_role == "counselor"', content))

print(f'Found {count_student} student comparisons')
print(f'Found {count_counselor} counselor comparisons')

# Replace
content = content.replace('user_role == "student"', 
                         'user_role == UserRole.STUDENT.value or user_role == UserRole.STUDENT')
content = content.replace('user_role == "counselor"', 
                         'user_role == UserRole.COUNSELOR.value or user_role == UserRole.COUNSELOR')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print('✅ Fixed all role comparisons')
