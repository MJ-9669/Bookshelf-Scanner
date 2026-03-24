import sqlite3
from google.adk.agents.llm_agent import Agent
from google.adk.agents import SequentialAgent


def save_to_database(books_list:list[dict[str,str]])-> str:
	'''
	Saves a list of books into the SQLite database.
	takes a list of dictionaries with 'Title', 'Author', and 'Genre'
	'''
	try:
		with sqlite3.connect("shelf.db") as connection:
			cursor = connection.cursor()


			cursor.execute('''CREATE TABLE IF NOT EXISTS books(
				Title TEXT, Author TEXT, Genre TEXT)''')


			for book in books_list:
				cursor.execute('''INSERT INTO books (Title, Author, Genre) VALUES (?, ?, ?)''',
						(book.get('Title', 'Unknown'),
						book.get('Author','Unknown'),
						book.get('Genre', 'Unknown')))	
			connection.commit()

			return f"Success: {len(books_list)} books saved to the database."
	except Exception as e:
		print(f"An error occured: {e}")



vision_specialist = Agent(
	name = "Vision_Specialist",
	model = "gemini-3-flash-preview",
	instruction = '''
		You are a vision specialist. You will receive an image of a bookshelf and the user's reading preferences.
		1. Extract the readable names of the books and authors.
		2. Return a clean text list of the titles and authors.
		3. CRITICAL: At the very bottom of your response, you MUST repeat the user's reading preferences exactly as they were provided so the next agent in the chain can see them.
		''' ,
		output_key="raw_books"	)

the_librarian = Agent(
	name = "The_Librarian",
	model = "gemini-3-flash-preview",
	instruction = '''
		You are a skilled librarian. You will receive a list of books and the user's reading preferences here: {raw_books}.
		1. Assign a genre to each book from ("Fiction", "Non-Fiction", "Sci-Fi", "Fantasy", "Mystery", "Thriller", "Romance", "Biography", "History", "Self-Help", "Business", "Comics", "Classics", "Young Adult", "Horror","Role-playing Game"]) this list and format the list as strict JSON.
		2. Use the 'save_to_database' tool to save this shelf.
		3. CRITICAL: After the tool runs, you MUST output the JSON list of books AND repeat the user's reading preferences at the bottom of your text so the matchmaker can see them. 
	''',
	tools = [save_to_database],
	output_key="formatted_books"
		)


the_matchmaker = Agent(
	name = "The_Matchmaker",
	model = "gemini-3-flash-preview",
	instruction = '''
		You are a matchmaker. You will receive a JSON list of books and the user's reading preferences (favorite genres and 			authors) right here: {formatted_books}.
		Your ONLY job is to compare the books to the preferences.
		CRITICAL RULES:
		1. If a book is by one of their favorite authors, or heavily matches the style of their favorite authors, prioritize 				picking it!
	 	2. pick the top 3 best matches.
		3. Write a short, engaging pitch for why the user should read each one, specifically referencing how it ties into their 		stated genres or favorite authors.
		DO NOT just output the full list of books. Output only your 3 recommendations.
	''')	

shelf_scanner_pipeline = SequentialAgent(
	name = "Shelf_Scanner_Pipeline",
	sub_agents = [vision_specialist, the_librarian, the_matchmaker]	
)

