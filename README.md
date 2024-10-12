# AI Flashcard Generator

This script generates Anki flashcards from web content using OpenAI's GPT models. It downloads the content of a given URL, uses AI to generate flashcards, and creates an Anki deck.

## Features

- Web scraping to extract content from a given URL
- AI-powered flashcard generation using OpenAI's GPT models
- Anki deck creation with customizable number of cards and deck name
- Command-line interface for easy use

## Installation

1. Ensure you have Python 3.7+ installed on your system.

2. Install `uv` if you haven't already:
   ```
   pip install uv
   ```

3. Clone this repository:
   ```
   git clone https://github.com/yourusername/ai-flashcard-generator.git
   cd ai-flashcard-generator
   ```

4. Create a virtual environment and install dependencies using `uv`:
   ```
   uv venv
   source .venv/bin/activate  # On Windows, use: .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

5. Set up your OpenAI API key as an environment variable:
   ```
   export OPENAI_API_KEY='your-api-key-here'
   ```

## Usage

Run the script with the following command:

```
python ai-flashcard-generator.py [OPTIONS] URL
```

Options:
- `--num-cards INTEGER`: Number of flashcards to generate (default: 5)
- `--deck-name TEXT`: Name of the generated Anki deck (default: "AI Generated Flashcards")
- `--model TEXT`: OpenAI model to use for flashcard generation (default: "gpt-3.5-turbo")

Example:
```
python ai-flashcard-generator.py https://en.wikipedia.org/wiki/Artificial_intelligence --num-cards 10 --deck-name "AI Basics"
```

This will generate an Anki deck file named "AI Basics.apkg" in the current directory.

## Dependencies

See `requirements.txt` for a list of dependencies.

## License

This project is open-source and available under the MIT License.
