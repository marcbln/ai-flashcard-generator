import os
import requests
from bs4 import BeautifulSoup
import openai
import genanki
import random
import typer
from typing import Optional

# Read OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

app = typer.Typer()

def download_webpage(url: str) -> str:
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.get_text()

def generate_flashcards(content: str, num_cards: int, model: str) -> list:
    prompt = f"Create {num_cards} flashcards from the following content. Format each flashcard as 'Question: ... Answer: ...'\n\n{content[:4000]}"
    
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that creates flashcards from given content."},
            {"role": "user", "content": prompt}
        ]
    )
    
    flashcards_text = response['choices'][0]['message']['content']
    flashcards = []
    
    for line in flashcards_text.split('\n'):
        if line.startswith("Question:"):
            question = line[9:].strip()
        elif line.startswith("Answer:"):
            answer = line[7:].strip()
            flashcards.append((question, answer))
    
    return flashcards

def create_anki_deck(flashcards: list, deck_name: str):
    model_id = random.randrange(1 << 30, 1 << 31)
    model = genanki.Model(
        model_id,
        'Simple Model',
        fields=[
            {'name': 'Question'},
            {'name': 'Answer'},
        ],
        templates=[
            {
                'name': 'Card 1',
                'qfmt': '{{Question}}',
                'afmt': '{{FrontSide}}<hr id="answer">{{Answer}}',
            },
        ])

    deck_id = random.randrange(1 << 30, 1 << 31)
    deck = genanki.Deck(deck_id, deck_name)

    for question, answer in flashcards:
        note = genanki.Note(
            model=model,
            fields=[question, answer]
        )
        deck.add_note(note)

    genanki.Package(deck).write_to_file(f'{deck_name}.apkg')

@app.command()
def main(
    url: str,
    num_cards: Optional[int] = typer.Option(5, help="Number of flashcards to generate"),
    deck_name: Optional[str] = typer.Option("AI Generated Flashcards", help="Name of the generated Anki deck"),
    model: Optional[str] = typer.Option("gpt-3.5-turbo", help="OpenAI model to use for flashcard generation")
):
    if not openai.api_key:
        typer.echo("Error: OPENAI_API_KEY environment variable is not set.")
        raise typer.Exit(code=1)

    typer.echo(f"Downloading content from {url}...")
    content = download_webpage(url)

    typer.echo(f"Generating {num_cards} flashcards...")
    flashcards = generate_flashcards(content, num_cards, model)

    typer.echo(f"Creating Anki deck '{deck_name}'...")
    create_anki_deck(flashcards, deck_name)

    typer.echo(f"Anki deck '{deck_name}.apkg' has been created.")

if __name__ == "__main__":
    app()
