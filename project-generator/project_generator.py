#!/usr/bin/env python3

import argparse
import os
import requests
import json
import re
import random
import time
import sys
import threading
from dotenv import load_dotenv

load_dotenv()

# ASCII art for entertainment
LOGO = """
╔═══════════════════════════════════════════════╗
║                                               ║
║   🚀 Project Idea Generator 3000 🚀           ║
║                                               ║
║   Cooking up awesome project ideas...         ║
║                                               ║
╚═══════════════════════════════════════════════╝
"""

class LoadingAnimation:
    """Simple loading animation for the terminal."""
    
    def __init__(self, message="Processing"):
        self.message = message
        self.is_running = False
        self.animation_thread = None
        self.animation_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        
    def start(self):
        self.is_running = True
        self.animation_thread = threading.Thread(target=self._animate)
        self.animation_thread.daemon = True
        self.animation_thread.start()
        
    def stop(self):
        self.is_running = False
        if self.animation_thread:
            self.animation_thread.join()
        # Clear the line
        sys.stdout.write("\r" + " " * (len(self.message) + 10) + "\r")
        sys.stdout.flush()
        
    def _animate(self):
        i = 0
        while self.is_running:
            frame = self.animation_chars[i % len(self.animation_chars)]
            sys.stdout.write(f"\r{frame} {self.message}...")
            sys.stdout.flush()
            time.sleep(0.1)
            i += 1

def setup_api_key():
    """Get the Gemini API key from environment variables."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
    return api_key

def generate_single_idea_prompt(genre, feasibility, business_domain=None, tech_stack=None, description_depth="medium", architecture_style="balanced"):
    """Generate a prompt for a single project idea."""
    
    feasibility_guide = {
        "high": "a project that can be completed within 1-4 weeks with common technologies",
        "medium": "a project that would take 1-3 months to build with reasonable effort",
        "low": "an ambitious project that is technically challenging but still possible"
    }
    
    depth_guide = {
        "low": "brief overview",
        "medium": "moderate detail",
        "high": "comprehensive breakdown"
    }
    
    architecture_contexts = {
        "minimalist": """Prefer minimal, lightweight tech stacks that focus on simplicity and efficiency.
Choose technologies that have low overhead, small footprints, and fast performance.
Avoid complex frameworks when simpler libraries or vanilla code would suffice.
Value developer productivity and code maintainability through simplicity.""",

        "modern": """Use current industry standard technologies that are widely adopted.
Balance between established reliability and modern capabilities.
Choose tech that has good community support and extensive documentation.
Focus on technologies that provide a good developer experience without sacrificing performance.""",

        "cutting_edge": """Incorporate emerging technologies and frameworks at the forefront of innovation.
Experiment with new approaches that may offer significant advantages in specific domains.
Consider technologies that might not be mainstream yet but show promise for the future.
Prioritize capabilities and features even if they come with some complexity or learning curve.""",

        "robust": """Prioritize battle-tested technologies known for stability and reliability.
Choose tech stacks that excel at scalability and maintainability for long-term projects.
Focus on established frameworks with strong enterprise adoption and support.
Value comprehensive solutions that handle edge cases and provide built-in safeguards."""
    }
    
    genre_contexts = {
        "biz_stuff": """A business-focused software solution that solves a real-world problem.
Focus on a practical application that addresses a genuine business challenge or improves efficiency.
The project should be targeted at a specific industry or common workplace pain point.
It should have a clear value proposition and potential for real-world implementation.""",

        "fun_stuff": """A creative and enjoyable project that sparks joy and imagination.
It should have an element of surprise, delight, or novelty that makes it fun to build and share.
The project can be whimsical, experimental, or have eye-catching visuals/interactions.
It should inspire creativity and potentially demonstrate interesting technical concepts.""",

        "learn_x_stuff": """An educational project that involves building an existing system from scratch to understand how it works.
