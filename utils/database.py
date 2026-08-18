import sqlite3


connection = sqlite3.connect("notes.db", check_same_thread=False)
cursor = connection.cursor()

cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT,
        summary TEXT,
        flashcards TEXT,
        quiz TEXT,
        title TEXT,
        created_at TEXT
    )
    """
)

columns = {column[1] for column in cursor.execute("PRAGMA table_info(notes)")}
if "title" not in columns:
    cursor.execute("ALTER TABLE notes ADD COLUMN title TEXT")
if "created_at" not in columns:
    cursor.execute("ALTER TABLE notes ADD COLUMN created_at TEXT")

cursor.execute("UPDATE notes SET title = filename WHERE title IS NULL OR title = ''")
cursor.execute(
    "UPDATE notes SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL OR created_at = ''"
)
connection.commit()


def save_notes(title, filename, summary, flashcards, quiz):
    cursor.execute(
        """
        INSERT INTO notes (filename, summary, flashcards, quiz, title, created_at)
        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """,
        (filename, summary, flashcards, quiz, title),
    )
    connection.commit()


def get_notes():
    return cursor.execute(
        """
        SELECT id, title, filename, summary, flashcards, quiz, created_at
        FROM notes
        ORDER BY datetime(created_at) DESC, id DESC
        """
    ).fetchall()


def delete_note(note_id):
    cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
    connection.commit()
