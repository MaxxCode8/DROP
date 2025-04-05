import re
import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def extract_project_info(text_content, project_name):
    """
    Extracts the description and core technologies of a project from the text content.
    """
    pattern = rf"""
    Project\ Name:\s*{re.escape(project_name)}\s*\r?\n\r?\n
    Description:\s*\r?\n
    (.*?)\r?\n\r?\n
    Tech\ Stack:\s*\r?\n
    (.*?)(?=\r?\n\r?\n[-]+|$)
    """
    match = re.search(pattern, text_content, re.DOTALL | re.VERBOSE)
    if match:
        description = match.group(1).strip()
        technologies = match.group(2).strip()
        return description, technologies
    return None, None


def select_projects(text_file):
    """
    Selects two projects from the text file.
    """
    try:
        with open(text_file, 'r') as f:
            text_content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Text file '{text_file}' not found.")

    # Corrected regular expression to handle project name extraction
    project_names = re.findall(r"Project Name: (.*?)\n", text_content)

    if len(project_names) < 2:
        raise ValueError("Less than two projects found in the text file.")

    return project_names[0], project_names[1]

def generate_rap_battle_prompt(project1_name, project2_name, text_file):
    """
    Generates the prompt for the Gemini API based on two selected projects.
    """
    try:
        with open(text_file, 'r') as f:
            text_content = f.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Text file '{text_file}' not found.")

    project1_description, project1_technologies = extract_project_info(text_content, project1_name)
    project2_description, project2_technologies = extract_project_info(text_content, project2_name)

    if not project1_description or not project2_description:
        raise ValueError("Could not extract project descriptions from text.")

    prompt = f"""
    Generate a rap battle between two web application projects: {project1_name} and {project2_name}.

    Project 1: {project1_name}
    Description: {project1_description}
    Technologies: {project1_technologies}

    Project 2: {project2_name}
    Description: {project2_description}
    Technologies: {project2_technologies}

    The rap battle should be in the style of two women arguing, with sharp, witty, and sassy disses.
    Each project should have at least two verses.
    The total length of the rap battle should be under 2900 characters.
    The output should only be the lyrics of the rap battle, nothing else.
    The projects should speak in turns, just like a rap battle show.
    The first project should open up the battle with a context of itself and some bars of other.
    The next stanza of second project, will have the input as the stanze the first project created, the project and description of the first project and project and description of the second project.
    and just like this the loop will continue until the rap battle lyrics are of 2850 chars.
    """
    return prompt

def call_gemini_api(api_key, prompt):
    """
    Calls the Gemini API with the given prompt and returns the response.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"

    headers = {
        "Content-Type": "application/json"
    }

    data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        response.raise_for_status()  # Raise an exception for HTTP errors

        result = response.json()
        # Extract the generated text from the response
        if "candidates" in result and result["candidates"]:
            content = result["candidates"][0]["content"]
            if "parts" in content and content["parts"]:
                text = content["parts"][0].get("text", "")
                return text

        return "No content generated"
    except Exception as e:
        raise Exception(f"Error calling Gemini API: {str(e)}")

def save_lyrics_to_file(lyrics, filename):
    """
    Saves the lyrics to a .txt file.
    """
    try:
        with open(filename, 'w') as f:
            f.write(lyrics)
        print(f"Lyrics saved to {filename}")
    except Exception as e:
        raise Exception(f"Error saving lyrics to file: {e}")

# Main execution
if __name__ == "__main__":
    text_file = os.path.join("output.txt")
    lyrics_file = os.path.join("lyrics.txt")

    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    try:
        project1_name, project2_name = select_projects(text_file)
        prompt = generate_rap_battle_prompt(project1_name, project2_name, text_file)
        lyrics = call_gemini_api(api_key, prompt)
        save_lyrics_to_file(lyrics, lyrics_file)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
