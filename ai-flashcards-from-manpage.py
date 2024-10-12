import os
import subprocess
from openai import OpenAI
import genanki
import random
import typer
from typing import Optional
from rich import print as rprint
from rich.panel import Panel
from rich.console import Console

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = typer.Typer()
console = Console()

def get_man_page(command: str) -> str:
    try:
        result = subprocess.run(['man', command], capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError:
        return f"Error: Unable to retrieve man page for '{command}'"

def generate_flashcards(content: str, num_cards: int, model: str) -> list:
    prompt = f"Create {num_cards} flashcards from the following man page content. Format each flashcard as 'Question: ... Answer: ...'\n\n{content[:4000]}"

    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant that creates flashcards from given content."},
            {"role": "user", "content": prompt}
        ]
    )

    flashcards_text = response.choices[0].message.content
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

def print_flashcards(flashcards: list):
    for i, (question, answer) in enumerate(flashcards, 1):
        rprint(Panel(f"[bold]Question:[/bold] {question}\n\n[bold]Answer:[/bold] {answer}",
                     title=f"Flashcard {i}",
                     expand=False))

@app.command()
def main(
    command: str = typer.Argument(..., help="Command name to generate flashcards from its man page"),
    num_cards: Optional[int] = typer.Option(5, help="Number of flashcards to generate"),
    deck_name: Optional[str] = typer.Option("Man Page Flashcards", help="Name of the generated Anki deck"),
    model: Optional[str] = typer.Option("gpt-3.5-turbo", help="OpenAI model to use for flashcard generation")
):
    if not client.api_key:
        console.print("[bold red]Error:[/bold red] OPENAI_API_KEY environment variable is not set.")
        raise typer.Exit(code=1)

    with console.status("[bold green]Retrieving man page...[/bold green]"):
        console.print(f"Retrieving man page for '{command}'...")
        content = get_man_page(command)

    if content.startswith("Error:"):
        console.print(f"[bold red]{content}[/bold red]")
        raise typer.Exit(code=1)

    with console.status("[bold green]Generating flashcards...[/bold green]"):
        console.print(f"Generating {num_cards} flashcards...")
        flashcards = generate_flashcards(content, num_cards, model)

    console.print("\n[bold]Generated Flashcards:[/bold]")
    print_flashcards(flashcards)

    with console.status("[bold green]Creating Anki deck...[/bold green]"):
        console.print(f"Creating Anki deck '{deck_name}'...")
        create_anki_deck(flashcards, deck_name)

    console.print(f"\n[bold green]Anki deck '{deck_name}.apkg' has been created successfully.[/bold green]")
    console.print(f"Number of flashcards in the deck: {len(flashcards)}")

if __name__ == "__main__":
    app()

