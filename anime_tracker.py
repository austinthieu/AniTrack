import aiosqlite
from jikan4snek import Jikan4SNEK
from tabulate import tabulate
from colorama import Fore, init
from datetime import datetime

# Initialize colorama for cross-platform color support
init(autoreset=True)


class AnimeTracker:
    def __init__(self, db_path="anime_tracker.db"):
        self.db_path = db_path
        self.jikan = Jikan4SNEK()

    async def initialize_database(self):
        """Create database and necessary tables if they don't exist."""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS watched_anime (
                    mal_id INTEGER PRIMARY KEY,
                    title TEXT,
                    watched_episodes INTEGER DEFAULT 0,
                    total_episodes INTEGER,
                    status TEXT,
                    user_rating REAL,
                    last_updated DATETIME,
                    notes TEXT
                )
            """)
            await db.commit()

    async def search_anime(self, query: str) -> None:
        """Search for anime and return formatted results."""
        anime_results = await self.jikan.search(query).anime()
        formatted_results = []

        for anime in anime_results["data"]:
            status_color = (
                Fore.GREEN if anime["status"] == "Finished Airing" else Fore.YELLOW
            )
            formatted_results.append(
                (
                    Fore.WHITE + anime["title"],
                    Fore.WHITE + str(anime.get("episodes", "Unknown")),
                    Fore.WHITE + anime["type"],
                    status_color + anime["status"],
                    Fore.CYAN + str(anime["mal_id"]),
                )
            )

        headers = [
            Fore.MAGENTA + "Title",
            Fore.MAGENTA + "Episodes",
            Fore.MAGENTA + "Type",
            Fore.MAGENTA + "Status",
            Fore.MAGENTA + "MAL ID",
        ]

        table = tabulate(
            formatted_results, headers=headers, tablefmt="simple", stralign="left"
        )
        print(table)

    async def add_to_watchlist(self, mal_id: int):
        """Add an anime to the watchlist."""
        # Fetch anime details
        anime_details = await self.jikan.get(mal_id).anime()

        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO watched_anime 
                (mal_id, title, total_episodes, status, last_updated) 
                VALUES (?, ?, ?, ?, ?)
            """,
                (
                    mal_id,
                    anime_details["data"]["title"],
                    anime_details["data"]["episodes"],
                    anime_details["data"]["status"],
                    datetime.now(),
                ),
            )
            await db.commit()

        print(f"{Fore.GREEN}Added {anime_details['data']['title']} to watchlist!")

    # Update watched progress and optional rating
    async def update_progress(self, mal_id: int, episodes: int, rating: float = None):
        async with aiosqlite.connect(self.db_path) as db:
            # Prepare the update query
            if rating is not None:
                await db.execute(
                    """
                    UPDATE watched_anime 
                    SET watched_episodes = ?, user_rating = ?, last_updated = ? 
                    WHERE mal_id = ?
                """,
                    (episodes, rating, datetime.now(), mal_id),
                )
            else:
                await db.execute(
                    """
                    UPDATE watched_anime 
                    SET watched_episodes = ?, last_updated = ? 
                    WHERE mal_id = ?
                """,
                    (episodes, datetime.now(), mal_id),
                )

            await db.commit()

        print(f"{Fore.GREEN}Updated progress for anime with MAL ID {mal_id}")

    # Display the current watch list
    async def view_watchlist(self):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                SELECT mal_id, title, watched_episodes, total_episodes, 
                       status, user_rating, last_updated 
                FROM watched_anime
            """)
            watchlist = await cursor.fetchall()

        if not watchlist:
            print(f"{Fore.YELLOW}Your watchlist is empty!")
            return

        formatted_watchlist = []
        for anime in watchlist:
            status_color = Fore.GREEN if anime[4] == "Finished Airing" else Fore.YELLOW
            formatted_watchlist.append(
                (
                    Fore.WHITE + str(anime[0]),  # MAL ID
                    Fore.WHITE + anime[1],  # Title
                    Fore.WHITE + f"{anime[2]}/{anime[3] or 'Unknown'}",  # Progress
                    status_color + (str(anime[4]) or "Unknown"),  # Status
                    Fore.WHITE
                    + (
                        str(anime[5]) if anime[5] is not None else "Not Rated"
                    ),  # Rating
                )
            )

        headers = [
            Fore.MAGENTA + "MAL ID",
            Fore.MAGENTA + "Title",
            Fore.MAGENTA + "Progress",
            Fore.MAGENTA + "Status",
            Fore.MAGENTA + "Rating",
        ]

        table = tabulate(
            formatted_watchlist,
            headers=headers,
            tablefmt="simple",
            stralign="left",
            numalign="left",
        )
        print(table)

    async def delete_anime_from_watchlist(self, mal_id):
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute(
                "SELECT title FROM watched_anime WHERE mal_id = ?", (mal_id,)
            )
            result = await cursor.fetchone()

            if result is None:
                print(
                    f"{Fore.YELLOW}No anime found with MAL ID {mal_id} in your watchlist."
                )

            await db.execute("DELETE FROM watched_anime where mal_id = ?", (mal_id,))

            await db.commit()

            print(f"{Fore.GREEN}Deleted {result[0]} from your watchlist!")
