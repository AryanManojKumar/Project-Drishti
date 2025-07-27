#!/usr/bin/env python3
# Clean the streamlit file

with open('streamlit_crowd_ui_fixed.py', 'r', encoding='utf-8', errors='ignore') as f:
    content = f.read()

# Find the first occurrence of main function
main_marker = 'if __name__ == "__main__":'
main_pos = content.find(main_marker)

if main_pos != -1:
    # Find the end of main() call
    lines_after_main = content[main_pos:].split('\n')
    
    # Keep only the main block (usually 3 lines)
    clean_ending = []
    for i, line in enumerate(lines_after_main):
        clean_ending.append(line)
        if 'main()' in line:
            break
        if i > 5:  # Safety limit
            break
    
    clean_content = content[:main_pos] + '\n'.join(clean_ending)
    
    with open('streamlit_crowd_ui_fixed.py', 'w', encoding='utf-8') as f:
        f.write(clean_content)
    
    print('✅ File cleaned successfully')
else:
    print('❌ Could not find main function')