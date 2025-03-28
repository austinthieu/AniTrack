import asyncio
import argparse
from anime_tracker import AnimeTracker


def main():
    # Set up argparse for command-line argument parsing
    parser = argparse.ArgumentParser(description="Anime Tracking CLI")

    # Add subcommands for different actions
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search for anime")
    search_parser.add_argument(
        "query", type=str, help="The title of the anime to search for"
    )

    # Add to watchlist command
    add_parser = subparsers.add_parser("add", help="Add anime to watchlist")
    add_parser.add_argument("mal_id", type=int, help="MyAnimeList ID of the anime")

    # Update progress command
    update_parser = subparsers.add_parser(
        "update", help="Update anime watching progress"
    )
    update_parser.add_argument("mal_id", type=int, help="MyAnimeList ID of the anime")
    update_parser.add_argument("episodes", type=int, help="Number of episodes watched")
    update_parser.add_argument(
        "--rating", type=float, help="Optional rating for the anime"
    )

    # Delete from watchlist command
    delete_parser = subparsers.add_parser("delete", help="Delete anime from watchlist")
    delete_parser.add_argument(
        "mal_id", type=int, help="MyAnimeList ID of the anime to delete"
    )

    # View watchlist command
    subparsers.add_parser("list", help="View your watchlist")

    # Parse arguments
    args = parser.parse_args()

    # Create AsyncIO event loop
    tracker = AnimeTracker()

    # Run appropriate async function based on command
    async def run():
        await tracker.initialize_database()

        if args.command == "search":
            await tracker.search_anime(args.query)
        elif args.command == "add":
            await tracker.add_to_watchlist(args.mal_id)
        elif args.command == "update":
            await tracker.update_progress(args.mal_id, args.episodes, args.rating)
        elif args.command == "delete":
            await tracker.delete_anime_from_watchlist(args.mal_id)
        elif args.command == "list":
            await tracker.view_watchlist()
        else:
            parser.print_help()

    # Run the async function
    asyncio.run(run())


if __name__ == "__main__":
    main()
