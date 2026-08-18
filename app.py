import hashlib
import os
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import streamlit as st

from utils.database import delete_note, get_notes, save_notes
from utils.gemini_client import generate_flashcards, generate_quiz, generate_summary
from utils.pdf_reader import extract_text_from_pdf
from utils.text_cleaner import clean_text


st.set_page_config(page_title="AI Notes Generator", page_icon="📚", layout="wide")

CONTENT_TYPES = ("summary", "flashcards", "quiz")

# Session state keeps the current draft and job status across reruns.
for key, value in {
    "summary": "",
    "flashcards": "",
    "quiz": "",
    "filename": "",
    "note_title": "",
    "note_title_filename": "",
    "saved_draft_signature": None,
    "save_form_open": False,
}.items():
    st.session_state.setdefault(key, value)

for content_type in CONTENT_TYPES:
    st.session_state.setdefault(f"{content_type}_job", None)
    st.session_state.setdefault(f"{content_type}_error", None)


@st.cache_resource
def get_generation_executor():
    return ThreadPoolExecutor(max_workers=3, thread_name_prefix="notes-generation")


# Run AI requests in the background so navigation does not cancel them.
def start_generation(content_type, generator, *args):
    job = st.session_state[f"{content_type}_job"]
    if job is None or job.done():
        st.session_state[f"{content_type}_error"] = None
        st.session_state[f"{content_type}_job"] = get_generation_executor().submit(
            generator, *args
        )


def collect_completed_generations():
    for content_type in CONTENT_TYPES:
        job = st.session_state[f"{content_type}_job"]
        if job is not None and job.done():
            try:
                st.session_state[content_type] = job.result()
            except Exception as error:
                st.session_state[f"{content_type}_error"] = error
            finally:
                st.session_state[f"{content_type}_job"] = None


def generation_in_progress(content_type):
    job = st.session_state[f"{content_type}_job"]
    return job is not None and not job.done()


def draft_signature(title):
    draft = "\0".join(
        [st.session_state.filename, title.strip()]
        + [st.session_state[content_type] for content_type in CONTENT_TYPES]
    )
    return hashlib.sha256(draft.encode()).hexdigest()


# Shared UI for summary, flashcard, and quiz generation.
def render_generator(
    content_type, title, description, generator, text, height, difficulty_options=None
):
    in_progress = generation_in_progress(content_type)

    st.header(title)
    if difficulty_options:
        difficulty = st.selectbox("Select Quiz Difficulty", difficulty_options)
        st.write(description)
        st.info(f"Current difficulty: **{difficulty}**")
    else:
        difficulty = None
        st.write(description)

    if in_progress:
        status_name = "Flashcard" if content_type == "flashcards" else title[2:]
        st.info(f"{status_name} generation is continuing in the background.")

    if st.button(
        f"✨ Generate {title[2:]}",
        key=f"generate_{content_type}",
        disabled=in_progress,
    ):
        if not text.strip():
            st.error("No readable text found in the PDF.")
        else:
            args = (text, difficulty) if difficulty else (text,)
            start_generation(content_type, generator, *args)
            st.rerun()

    if error := st.session_state[f"{content_type}_error"]:
        error_text = str(error).upper()
        if "503" in error_text or "UNAVAILABLE" in error_text:
            error_message = "The AI service is busy right now. Please try again in a moment."
        elif content_type == "flashcards":
            error_message = "Something went wrong while generating flashcards."
        else:
            error_message = f"Something went wrong while generating the {content_type}."
        st.error(error_message)

    if result := st.session_state[content_type]:
        st.divider()
        st.subheader(f"Generated {title[2:]}")
        if content_type == "summary":
            st.write(result)
        else:
            st.text_area(title[2:], result, height=height)
        st.download_button(
            label=f"⬇️ Download {title[2:]}",
            data=result,
            file_name=f"{content_type}.txt",
            mime="text/plain",
            key=f"download_{content_type}",
        )


def render_saved_notes():
    st.header("💾 Saved Notes")
    st.write("Your previously saved notes are stored in SQLite.")

    if not (saved_notes := get_notes()):
        st.info("You don't have any saved notes yet.")
        return

    for note_id, title, filename, summary, flashcards, quiz, created_at in saved_notes:
        with st.expander(f"📄 {title} — {filename}"):
            st.write("**Filename:**", filename)
            st.caption(f"Saved: {created_at}")
            st.divider()

            if summary:
                st.subheader("📝 Summary")
                st.write(summary)
            if flashcards:
                st.subheader("🗂️ Flashcards")
                st.text_area(
                    "Saved Flashcards",
                    flashcards,
                    height=250,
                    key=f"saved_flashcards_{note_id}",
                )
            if quiz:
                st.subheader("🧠 Quiz")
                st.text_area("Saved Quiz", quiz, height=300, key=f"saved_quiz_{note_id}")

            st.divider()
            if st.button("🗑️ Delete This Note", key=f"delete_{note_id}"):
                delete_note(note_id)
                st.success("Note deleted successfully!")
                st.rerun()


