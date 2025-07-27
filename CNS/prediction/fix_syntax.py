# Fix syntax error in streamlit file
with open('streamlit_crowd_ui_fixed.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the syntax error by removing the problematic layout code
content = content.replace('st.info("💡 **Troubleshooting:** Check internet connection and coordinate values")layout(', 'st.info("💡 **Troubleshooting:** Check internet connection and coordinate values")')

# Remove any duplicate layout code that got mixed up
lines = content.split('\n')
cleaned_lines = []
skip_until_next_method = False

for i, line in enumerate(lines):
    if 'st.info("💡 **Troubleshooting:** Check internet connection and coordinate values")' in line and 'layout(' in line:
        # Fix this line
        cleaned_lines.append('            st.info("💡 **Troubleshooting:** Check internet connection and coordinate values")')
        skip_until_next_method = True
    elif skip_until_next_method:
        # Skip lines until we find a new method or class definition
        if line.strip().startswith('def ') or line.strip().startswith('class ') or 'def main():' in line:
            skip_until_next_method = False
            cleaned_lines.append(line)
    else:
        cleaned_lines.append(line)

# Write cleaned content back
with open('streamlit_crowd_ui_fixed.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(cleaned_lines))

print("✅ Syntax error fixed!")