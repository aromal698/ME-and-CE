# Pathway Engineering Study Hub

A starter app for Mechanical and Civil Engineering students. It provides an editable eight-semester, six-subject structure; local class notes; PDF upload, preview, and downloadable notes PDFs; user-authored micro bits; self-test practice; and a syllabus-grounded study-material maker using Ollama local AI.

## Windows quick start

1. Install Python 3.10 or newer. During installation, select **Add Python to PATH**.
2. Extract the downloaded ZIP file.
3. Open the `engineering-roadmap-app` folder.
4. Double-click `Run_Pathway.bat`. The first launch installs the required packages; allow it to finish. A browser tab should open automatically. Keep the black terminal window open while you use the app.

If Windows asks which app to use for `.bat`, right-click the file and choose **Open**. Do not open `app.py` directly or open it in the browser.

## Manual start

Open Command Prompt or PowerShell in this folder and run:

```bash
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

If `py` is unavailable, replace it with `python`.

## Free AI study-material maker

The **AI Study Maker** page can draft study notes, exam micro bits, and practice questions from a supplied KTU syllabus extract. This version is set to the KTU B.Tech 2024 scheme. Select the semester and subject, then paste the official 2024 subject syllabus or upload a text-based PDF. Confirm the course syllabus with your college, especially if your curriculum includes course choices. The app extracts PDF text with `pypdf`.

For AI generation, install [Ollama for Windows](https://ollama.com/download/windows), open Command Prompt, and run:

```bash
ollama pull llama3.2
```

Keep Ollama running while using the app. This uses a locally downloaded model and has no per-prompt API charge; model download uses internet and disk space, and generation speed depends on the computer. The app does not send syllabus text to a cloud AI service. Scanned image-only PDFs need OCR or pasted text.

This app targets the KTU B.Tech 2024 scheme. Use the [official KTU B.Tech curriculum index](https://ktu.edu.in/academics/branchcurriculum/hardcoded-btech) to locate your branch and course syllabus, and confirm course choices with your college. AI material is a draft: check equations and explanations with official course documents and faculty notes.

## Customize it

Choose CE or ME and a semester in the left sidebar. Open **Setup & Profile** and replace the six placeholder subject names with your university syllabus. Repeat for each semester. Add your own notes, PDFs, and revision prompts.

The app saves `student_data.json` and PDF files in this folder (PDF files go in `uploads/`). Back up this folder to retain student content. This starter version saves locally and does not connect to a cloud database or cloud AI service. Subject names are editable because curricula differ by university.