Focus on reimplementing a popular tool, database, or widely-used product to learn its inner workings.
The project should provide a valuable learning experience about fundamental concepts.
The emphasis should be on the educational value and deep understanding gained from the implementation process."""
    }
    
    # List of possible system design types to ensure diversity
    system_design_types = [
        "web application",
        "mobile application",
        "desktop application",
        "microservice",
        "command-line tool",
        "API service",
        "data processing pipeline",
        "embedded system",
        "IoT solution",
        "browser extension",
        "developer library/framework",
        "blockchain application",
        "AI/ML model deployment",
        "DevOps automation tool",
        "distributed system",
        "serverless solution"
    ]
    
    # Choose a random system design type
    chosen_system_type = random.choice(system_design_types)
    
    # Select the appropriate context based on genre
    genre_context = genre_contexts.get(genre.lower().replace(" ", "_"), "")
    
    # Select the appropriate architecture context
    arch_context = architecture_contexts.get(architecture_style.lower(), "")
    
    business_domains = [
        "healthcare", "finance", "education", "retail", "manufacturing", 
        "logistics", "agriculture", "real estate", "hospitality", "transportation",
        "construction", "energy", "legal services", "entertainment", "human resources",
        "marketing", "customer service", "supply chain", "inventory management", "project management",
        "data analytics", "security", "environmental services", "non-profit", "government services"
    ]
    
    # Use specified domain or pick a random one if in biz_stuff genre
    domain_instruction = ""
    if genre.lower() == "biz_stuff":
        chosen_domain = business_domain if business_domain else random.choice(business_domains)
        domain_instruction = f"""This idea MUST be focused on the {chosen_domain} industry/domain and NOT be a generic CRM, ERP, or management system.
Create something unique and specific to actual {chosen_domain} industry needs.
The solution should be implemented as a {chosen_system_type} (not necessarily a web application)."""
    else:
        domain_instruction = f"Design this as a {chosen_system_type} (not necessarily a web application)."
    
    prompt = f"""Generate ONE interesting and creative project idea in the '{genre}' category.

{genre_context}

{domain_instruction}

Focus on {feasibility_guide.get(feasibility, "a feasible project")}

For tech stack recommendations:
{arch_context}

Format your response using exactly this structure:
Project Name: [A catchy, descriptive name]

Description: 
[A {depth_guide.get(description_depth, "detailed")} description of what the project does. Use bullet points for features where appropriate.]

