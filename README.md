# AI Flashcard Generator

This project contains two scripts that generate Anki flashcards using OpenAI's GPT models:
1. `ai-flashcards-from-url.py`: Generates flashcards from web content.
2. `ai-flashcards-from-manpage.py`: Generates flashcards from man pages.

Both scripts use AI to generate flashcards and create Anki decks.

## Quickstart

To quickly generate flashcards from a webpage:

```
python ai-flashcards-from-url.py https://docs.sqlalchemy.org/en/20/glossary.html --num-cards 10 --deck-name "SQLAlchemy Glossary"
```

To generate flashcards from a man page:

```
python ai-flashcards-from-manpage.py ls --num-cards 10 --deck-name "ls Command"
```

These commands will create Anki deck files (.apkg) with 10 flashcards each, based on the specified content.

## Features

- Web scraping to extract content from a given URL
- Man page content extraction
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

Run the scripts with the following commands:

For web content:
```
python ai-flashcards-from-url.py [OPTIONS] URL
```

For man pages:
```
python ai-flashcards-from-manpage.py [OPTIONS] COMMAND
```

Options for both scripts:
- `--num-cards INTEGER`: Number of flashcards to generate (default: 5)
- `--deck-name TEXT`: Name of the generated Anki deck (default: "AI Generated Flashcards")
- `--model TEXT`: OpenAI model to use for flashcard generation (default: "gpt-3.5-turbo")

Examples:
```
python ai-flashcards-from-url.py https://en.wikipedia.org/wiki/Artificial_intelligence --num-cards 10 --deck-name "AI Basics"
python ai-flashcards-from-manpage.py grep --num-cards 8 --deck-name "grep Command"
```

These commands will generate Anki deck files (.apkg) in the current directory.

## Dependencies

The project uses the following libraries:

- `requests`: For making HTTP requests to fetch web content.
- `beautifulsoup4`: For parsing and extracting data from HTML.
- `openai`: For generating flashcards using OpenAI's language models.
- `genanki`: For creating Anki deck files.
- `typer`: For building the command-line interface.
- `click`: A dependency of Typer for creating command-line interfaces.
- `rich`: For rich text and beautiful formatting in the terminal.

See `requirements.txt` for the full list of dependencies and their versions.

## License

This project is open-source and available under the MIT License.
