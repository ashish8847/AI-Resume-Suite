import streamlit as st
import PyPDF2
import requests
import os
from dotenv import load_dotenv
from fpdf import FPDF  # For generating PDF resumes

# Load environment variables
load_dotenv()

# Page setup
st.set_page_config(page_title="AI Resume Suite", layout="wide")
st.title("🧠 AI Resume Suite")
st.write("Choose between analyzing your existing resume or building a new one.")

# Sidebar Navigation
option = st.sidebar.radio("Select Feature", ["Resume Analyzer", "Resume Builder"])

# =========================================================
# 🧠 1. RESUME ANALYZER SECTION
# =========================================================
if option == "Resume Analyzer":
    st.header("📄 AI Resume Analyzer")

    st.write("Upload your resume (PDF) and optionally include a job description for tailored feedback.")

    st.sidebar.header("❓ Need Help?")
    st.sidebar.markdown("""
    - Upload a **detailed resume** for better suggestions.  
    - Paste a **job description** for accurate matching.  
    - Choose a **feedback tone**.  
    - The AI will give structured improvement suggestions.
    """)

    uploaded_file = st.file_uploader("📤 Upload your resume (PDF only)", type="pdf")

    # Function to extract text from the PDF
    def extract_text_from_pdf(file):
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted
        return text

    resume_text = ""
    if uploaded_file:
        with st.spinner("Extracting text from your resume..."):
            resume_text = extract_text_from_pdf(uploaded_file)
            if resume_text.strip() == "":
                st.warning("The resume is empty or unreadable. Please upload a different file.")
            else:
                st.subheader("📄 Extracted Resume Text")
                st.text_area("Resume Content", resume_text, height=300)

    st.subheader("📝 Job Description (Optional)")
    job_description = st.text_area("Paste job description here", height=200)

    st.subheader("🎯 Feedback Tone")
    tone = st.selectbox("Choose tone for feedback", ["Strict HR", "Friendly Mentor"])

    if st.button("Generate AI Feedback"):
        if resume_text.strip() == "":
            st.warning("Please upload a valid resume before proceeding.")
        else:
            with st.spinner("Generating feedback using LLaMA 3..."):
                GROQ_API_KEY = os.getenv("GROQ_API_KEY")
                if not GROQ_API_KEY:
                    st.error("Missing GROQ_API_KEY in .env file.")
                else:
                    user_message = f"Here is a resume:\n{resume_text}\n"
                    if job_description.strip():
                        user_message += f"\nThis is the job description:\n{job_description}\n"
                    user_message += f"""
                    Please provide:
                    1. Suggestions for improvement in a {tone.lower()} tone.
                    2. Comparison against job description.
                    3. Matched/missing keywords.
                    4. A score (out of 10).
                    5. Final recommendations.
                    """

                    headers = {
                        "Authorization": f"Bearer {GROQ_API_KEY}",
                        "Content-Type": "application/json"
                    }

                    payload = {
                        "messages": [
                            {"role": "system", "content": f"You are an expert resume reviewer giving {tone.lower()} feedback."},
                            {"role": "user", "content": user_message}
                        ],
                        "model": "llama-3.1-8b-instant"
                    }

                    response = requests.post("https://api.groq.com/openai/v1/chat/completions",
                                             headers=headers, json=payload)

                    if response.status_code == 200:
                        result = response.json()
                        ai_feedback = result["choices"][0]["message"]["content"]
                        st.subheader("💡 AI Feedback")
                        st.markdown(ai_feedback)
                        st.download_button("📥 Download Feedback", ai_feedback, file_name="ai_feedback.txt")
                    else:
                        st.error("❌ Failed to get feedback. Try again later.")


# =========================================================
# 🏗️ 2. RESUME BUILDER SECTION
# =========================================================
elif option == "Resume Builder":
    st.header("🏗️ AI Resume Builder")

    st.write("Fill out the details below and generate a professional-looking resume PDF instantly.")

    # Basic Info
    name = st.text_input("Full Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone Number")
    linkedin = st.text_input("LinkedIn URL")
    summary = st.text_area("Professional Summary", height=100)

    # Education
    st.subheader("🎓 Education")
    edu_degree = st.text_input("Degree")
    edu_institution = st.text_input("Institution")
    edu_year = st.text_input("Graduation Year")

    # Skills
    st.subheader("🧰 Skills")
    skills = st.text_area("List your skills (comma-separated, e.g., Python, Data Analysis, Communication)")

    # Experience
    st.subheader("💼 Work Experience")
    job_title = st.text_input("Job Title")
    company = st.text_input("Company Name")
    duration = st.text_input("Duration (e.g., Jan 2022 – Present)")
    job_description = st.text_area("Job Responsibilities / Achievements", height=150)

    # Generate Resume Button
    if st.button("🧾 Generate Resume PDF"):
        if not name or not email or not summary:
            st.warning("Please fill out at least your name, email, and summary.")
        else:
            # Create a PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 18)
            pdf.cell(0, 10, name, ln=True, align="C")
            pdf.set_font("Arial", "", 12)
            pdf.cell(0, 8, f"Email: {email}", ln=True, align="C")
            pdf.cell(0, 8, f"Phone: {phone}", ln=True, align="C")
            pdf.cell(0, 8, f"LinkedIn: {linkedin}", ln=True, align="C")
            pdf.ln(10)

            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Professional Summary", ln=True)
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 8, summary)
            pdf.ln(5)

            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Education", ln=True)
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 8, f"{edu_degree}, {edu_institution} ({edu_year})")
            pdf.ln(5)

            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Skills", ln=True)
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 8, skills)
            pdf.ln(5)

            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Experience", ln=True)
            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 8, f"{job_title} at {company} ({duration})")
            pdf.multi_cell(0, 8, job_description)
            pdf.ln(5)

            pdf_output = f"{name.replace(' ', '_')}_Resume.pdf"
            pdf.output(pdf_output)
            with open(pdf_output, "rb") as file:
                st.download_button(
                    label="📥 Download Resume PDF",
                    data=file,
                    file_name=pdf_output,
                    mime="application/pdf"
                )
            st.success("✅ Resume generated successfully!")
