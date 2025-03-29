#!/usr/bin/env python3

import argparse
import os
import requests
import json
from dotenv import load_dotenv

load_dotenv()

def setup_api_key():
    """Get the Gemini API key from environment variables."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    return api_key

def generate_prompt(genre, num_ideas, feasibility, tech_stack=None, description_depth="medium"):
    """Generate the prompt for the LLM based on user inputs."""
    
    feasibility_guide = {
        "high": "projects that can be completed within 1-4 weeks with common technologies",
        "medium": "projects that would take 1-3 months to build with reasonable effort",
        "low": "ambitious projects that are technically challenging but still possible"
    }
    
    depth_guide = {
        "low": "brief overview",
        "medium": "moderate detail",
        "high": "comprehensive breakdown"
    }
    
    prompt = f"""Generate {num_ideas} interesting and creative project ideas in the '{genre}' category.

Focus on {feasibility_guide.get(feasibility, "feasible projects")}

For each project idea, provide:
1. A catchy project name
2. A {depth_guide.get(description_depth, "detailed")} description of what the project does
3. The core technologies or tech stack needed"""
    
    if tech_stack:
        prompt += f"\n4. Explanation of how to implement this using: {tech_stack}"
    
    prompt += "\n\nEnsure the ideas are specific, practical, and have clear value. Avoid overly generic or unrealistic concepts."
    
    return prompt

def generate_project_ideas(api_key, prompt):
    """Get project ideas from Gemini API based on the prompt."""
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
        return f"Error generating project ideas: {str(e)}"

def main():
    parser = argparse.ArgumentParser(description="Generate creative project ideas using Gemini API")
    
    parser.add_argument("--genre", type=str, required=True, 
                        help="Project genre (e.g., 'web app', 'mobile game', 'machine learning')")
    parser.add_argument("--ideas", type=int, default=3,
                        help="Number of project ideas to generate (default: 3)")
    parser.add_argument("--feasibility", type=str, choices=["high", "medium", "low"], default="medium",
                        help="How feasible/realistic the projects should be (default: medium)")
    parser.add_argument("--tech", type=str,
                        help="Specific technologies to use (comma-separated)")
    parser.add_argument("--depth", type=str, choices=["low", "medium", "high"], default="medium",
                        help="Detail level for project descriptions (default: medium)")
    
    args = parser.parse_args()
    
    try:
        api_key = setup_api_key()
        prompt = generate_prompt(
            args.genre, 
            args.ideas, 
            args.feasibility, 
            args.tech, 
            args.depth
        )
        
        print("\nGenerating project ideas...\n")
        result = generate_project_ideas(api_key, prompt)
        print(result)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 