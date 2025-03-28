import asyncio
import argparse
from jikan4snek import Jikan4SNEK, dump
from tabulate import tabulate
from colorama import Fore, Style, init


async def search_anime(query):
    jikan = Jikan4SNEK()
    anime_results = await jikan.search(query).anime()

    formatted_results = []
    for anime in anime_results["data"]:
        status_color = (
            Fore.GREEN if anime["status"] == "Finished Airing" else Fore.YELLOW
        )

        formatted_results.append(
            (
                Fore.WHITE + anime["title"],
                Fore.WHITE + str(anime["episodes"]),
                Fore.WHITE + anime["type"],
                status_color + anime["status"],
            )
        )

    headers = [
        Fore.MAGENTA + "Title",
        Fore.MAGENTA + "Episodes",
        Fore.MAGENTA + "Type",
        Fore.MAGENTA + "Status",
    ]

    table = tabulate(
        formatted_results, headers=headers, tablefmt="simple", stralign="left"
    )

    print(table)


def main():
    # Set up argparse for command-line argument parsing
    parser = argparse.ArgumentParser(description="Search for anime using Jikan API")
    parser.add_argument("anime", type=str, help="The title of the anime to search for")
    args = parser.parse_args()

    # Run the search function asynchronously
    asyncio.run(search_anime(args.anime))


if __name__ == "__main__":
    main()
