# Project Idea Generator

A command-line utility that generates creative project ideas using the Gemini API via REST.

## Setup

1. Install the required packages:
```
pip install -r requirements.txt
```

2. Set your Gemini API key:
   - Create a `.env` file in the project directory and add:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```
   - Or set it directly as an environment variable:
   ```
   export GEMINI_API_KEY="your_api_key_here"
   ```

## Usage

Run the script with your desired parameters:

```
python project_generator.py --genre "web app" --ideas 3 --feasibility medium
```

### Parameters

- `--genre` (required): The category of project (e.g., "web app", "mobile game", "AI", "business")
- `--ideas`: Number of project ideas to generate (default: 3)
- `--feasibility`: How realistic the projects should be: "high" (1-4 weeks), "medium" (1-3 months), or "low" (ambitious but possible)
- `--tech`: Specific technologies to focus on (comma-separated)
- `--depth`: Detail level for descriptions: "low", "medium", or "high"

### Examples

Generate 5 highly feasible web app ideas:
```
python project_generator.py --genre "web app" --ideas 5 --feasibility high
```

Generate 3 machine learning project ideas using specific technologies:
```
python project_generator.py --genre "machine learning" --tech "Python,TensorFlow,scikit-learn" --depth high
```

Generate 2 ambitious mobile app ideas:
```
python project_generator.py --genre "mobile app" --ideas 2 --feasibility low
``` 