# from pydub import AudioSegment

# def merge_audio_clips():

#     combined_audio = AudioSegment.empty()

#     for i in range(60):
#         try:
#             audio_clip = AudioSegment.from_file(f"/Users/aditya/Documents/Programming/Hackathon/KTHACKS/StudyWaves/AI/female_{i}.mp3")
#             combined_audio += audio_clip
#         except Exception as e:
#             print(f"Error loading file /Users/aditya/Documents/Programming/Hackathon/KTHACKS/StudyWaves/AI/female_{i}.mp3: {e}")

#         try:
#             audio_clip = AudioSegment.from_file(f"/Users/aditya/Documents/Programming/Hackathon/KTHACKS/StudyWaves/AI/male_{i}.mp3")
#             combined_audio += audio_clip
#         except Exception as e:
#             print(f"Error loading file ./StudyWaves/AI/male_{i}.mp3: {e}")

#     combined_audio.export("final_merged.mp3", format="mp3") # or another format
#     print(f"Merged audio saved to final_merged.mp3")
# merge_audio_clips()



from pydub import AudioSegment
from pydub.playback import play
import time
import keyboard
from google import genai
from google.genai import types
import requests
from murf import Murf


from pynput import keyboard
import os
from dotenv import load_dotenv

def femalePodCaster(text, output_filename="output_audio.wav"):
    client = Murf(api_key=os.environ.get("MURF_API_KEY"))

    response = client.text_to_speech.generate(
        text = text,
        voice_id = "en-US-natalie",
        style = "Conversational",
        multi_native_locale = "en-US"
        )

    try:
        audio_response = requests.get(response.audio_file)
        audio_response.raise_for_status() 
        with open(output_filename, 'wb') as f:
            f.write(audio_response.content)
        
        print(f"Audio file downloaded successfully as: {output_filename}")
        return output_filename
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading audio file: {e}")
        return None
    

def malePodCaster(text, output_filename="output_audio.wav"):
    client = Murf(api_key=os.environ.get("MURF_API_KEY"))

    response = client.text_to_speech.generate(
        text = text,
        voice_id = "en-US-charles",
        style = "Conversational",
        multi_native_locale = "en-US"
        )

    try:
        audio_response = requests.get(response.audio_file)
        audio_response.raise_for_status()
        
        # Save the audio file
        with open(output_filename, 'wb') as f:
            f.write(audio_response.content)
        
        print(f"Audio file downloaded successfully as: {output_filename}")
        return output_filename
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading audio file: {e}")
        return None

stop = False

load_dotenv()
def reCast(read, unread, question):
    global stop
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-flash-preview-05-20"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text = f"""Read:{read}
                                        UnRead:{unread}
                                        question: {question}"""),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text="""
You are a helpful and creative podcast script editor.

You will be given:

The podcast script so far, split into two parts:

Read: already spoken content,

Unread: upcoming lines that will be spoken immediately after your segment.

A listener question.

Your task is to write a bridging script segment that fits naturally between the Read and Unread sections.

Your output must:
Begin after the last line of the Read section (but do not include or paraphrase that last line).

Never repeat, rephrase, summarize, or echo any content from the Read or Unread sections.

This includes facts, examples, phrases, definitions, or points that have already been or will be mentioned.

If your segment includes anything the Unread section already covers, it will result in duplicate content - which is unacceptable.

Answer or acknowledge the listener's question directly.

If the Unread section already answers the question fully, say so briefly and then transition to the next part.

Match the tone, voice, pacing, and speaker style of the existing podcast.

Optionally add personality or insight, only if it doesn't create repetition.
                                 
Format your response as a script, with speaker labels (e.g., Speaker 1, Speaker 2) and natural podcast dialogue or monologue.

CRITICAL RULE:
This is not a summary or preview. Your segment must be unique. Any idea, phrase, or point already covered in either Read or Unread should be treated as off-limits.