# Collect any background results before rendering the page.
collect_completed_generations()

st.sidebar.title("📚 AI Notes Generator")
st.sidebar.write("Upload your study material and let AI help you learn.")
st.sidebar.divider()

if st.sidebar.button("🔄 Reset Application"):
    st.session_state.clear()
    st.rerun()

st.title("📚 AI Notes Generator")
st.write("Upload a PDF and use AI to create summaries, flashcards, and quizzes.")

uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])

if uploaded_file is not None:
    # Reset the suggested save title when a different file is uploaded.
    st.session_state.filename = uploaded_file.name
    if st.session_state.note_title_filename != uploaded_file.name:
        st.session_state.note_title = Path(uploaded_file.name).stem
        st.session_state.note_title_filename = uploaded_file.name
        st.session_state.saved_draft_signature = None
        st.session_state.save_form_open = False

    st.success("PDF uploaded successfully!")
    os.makedirs("uploads", exist_ok=True)
    with open(os.path.join("uploads", uploaded_file.name), "wb") as file:
        file.write(uploaded_file.getbuffer())

    st.subheader("📄 File Information")
    name_column, size_column = st.columns(2)
    name_column.markdown(f"**Name:** {uploaded_file.name}")
    size = uploaded_file.size
    size_text = f"{size / 1024:.2f} KB" if size < 1024 * 1024 else f"{size / (1024 * 1024):.2f} MB"
    size_column.markdown(f"**Size:** {size_text}")

    text = clean_text(extract_text_from_pdf(uploaded_file))
    st.sidebar.metric("Words", len(text.split()))
    st.sidebar.metric("Characters", len(text))
    st.sidebar.metric("Estimated Pages", len(text) // 3000 + 1)

    with st.expander("📖 View Extracted Text"):
        if text.strip():
            st.text_area("Extracted Text Preview", text[:5000], height=250)
        else:
            st.warning("No readable text was found in this PDF.")

    st.divider()
    st.subheader("What would you like to generate?")
    section = st.radio(
        "Choose an option",
        ["Summary", "Flashcards", "Quiz", "Saved Notes"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if section == "Summary":
        render_generator(
            "summary",
            "📝 Summary",
            "Generate a concise summary of your uploaded PDF.",
            generate_summary,
            text,
            0,
        )
    elif section == "Flashcards":
        render_generator(
            "flashcards",
            "🗂️ Flashcards",
            "Generate study flashcards from your uploaded PDF.",
            generate_flashcards,
            text,
            450,
        )
    elif section == "Quiz":
        render_generator(
            "quiz",
            "🧠 Quiz",
            "Generate a quiz based on your PDF.",
            generate_quiz,
            text,
            500,
            ["Easy", "Medium", "Hard"],
        )
    else:
        render_saved_notes()

# Save the current draft only after the user confirms it.
if uploaded_file is not None and any(st.session_state[content] for content in CONTENT_TYPES):
    st.divider()
    st.subheader("💾 Save Your Generated Notes")
    active_generation = any(generation_in_progress(content) for content in CONTENT_TYPES)

    if active_generation:
        st.info("Wait for all active generations to finish before saving this note.")

    if st.button("💾 Save Notes", disabled=active_generation, key="open_save_notes"):
        st.session_state.save_form_open = True

    if st.session_state.save_form_open:
        with st.form("save_notes_form"):
            title = st.text_input("Note title", key="note_title", max_chars=120)
            save_clicked = st.form_submit_button("Confirm save")

        if save_clicked:
            signature = draft_signature(title)
            if not title.strip():
                st.error("Add a note title before saving.")
            elif signature == st.session_state.saved_draft_signature:
                st.info("This version is already saved. Edit or generate more content to save a new version.")
            else:
                save_notes(
                    title.strip(),
                    st.session_state.filename,
                    st.session_state.summary,
                    st.session_state.flashcards,
                    st.session_state.quiz,
                )
                st.session_state.saved_draft_signature = signature
                st.session_state.save_form_open = False
                st.success("Notes saved successfully!")
