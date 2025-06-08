## Inspiration

The main inspiration for this project actually came out of necessity. Last week, during finals, our team members had tests almost daily. We are all busy high schoolers, with time being dedicated to extracurriculars, school work, and chores, we were often spread very thin. A major area of concern for us was preparing for tests or presentations, trying to optimize our time, we realized that every day hours were wasted on driving, doing chores, and walking between classes. All of this time could have been used to actually do something productive. That is when we decided to build SoundWave, a tool perfect for helping busy people prepare for anything.

## What it does

SoundWave takes your documents and notes and generates a full podcast. But truthfully, this isn't very helpful; simply having a podcast isn't enough to actually process information. This is why we decided to make it an interactive podcast. By clicking the ask a question button, users can use either voice input or manually type a question they might have. The question will then be smoothly integrated into the podcast and thoroughly explained. This is perfect for when you don't fully understand a topic. Additionally, after finishing listening to the podcast, users have the option to then generate flashcards to further help them understand the concept. With effective retention strategies, any user can fully understand and process any document or notes quickly.

## How we built it

The project was built on the Django framework using (obviously) Python. The database is running on MySQL. The podcast generation was done using the Gemini API since it was free, and the text-to-speech was created using Murf. AI since it offers the best balance of realistic voices and the number of free API calls.

## Challenges we ran into

We ran into multiple challenges while writing our program, the most notable being UI/UX. We want the users of our program to have the best experience, so a lot of time was spent on making our program look visually appealing and feel nice to use. However, because of the complicated nature of our program and its structure, styling our pages was not easy. One edit could break the entire thing, and that did happen many times. Another major issue was our planned Google Drive integration. Initially, we expected a quick and easy integration with our program, but in reality, it was the complete opposite. The biggest problem was communicating with the Google Cloud Console for OAuth. Oftentimes, logging in would not work, and if it did, it would not register properly. We debugged for hours, but unfortunately, we did end up having to remove the feature. This needed us to come up with another solution, which was to upload files locally and to send them to an LLM, which cost us extra time and came with its own challenges. In the end, we chose to prioritize stability over what we initially envisioned, but we are confident that our solutions will still work in the long run.

## Accomplishments that we're proud of
We are proud of how well our script and audio generation turned out. Our program uses AI to generate scripts in a specific format that is then turned into audio (TTS). Each line of the script is an individual file, which we then splice and combine to make them a whole, effectively becoming a podcast. We are most proud of our interactive features. We needed to be able to splice the audio clips whenever the user asks a question and modify as needed in real time, while still staying on topic and relevant.


## What we learned
We learned how to splice audio and integrate new audio clips when users had questions. Also, we learned a lot about frontend development with HTML, CSS, and JavaScript to perform complex animations for flashcards.


## What's next for StudyWave

The next step would be to develop our product into a phone app. We think most users will probably generate more podcasts on mobile devices. Although our website is currently compatible with mobile, we want to make sure users have as many options as possible. Additionally, we want built-in Google Drive integrations so that users can easily make any document a podcast.