Keep it natural and concise:
Do not over-explain. A short, direct, well-written segment is far better than unnecessary filler.
"""),
        ],
    )
    response = client.models.generate_content(
        model=model,
        contents=contents,
        config=generate_content_config,
    )

    lines = response.text.split('\n')


    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
            
        if line.startswith("**Speaker 1:**"):
            text = line.replace("**Speaker 1:**", "").strip()
            downloaded_file = femalePodCaster(text, f"/Users/aditya/Documents/Programming/Hackathon/KTHACKS/StudyWaves/AI/questions/female_{i}.mp3")
        elif line.startswith("**Speaker 2:**"):
            text = line.replace("**Speaker 2:**", "").strip()
            downloaded_file = malePodCaster(text, f"/Users/aditya/Documents/Programming/Hackathon/KTHACKS/StudyWaves/AI/questions/male_{i}.mp3")
        
        i += 1

    stop= False
    play_audio_clips_sequentially(response.text, "/Users/aditya/Documents/Programming/Hackathon/KTHACKS/StudyWaves/AI/questions")

    directory_path = "/Users/aditya/Documents/Programming/Hackathon/KTHACKS/StudyWaves/AI/questions"
    for i in os.listdir(directory_path):
        file_path = os.path.join(directory_path, i)
        if os.path.isfile(file_path):
            os.remove(file_path)


def on_press(key):
    print
    global stop
    try:
        if key.char == 'p':
            print("Playback stopped.")
            stop = True
            return False
    except AttributeError:
        pass


def splitter(i, script):
    # output = []
    lines = script.split('\n')
    splitSpot = i + 1
    read = '\n'.join(lines[:splitSpot])
    unread = '\n'.join(lines[splitSpot:])
    
    # a = 0
    # while a < len(lines) and a < i:
    #     line = lines[a].strip()
    #     if not line:  # Skip empty lines
    #         a += 1
    #         continue
            
    #     if line.startswith("**Speaker 1:**"):
    #         text = line.replace("**Speaker 1:**", "").strip()
    #         output.append({"female": text})
    #     elif line.startswith("**Speaker 2:**"):
    #         text = line.replace("**Speaker 2:**", "").strip()
    #         output.append({"male": text})
        
    #     a += 1
    return read, unread
    
    

def play_audio_clips_sequentially(script, path):
    global stop
    listener = keyboard.Listener(on_press=on_press)
    listener.start()
    for i in range(60):
        try:
            # Play female voice clip if exists
            female_file = f"{path}/female_{i}.mp3"
            audio_clip = AudioSegment.from_file(female_file)
            #print(f"Playing female_{i}.mp3")
            play(audio_clip)
        except Exception as e:
            #print(f"Error loading/playing file {female_file}: {e}")
            pass

        try:
            # Play male voice clip if exists
            male_file = f"{path}/male_{i}.mp3"
            audio_clip = AudioSegment.from_file(male_file)
            #print(f"Playing male_{i}.mp3")
            play(audio_clip)
        except Exception as e:
            #print(f"Error loading/playing file {male_file}: {e}")
            pass

        if stop:
            read, unread = splitter(i, script)
            # print(read)
            # print("_________________________________")
            # print(unread)
            reCast(read, unread, input("Enter a question to continue the script: "))
            stop = False

    print("Finished playing all audio clips")

sample_script = """
    **Speaker 1:** Welcome to "Leading the Way," the podcast that explores the fascinating world of leadership. Today, we're diving deep into leadership styles – what they are, how they work, and why understanding them is crucial for anyone looking to make an impact.

**Speaker 2:** That's right! Leadership isn't just about being in charge; it's about guiding, inspiring, and bringing people together. At its core, leadership is about being able to persuade people around you to work together with you on something, or to do what you instruct. And effective leaders often share some key traits: they're decisive, great communicators, adaptable, and often deeply trusting of their teams.

**Speaker 1:** Absolutely. And while those traits are important, the *way* a leader operates can vary dramatically. Many of the fundamental ideas about leadership styles stem from the work of psychologist Kurt Lewin, often called the father of social psychology. His studies in the 1930s really laid the groundwork for understanding group dynamics and organizational behavior, and he identified three core styles: autocratic, democratic, and laissez-faire.

**Speaker 2:** Let's break those down, starting with the **autocratic style**. This is where one person holds all the power, giving clear orders with very little input from others. Think of it as a top-down approach.

**Speaker 1:** Qualities of an autocratic leader often include being very decisive and self-confident. The pros here are quick decision-making, especially in critical situations, and very clear directions, which can minimize confusion.

**Speaker 2:** But there are definitely cons. Employees might lack motivation because they have no involvement in decisions, and the team can become overly reliant on the leader. This style works well in industries like the military or crisis management, where rapid, clear directives are essential.

**Speaker 1:** But you wouldn't want it in, say, a marketing firm or a startup, where innovation and collaboration are key. A great example of an autocratic leader in practice is Bill Belichick, the former coach of the New England Patriots – known for his absolute control and clear, non-negotiable instructions.

