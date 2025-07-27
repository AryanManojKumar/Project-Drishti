# Find and remove content after main function
with open('streamlit_crowd_ui_fixed.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the main function end
main_end = content.find('if __name__ == "__main__":\n    main()')
if main_end != -1:
    # Keep content up to and including the main call
    clean_content = content[:main_end + len('if __name__ == "__main__":\n    main()')]
    
    # Write clean content back
    with open('streamlit_crowd_ui_fixed.py', 'w', encoding='utf-8') as f:
        f.write(clean_content)
    
    print("✅ File cleaned successfully!")
else:
    print("❌ Could not find main function end")