Tech Stack:
[The core technologies or tech stack needed, with specific reasoning for each choice]
- Explain why each technology is particularly well-suited for this project
- Consider how the technologies work together as a cohesive stack
- Address any trade-offs or alternatives that were considered
"""
    
    if tech_stack:
        prompt += f"\nImplementation with {tech_stack}:\n[Explanation of how to implement this using these specific technologies, justifying why they align with the project requirements]"
    
    prompt += "\n\nEnsure the idea is specific, practical, and has clear value. Avoid generic or unrealistic concepts. DO NOT include any introductory or concluding text outside the structure above. Use proper formatting with bullet points, line breaks, etc. to make the output readable."
    
    return prompt, chosen_domain if genre.lower() == "biz_stuff" else None, chosen_system_type

def generate_single_project_idea(api_key, prompt):
    """Get a single project idea from Gemini API based on the prompt."""
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
        ],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.95,
            "maxOutputTokens": 2048
        }
    }
    
    loading = LoadingAnimation("Consulting the AI oracle")
    loading.start()
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data))
        loading.stop()
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        result = response.json()
        # Extract the generated text from the response
        if "candidates" in result and result["candidates"]:
            content = result["candidates"][0]["content"]
            if "parts" in content and content["parts"]:
                text = content["parts"][0].get("text", "")
                
                # Skip cleaning if we got an empty response
                if not text.strip():
                    print("Warning: Received empty response from API")
                    return "# Error: No Content Generated\n\nThe API returned an empty response. Please try again."
                
                # Debug: Print raw response for troubleshooting
                # print("Raw API response:", text[:500] + "..." if len(text) > 500 else text)
                
                # Clean up any introductory text before the first heading 
                # but PRESERVE all content after the first heading
                text = re.sub(r'^.*?(# .*?)$', r'\1', text, flags=re.DOTALL, count=1)
                
                # Fix any malformed markdown headings
                text = re.sub(r'^#+\s*([^\n]+)', r'# \1', text, count=1)
                
                return text
        
        print("Warning: No valid content found in API response")
        return "# Error: Invalid Response\n\nThe API response did not contain valid content. Please try again."
    except Exception as e:
        loading.stop()
        error_message = str(e)
        print(f"Error in API request: {error_message}")
        return f"# Error Generating Project Idea\n\n{error_message}"

def clean_markdown(text):
    """Clean up the markdown text to remove introductions, etc."""
    # Remove introductory phrases like "Here are X project ideas..."
    text = re.sub(r'^.*?#\s*', '# ', text, flags=re.DOTALL, count=1)
    
    # Remove any trailing conclusions
    text = re.sub(r'\n\n.*?I hope .*$', '', text, flags=re.DOTALL)
    text = re.sub(r'\n\n.*?These ideas .*$', '', text, flags=re.DOTALL)
    
    return text.strip()

def generate_multiple_diverse_ideas(api_key, genre, num_ideas, feasibility, tech_stack, description_depth, architecture_style):
    """Generate multiple diverse project ideas by making separate API calls for each."""
    ideas = []
    used_domains = set()
    used_system_types = set()
    
    print(f"Generating {num_ideas} diverse project ideas in the '{genre}' category...\n")
    
    for i in range(num_ideas):
        # For business ideas, exclude already used domains
        business_domain = None
        if genre.lower() == "biz_stuff":
            business_domains = [
                "healthcare", "finance", "education", "retail", "manufacturing", 
                "logistics", "agriculture", "real estate", "hospitality", "transportation",
                "construction", "energy", "legal services", "entertainment", "human resources",
                "marketing", "customer service", "supply chain", "inventory management", "project management",
                "data analytics", "security", "environmental services", "non-profit", "government services"
            ]
            available_domains = [d for d in business_domains if d not in used_domains]
            if available_domains:
                business_domain = random.choice(available_domains)
        
        prompt, chosen_domain, chosen_system_type = generate_single_idea_prompt(
            genre, 
            feasibility, 
            business_domain,
            tech_stack, 
            description_depth,
            architecture_style
        )
        
        system_type_info = f", System Type: {chosen_system_type}" if chosen_system_type else ""
        print(f"Generating idea {i+1}/{num_ideas}..." + (f" (Domain: {chosen_domain}{system_type_info})" if chosen_domain else f"{system_type_info}"))
        
        # Try up to 3 times in case we get empty content
        max_attempts = 3
        for attempt in range(max_attempts):
            idea_text = generate_single_project_idea(api_key, prompt)
            
            # Check if we got a valid response with content
            if idea_text and ("# Error" not in idea_text) and len(idea_text.strip()) > 20:
                break
                
            if attempt < max_attempts - 1:
                print(f"  Attempt {attempt+1} failed, retrying...")
                time.sleep(1)  # Add delay before retry
        
        ideas.append(idea_text)
        
        if chosen_domain:
            used_domains.add(chosen_domain)
        
        if chosen_system_type:
            used_system_types.add(chosen_system_type)
        
        # Add a small delay to avoid rate limiting
        if i < num_ideas - 1:
            time.sleep(1)
    
    # Join the ideas with separator between them, but not at the beginning
    if not ideas:
        return "No ideas generated."
    elif len(ideas) == 1:
        return ideas[0]
    else:
        separator = "\n\n" + ("-" * 80) + "\n\n"
        return separator.join(ideas)

def save_to_markdown(content, output_file="project_ideas.txt"):
    """Save the generated content to a text file."""
    with open(output_file, "w") as f:
        f.write(content)
    return output_file

def get_random_choices():
    """Generate random choices for all parameters."""
    genres = ["biz_stuff", "fun_stuff", "learn_x_stuff"]
    feasibilities = ["high", "medium", "low"]
    architectures = ["minimalist", "modern", "cutting_edge", "robust"]
    depths = ["low", "medium", "high"]
    
    return {
        "genre": random.choice(genres),
        "ideas": 3,  # Fixed at 3 ideas for random mode
        "feasibility": random.choice(feasibilities),
        "architecture": random.choice(architectures),
        "depth": random.choice(depths)
    }

def display_random_choices(choices):
    """Display the randomly chosen parameters in a visually appealing way."""
    print("\n" + "=" * 60)
    print(" 🎲  RANDOM MODE ACTIVATED  🎲 ")
    print("=" * 60)
    print(f"🔹 Genre: {choices['genre']}")
    print(f"🔹 Number of ideas: {choices['ideas']}")
    print(f"🔹 Feasibility: {choices['feasibility']}")
    print(f"🔹 Detail level: {choices['depth']}")
    print(f"🔹 Architecture style: {choices['architecture']}")
    print("=" * 60 + "\n")

def main():
    parser = argparse.ArgumentParser(description="Generate creative project ideas using Gemini API")
    
    parser.add_argument("--genre", type=str,
                        choices=["biz_stuff", "fun_stuff", "learn_x_stuff"],
                        help="Project genre type (biz_stuff, fun_stuff, or learn_x_stuff)")
    parser.add_argument("--ideas", type=int, default=2,
                        help="Number of project ideas to generate (default: 2)")
    parser.add_argument("--feasibility", type=str, choices=["high", "medium", "low"], default="medium",
                        help="How feasible/realistic the projects should be (default: medium)")
    parser.add_argument("--tech", type=str,
                        help="Specific technologies to use (comma-separated)")
    parser.add_argument("--depth", type=str, choices=["low", "medium", "high"], default="medium",
                        help="Detail level for project descriptions (default: medium)")
    parser.add_argument("--architecture", type=str, 
                       choices=["minimalist", "modern", "cutting_edge", "robust"], default="modern",
                       help="Architecture style preference for tech stack recommendations (default: modern)")
    parser.add_argument("--output", type=str, default="project_ideas.txt",
                       help="Output file name (default: project_ideas.txt)")
    parser.add_argument("--random", action="store_true",
                       help="Use random values for all parameters except tech stack")
    
    args = parser.parse_args()
    
    # Print logo
    print(LOGO)
    
    try:
        api_key = setup_api_key()
        
        # Handle random mode
        if args.random:
            random_choices = get_random_choices()
            display_random_choices(random_choices)
            
            # Use random choices but keep tech stack and output file as specified
            genre = random_choices["genre"]
            ideas = random_choices["ideas"]
            feasibility = random_choices["feasibility"]
            depth = random_choices["depth"]
            architecture = random_choices["architecture"]
            tech_stack = args.tech
            output_file = args.output
        else:
            # Make sure genre is provided if not in random mode
            if not args.genre:
                parser.error("the --genre argument is required unless --random is specified")
                
            genre = args.genre
            ideas = args.ideas
            feasibility = args.feasibility
            depth = args.depth
            architecture = args.architecture
            tech_stack = args.tech
            output_file = args.output
        
        result = generate_multiple_diverse_ideas(
            api_key,
            genre, 
            ideas, 
            feasibility, 
            tech_stack, 
            depth,
            architecture
        )
        
        output_file = save_to_markdown(result, output_file)
        print(f"\n✅ Project ideas successfully saved to {output_file}")
        print("\nThanks for using Project Idea Generator 3000! Happy coding! 🚀")
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == "__main__":
    main() 