**Speaker 2:** Moving on to the opposite end of the spectrum, we have the **democratic leadership style**. Here, leaders gather input from the entire team before making a decision. It’s all about collective effort.

**Speaker 1:** Democratic leaders are typically excellent communicators and very approachable. The big pros are happier, more engaged employees, and often more innovative solutions because you're tapping into a wider range of ideas.

**Speaker 2:** The downsides? Slower decision-making, as you're waiting for everyone's input, and the potential for conflict when ideas clash. This style is fantastic for tech companies or in education, where brainstorming and collaborative problem-solving thrive.

**Speaker 1:** But it might struggle in high-pressure jobs where quick decisions are needed, or with teams that are very inexperienced and need more guidance. Bill Gates, known for fostering a culture of collaboration at Microsoft, is a good example of a democratic leader.

**Speaker 2:** Next up is the **laissez-faire style**. This is French for "let them do," and it’s truly hands-off. Employees have a lot more decision-making power, with minimal impact from the leader.

**Speaker 1:** Laissez-faire leaders are highly trusting and excellent delegators. The benefits are increased independence and innovation among team members, and potentially faster timelines because there's no micromanagement.

**Speaker 2:** However, the cons include a potential lack of direction for the team and it can be really hard for unmotivated people to thrive in this environment. It's great for startups or research environments where self-starters are common, but terrible for manufacturing or teams that need constant supervision. Warren Buffett, known for trusting his company managers to run their businesses with minimal interference, exemplifies this style.

**Speaker 1:** So those are Lewin's foundational styles. But leadership has evolved, and we have more nuanced approaches today. One that's really gained traction is **transformational leadership**.

**Speaker 2:** This is a style that truly inspires employees to work toward a shared goal, fostering growth and deep loyalty. Transformational leaders are often charismatic, inspirational, and strong communicators.

**Speaker 1:** The pros are high employee loyalty, incredible innovation, and adaptability. But a potential con is burnout, either for the leader or the team, due to the intense focus on vision, and potentially too much reliance on the leader's personal vision.

**Speaker 2:** This style shines in non-profits or growing companies that need a compelling vision to rally around. It might not be ideal for routine jobs or very short-term projects. Nelson Mandela is a powerful example of a transformational leader who inspired a nation.

**Speaker 1:** Another key modern style is **situational leadership**. This is a flexible approach where the leader adapts their style to what the team or the specific situation demands.

**Speaker 2:** Situational leaders are characterized by their flexibility and active listening skills. The benefits include improved performance across the team and greater employee growth, as the leader adjusts their support as needed.

**Speaker 1:** The potential downsides are that it can sometimes lead to confusion if the style shifts too often, and it might focus too much on short-term goals rather than a consistent long-term vision. It's excellent for fast-changing industries or teams with diverse skill levels.

**Speaker 2:** But less effective for repetitive tasks or environments with very rigid rules. Dwight D. Eisenhower, known for his ability to adapt his leadership as a military commander and later as president, is a great example of a situational leader.

**Speaker 1:** Finally, let's talk about **paternalistic leadership**. This is where the leader acts almost like a parent, focusing deeply on employee well-being and cultivating a family-like workplace culture.

**Speaker 2:** Paternalistic leaders are nurturing and empowering. The big pros are high job satisfaction and strong employee retention because people feel cared for.

**Speaker 1:** On the flip side, there can be a perception of favoritism, and it might limit delegation because the leader wants to be involved in everything. It's often very effective in family-owned businesses or small, close-knit teams.

**Speaker 2:** However, it might not suit highly innovative fields that require more autonomy, or very large companies where that personal touch is harder to maintain. Jack Ma, the founder of Alibaba, often described as fostering a close-knit, family-like culture among his employees, fits this description.

**Speaker 1:** So, as we've explored, there's no single "best" leadership style. Effective leadership isn't about fitting into one mold, but about understanding these different approaches and knowing when to apply them.

**Speaker 2:** Exactly. Whether you're leading a large corporation or a small team, developing your own leadership skills comes down to self-awareness, knowing your team, and being willing to adapt. It's a continuous journey of learning and applying these different styles strategically.

**Speaker 1:** And that's our deep dive into leadership styles for today. We hope this helps you not only understand the leaders around you but also develop your own leadership journey.

**Speaker 2:** Join us next time for more insights on "Leading the Way!"
    """

play_audio_clips_sequentially(sample_script, "/Users/aditya/Documents/Programming/Hackathon/KTHACKS/StudyWaves/AI/podcast")