import pandas as pd
import streamlit as st
from scanner_agents.agent import shelf_scanner_pipeline
from PIL import Image

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

import io
import asyncio

import os
from dotenv import load_dotenv

# Tell Python exactly where the .env file lives
load_dotenv("scanner_agents/.env")

st.title("AI Bookshelf Scanner and Book Recommender")
st.markdown("Find the perfect book from you.")
st.write("")

st.markdown("Taking a photo of an entire bookshelf at stores, the library, or a friend's house, and we'll help you figure out which ones you'll like!")

st.write("")

# if st.button("Start Scanning", type = "primary"):
	

st.write("")

st.subheader("How It Works")
c1,c2,c3 = st.columns(3)
with c1:
	st.markdown("#### 1. Set Preferences")
	st.caption("Tell us about your reading interests and favorite author")
with c2:
	st.markdown("#### 2. Upload Photo")
	st.caption("Take a photo of bookshelf and our AI will Identify each book")
with c3:
	st.markdown("#### 3. Find Matches")
	st.caption("We highlight books that match your taste")


st.markdown("#### Tell us about your reading preferences")

st.write("Select genres and authors that interest you to help us provide better recommendations.")

all_genres = ["Fiction", "Non-Fiction", "Sci-Fi", "Fantasy", "Mystery", "Thriller", "Romance", "Biography", "History", "Self-	Help", "Business", "Comics", "Classics", "Young Adult", "Horror","Role-playing Game"]

user_pref = st.multiselect("Choose genre:", all_genres)

st.write("")

st.write("Upload a photo of books.")

input_options = st.radio("Choose input method:",["Browse files", "Camera" ])

if input_options == "Camera":
	uploaded_file = st.camera_input("Take picture of your bookshlef")
else:
	uploaded_file = st.file_uploader("Upload an image", type = ["jpeg", "jpg", "png"])

if uploaded_file:
	st.image(uploaded_file)

if st.button("Start Scanning"):
	if uploaded_file is not None:
		with st.spinner("Analyzing and Cross-Referencing the Preferences..."):
			img = Image.open(uploaded_file)

			buf = io.BytesIO()
			img.convert('RGB').save(buf, format="JPEG")
			image_bytes = buf.getvalue()

			session_service = InMemorySessionService()

			asyncio.run(session_service.create_session(
				app_name="Shelf_Scanner_app", 
				user_id="demo_user", 
				session_id="session_001"
				))


			runner = Runner(
				agent=shelf_scanner_pipeline,
				app_name="Shelf_Scanner_app",
				session_service=session_service
			)



			user_prompt = f"Here is my bookshelf. My reading preferences are: {', '.join(user_pref)}"
			message = types.Content(
				role="user",
				parts=[
					types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg"),
					types.Part.from_text(text=user_prompt)
				]
			)

			try:
				events = runner.run(
					user_id = "demo_user",
					session_id = "session_001",
					new_message=message
				)

				final_result = ""
				for event in events:
					# Check if it's the final response
					if event.is_final_response():
						# Safely ensure the text actually exists before grabbing it
						if event.content and event.content.parts:
							final_result = event.content.parts[0].text

				st.success("Analysis Complete!")
				
				if final_result == "":
					st.warning("The AI ran, but returned empty text! We need to link the pipeline memory.")
				else:
					st.markdown(final_result)

			except Exception as e:
				st.error(f"Pipeline crashed internally: {e}")

	else:
		st.warning("Please upload or take a photo of a bookshelf first!")