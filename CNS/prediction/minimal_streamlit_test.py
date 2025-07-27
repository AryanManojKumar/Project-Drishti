import streamlit as st

class CrowdPredictionUI:
    def __init__(self):
        pass

    def run(self):
        st.title("Minimal Streamlit Test")
        self.prediction_section()

    def prediction_section(self):
        st.header("Prediction Section")
        try:
            st.write("This is inside the try block.")
            # Simulate prediction logic here
            for i in range(3):
                st.write(f"Prediction {i+1}")
        except Exception as e:
            st.error(f"Error: {e}")

def main():
    ui = CrowdPredictionUI()
    ui.run()

if __name__ == "__main__":
    main()