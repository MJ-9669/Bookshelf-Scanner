# 📚 AI Bookshelf Scanner & Recommender

An intelligent, multi-agent web application that analyzes photos of any bookshelf and provides personalized book recommendations based on your reading preferences. Built with Python, Streamlit, and Google's Agent Development Kit (ADK).

[Shelf_Scanner](https://bookshelf-scanner.streamlit.app/)

## ✨ Features
* **Image Recognition:** Snap a picture or upload an image of any bookshelf (at a store, library, or friend's house).
* **Multi-Agent AI Pipeline:** Utilizes a sequential chain of specialized AI agents to process data step-by-step.
* **Personalized Matches:** Cross-references the identified books with your selected favorite genres to pitch the top 3 best recommendations.
* **Local Database:** Automatically formats and saves scanned books and their assigned genres to a local SQLite database for future reference.

## 🛠️ Tech Stack
* **Frontend:** Streamlit
* **AI Framework:** Google Agent Development Kit (ADK)
* **Models:** Gemini 3 Flash & Gemini 3 Flash Preview (Vision)
* **Database:** SQLite3
* **Image Processing:** Pillow (PIL)

## 🧠 How It Works (Under the Hood)
This application runs on a `SequentialAgent` pipeline consisting of three distinct AI roles:
1. **The Vision Specialist:** Ingests the raw image, reads the spines of the books, and extracts a raw list of titles and authors.
2. **The Librarian:** Takes the messy text list, corrects spelling, assigns accurate genres, formats the data into strict JSON, and triggers a tool to save the shelf to a local `.db` file.
3. **The Matchmaker:** Compares the structured JSON list against the user's selected preferences to generate engaging, custom pitches for the top 3 books they should read next.

## 🏗️ System Architecture

The application is built on a sequential multi-agent architecture using Google's Agent Development Kit (ADK). The data flows through a strict pipeline where each agent handles a highly specialized task.

### **The Data Flow:**
1. **Frontend (Streamlit):** Captures the user's reading preferences and bookshelf image, converting the image into a byte stream.
2. **Orchestrator (ADK Runner & Session Service):** Creates a temporary in-memory session to hold shared context and executes the `SequentialAgent` pipeline.
3. **Agent 1: Vision Specialist (`gemini-3-flash-preview`)**
   * **Input:** Bookshelf Image Bytes + User Preferences.
   * **Task:** Performs visual extraction to read book spines.
   * **Output:** A raw text list of titles and authors (saved to pipeline memory as `raw_books`).
4. **Agent 2: The Librarian (`gemini-3-flash`)**
   * **Input:** `raw_books` state + User Preferences.
   * **Task:** Cleans the text, assigns literary genres, formats the data into strict JSON, and executes a custom Python tool (`save_to_database`).
   * **Tool Execution:** Writes the structured JSON data into a local SQLite database (`shelf.db`).
   * **Output:** The finalized JSON list (saved to pipeline memory as `formatted_books`).
5. **Agent 3: The Matchmaker (`gemini-3-flash`)**
   * **Input:** `formatted_books` JSON + User Preferences.
   * **Task:** Cross-references the available inventory with the user's specific tastes.
   * **Output:** Generates the final, formatted recommendation pitch which the Orchestrator returns to the Streamlit UI.
