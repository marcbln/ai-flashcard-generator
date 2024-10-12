"""
Man Page Flashcard Generator

This script generates Anki flashcards from Unix man pages. It employs a sophisticated
section-splitting strategy to process the man page content effectively:

1. Initial Split: The man page is first split into major sections using double newlines 
   (\n\n) as delimiters. This typically separates main sections of a man page.

2. Refinement: Each resulting section is then analyzed:
   a. If a section is longer than 4000 characters (to stay within typical API limits), 
      it's further split into subsections using single newlines (\n) as delimiters.
   b. Sections under 4000 characters are kept intact.

3. Flashcard Generation: The script attempts to distribute flashcard generation evenly 
   across all sections, ensuring comprehensive coverage of the man page content.

This approach allows for intelligent processing of man pages, respecting their structure
while also managing content length for effective API usage and flashcard creation.
"""

import os
import subprocess
import re
from openai import OpenAI
import genanki
import random
import typer
from typing import Optional
from rich import print as rprint
from rich.panel import Panel
from rich.console import Console
from pathlib import Path

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
app = typer.Typer()
console = Console()


def get_man_page(command: str) -> str:
    try:
        result = subprocess.run(['man', command], capture_output=True, text=True)
        return result.stdout
    except subprocess.CalledProcessError:
        return f"Error: Unable to retrieve man page for '{command}'"


def split_into_sections(content: str) -> list:
    # Split by double newlines (major sections)
    major_sections = re.split(r'\n\n+', content)
    console.print(f"[bold]Initial split:[/bold] Found {len(major_sections)} major sections")

    # Further split long sections by single newlines
    refined_sections = []
    for i, section in enumerate(major_sections, 1):
        if len(section) > 4000:
            subsections = section.split('\n')
            refined_sections.extend(subsections)
            console.print(
                f"  Section {i}: Split into {len(subsections)} subsections (original length: {len(section)} chars)")
        else:
            refined_sections.append(section)
            console.print(f"  Section {i}: Kept intact (length: {len(section)} chars)")

    console.print(f"[bold]Final result:[/bold] {len(refined_sections)} total sections for processing")
    return refined_sections


def generate_flashcards(sections: list, num_cards: int, model: str) -> list:
    flashcards = []
    cards_per_section = max(1, num_cards // len(sections))

    for i, section in enumerate(sections, 1):
        if len(flashcards) >= num_cards:
            break

        cards_to_generate = min(num_cards - len(flashcards), cards_per_section)
        console.print(
            f"Generating {cards_to_generate} flashcards from section {i}/{len(sections)} (length: {len(section)} chars)")

        prompt = f"Create {cards_to_generate} flashcards from the following man page section (section {i}/{len(sections)}). Format each flashcard as 'Question: ... Answer: ...'\n\n{section[:4000]}"

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system",
                 "content": "You are a helpful assistant that creates flashcards from given content."},
                {"role": "user", "content": prompt}
            ]
        )

        flashcards_text = response.choices[0].message.content
        section_flashcards = []

        for line in flashcards_text.split('\n'):
            if line.startswith("Question:"):
                question = line[9:].strip()
            elif line.startswith("Answer:"):
                answer = line[7:].strip()
                section_flashcards.append((question, answer))

        flashcards.extend(section_flashcards)
        console.print(f"  Generated {len(section_flashcards)} flashcards from this section")

    console.print(f"[bold]Total flashcards generated:[/bold] {len(flashcards)}")
    return flashcards[:num_cards]


def create_anki_deck(flashcards: list, deck_name: str, command: str):
    output_dir = Path("anki_decks")
    output_dir.mkdir(exist_ok=True)

    filename = f"{command}.apkg" if deck_name == "Man Page Flashcards" else f"{deck_name}.apkg"
    output_path = output_dir / filename
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

    genanki.Package(deck).write_to_file(str(output_path))
    return output_path


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

    with console.status("[bold green]Processing man page...[/bold green]"):
        console.print("Splitting man page into sections...")
        sections = split_into_sections(content)

    with console.status("[bold green]Generating flashcards...[/bold green]"):
        console.print(f"Generating {num_cards} flashcards...")
        flashcards = generate_flashcards(sections, num_cards, model)

    console.print("\n[bold]Generated Flashcards:[/bold]")
    print_flashcards(flashcards)

    with console.status("[bold green]Creating Anki deck...[/bold green]"):
        console.print(f"Creating Anki deck '{deck_name}'...")
        output_path = create_anki_deck(flashcards, deck_name, command)

    console.print(f"\n[bold green]Anki deck '{output_path}' has been created successfully.[/bold green]")
    console.print(f"Number of flashcards in the deck: {len(flashcards)}")


if __name__ == "__main__":
    app()