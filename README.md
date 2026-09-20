# 📚 AI Notes Generator

An AI-powered study assistant that converts PDF study material into summaries, flashcards, and quizzes using Google's Gemini API.

## 🚀 Features

* Upload PDF study material
* Extract and clean text from PDFs
* Generate AI-powered summaries
* Generate study flashcards
* Generate quizzes
* Choose quiz difficulty
* Download generated summaries, flashcards, and quizzes
* Save generated notes using SQLite
* View previously saved notes
* Delete saved notes
* Track document statistics such as word count, character count, and estimated pages

## 🛠️ Technologies Used

- Python
- Streamlit
- Google Gemini API
- SQLite
- PyMuPDF
- python-dotenv

## 📁 Project Structure

```text
ai-notes-generator/
│
├── app.py
├── .env
├── .gitignore
├── README.md
├── requirements.txt
│
├── uploads/
├── generated/
│
└── utils/
    ├── pdf_reader.py
    ├── text_cleaner.py
    ├── text_chunker.py
    ├── gemini_client.py
    └── database.py
    └── prompts.py
```

## 📁 Future Enhancements

* Add chunk-based processing for handling larger PDF documents efficiently.
* Add support for scanned/image-based PDFs.
* Move from SQLite to a cloud database for multi-user deployments.
