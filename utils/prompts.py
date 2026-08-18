SUMMARY_PROMPT = """
You are an expert study assistant.

Your task is to summarize the following study material.

Instructions:

1. Keep only the important information.
2. Use bullet points.
3. Keep formulas unchanged.
4. Explain difficult concepts simply.
5. Maximum 200 words.
6. Do not invent information.

Study Material:

{text}
"""

FLASHCARD_PROMPT = """
You are an expert teacher.

Read the study material below and create flashcards.

Rules:
1. Create 10 flashcards.
2. Each flashcard should have one Question and one Answer.
3. Keep answers short and clear.
4. Do not invent information.
5. Format exactly like this:

Question: ...
Answer: ...

Study Material:

{text}
"""

QUIZ_PROMPT = """
You are an expert teacher.

Difficulty:
{difficulty}

Read the study material and generate a quiz.

Rules:

1. Create 10 Multiple Choice Questions.
2. Each question should have 4 options.
3. Mention the correct answer.
4. Questions should cover different topics.
5. Do not invent information.

Format exactly like this:

Question 1:
...

A.
B.
C.
D.

Answer:

Study Material:

{text}
"""