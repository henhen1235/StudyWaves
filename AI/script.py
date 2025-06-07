import base64
import os
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

def createScript(prompts):
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemini-2.5-flash-preview-05-20"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=prompts),
            ],
        ),
    ]
    generate_content_config = types.GenerateContentConfig(
        response_mime_type="text/plain",
        system_instruction=[
            types.Part.from_text(text="""You are a podcast writer helping the user turn their notes and documents into an engaging and accurate podcast script between two people.
Use the provided source material to write a script that sounds natural, conversational, and informative.
You may summarize, restructure, and paraphrase content, but do not invent facts.
Format the output like a real podcast script with speaker labels (e.g., Speaker 1, Speaker 2)."""),
        ],
    )
    print(client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ))
    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        print(chunk.text, end="")


prompt = """2.3 Leadership Styles
Define what leadership is and identify traits of effective leaders.
Describe behaviors that effective leaders demonstrate.
Specify the contexts in which various leadership styles are effective.
Explain the concepts of transformational, transactional, charismatic, servant, and authentic leadership.
Develop your own leadership skills.
Leadership: Being able to persuade people around you to work together with you on something or to do what you instruct.

Kurt Lewin was a psychologist who is known as the starter of social psychology. His work is what helps modern companies understand group dynamics and organizational behavior. He is most famous for his leadership style studies where he found autocratic, democratic, and laissez-faire types. 

Autocratic

Definition:  A style of leading where one person has all of the power and gives clear orders with little input from others.

Qualities: Decisive, Self-confident 

Pros: Quick decision making in important situations, clear directions so less confusion

Cons: Lack of motivation from employees because no involvement, over-reliance on the leader

Good Industry: Military, Crisis management

Bad Industry: Marketing, Start-ups

Person:Bill Belichick



Democratic 

Definition: A style where leaders will gather the entire team’s input before making a decision for a collective effort.

Qualities: Good communicator, approachable

Pros: More happy employees because of engagement, innovative solutions

Cons: Slower decision making, conflict in ideas


Good Industry: Tech companies, education

Bad Industry: High-pressure jobs, teams with inexperienced members


Person: Bill Gates

Laissez-Faire

Definition: An approach to leading where the employees have more decision making power with little leader impact.

Qualities: Trusting, good delegator

Pros: More independence and innovation, faster timeline because no micromanagement

Cons: Lack of direction, hard for unmotivated people

Good Industry: Start-ups, Research

Bad Industry: manufacturing, teams that need supervision

Person: Warren Buffett



Transformational 

Definition: A newer style of leadership that inspired employees work toward a shared goal to create growth and loyalty

Qualities: Charismatic, inspirational, strong communicator

Pros: High employee loyalty, innovation and adaptability 

Cons: Maybe burnout, too much reliance on leader’s vision

Good Industry: non-profits, growing companies

Bad Industry: Routine jobs, short projects.

Person: Nelson Mandela


Situational 

Definition: A flexible leadership style that adapts to what the team or situation demands.

Qualities: Flexibility, Active listener

Pros: improved performance, more employee growth 

Cons: confusion, only focused on short term goals

Good Industry: fast changing industries, teams with different skills

Bad Industry: repetitive tasks, rigid rules.

Person: Dwight D. Eisenhower




Paternalistic 

Definition: A leadership style where the leader kind of acts like a parent and focuses on employee well-being and creating a family like workplace culture.

Qualities: Nurturing, Empowering

Pros: High job satisfaction, Strong retention 

Cons: Perceived favoritism, limited delegation

Good Industry: family owned business, small teams

Bad Industry: innovative fields, large companies.

Person: Jack Ma

"""

createScript(prompt);
