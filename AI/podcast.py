import requests
import os
from murf import Murf
from dotenv import load_dotenv

load_dotenv()


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
        audio_response.raise_for_status()  # Raises an HTTPError for bad responses
        
        # Save the audio file
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
        audio_response.raise_for_status()  # Raises an HTTPError for bad responses
        
        # Save the audio file
        with open(output_filename, 'wb') as f:
            f.write(audio_response.content)
        
        print(f"Audio file downloaded successfully as: {output_filename}")
        return output_filename
        
    except requests.exceptions.RequestException as e:
        print(f"Error downloading audio file: {e}")
        return None


    

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

lines = sample_script.split('\n')


i = 0
while i < len(lines):
    line = lines[i].strip()
    if not line:  # Skip empty lines
        i += 1
        continue
        
    if line.startswith("**Speaker 1:**"):
        text = line.replace("**Speaker 1:**", "").strip()
        downloaded_file = femalePodCaster(text, f"female_{i}.mp3")
    elif line.startswith("**Speaker 2:**"):
        text = line.replace("**Speaker 2:**", "").strip()
        downloaded_file = malePodCaster(text, f"male_{i}.mp3")
    
    i += 1

if downloaded_file:
    print(f"You can now play the audio file: {downloaded_file}")
