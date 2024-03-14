""" Get data on how much England mens batters averages have increased due to Bazzball
    Main function at bottom"""

import requests
from bs4 import BeautifulSoup
import polars as pl

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
}


def get_players_data() -> list[dict[str, float, float, float]]:
    """Return list of player dictionaries containing name,
    average when Stokes is/isn't captain and the increase between them"""
    player_codes = [
        "665053",  # Crawley
        "521637",  # Duckett
        "887207",  # Pope
        "303669",  # Root
        "911707",  # Brook
        "297433",  # Bairstow
        "311158",  # Stokes
        "364788",  # Foakes
    ]
    players_data = []
    for player_code in player_codes:
        cricinfo_player_url = (
            f"https://stats.espncricinfo.com/ci/engine/player/{player_code}"
            ".html?class=1;template=results;type=allround"
        )
        page = requests.get(cricinfo_player_url, headers=headers, timeout=20)
        soup = BeautifulSoup(page.content, "html.parser")

        name = get_player_name(soup)
        print(name)

        captain_breakdown_rows = get_table_rows_for_captain_data(soup)
        players_data.append(get_player_data_breakdown(captain_breakdown_rows, name))

    return players_data


def get_player_name(soup: BeautifulSoup) -> str:
    """Get the players name from the BeautifulSoup scraped output"""
    name_element = soup.find("div", class_="icc-home")
    return name_element.text.split("/")[2].strip()


def get_player_data_breakdown(captain_breakdown_rows: BeautifulSoup, name: str):
    """Get dictionary of player name, average dependent on captain and the Bazzball increase"""
    if is_stokes_only_captain(captain_breakdown_rows):
        elements = captain_breakdown_rows[0].find_all("td")
        stokes_average = float(elements[4].text)
        player_data_element = {
            "player": name,
            "Stokes_ave": stokes_average,
            "not_stokes_ave": "nan",
            "increase": "nan",
        }
    else:
        not_stokes_runs, not_stokes_dismissals = 0, 0
        for row in captain_breakdown_rows:
            if "Stokes" in row.text:
                elements = row.find_all("td")
                stokes_average = float(elements[5].text)
            else:
                elements = row.find_all("td")
                not_stokes_runs += int(elements[3].text)
                not_stokes_dismissals += round(
                    float(elements[3].text) / float(elements[5].text)
                )

        not_stokes_average = (
            not_stokes_runs / not_stokes_dismissals if not_stokes_dismissals else 0
        )
        player_data_element = {
            "player": name,
            "Stokes_ave": stokes_average,
            "not_stokes_ave": round(not_stokes_average, 2),
            "increase": round(stokes_average - not_stokes_average, 2),
        }
    return player_data_element


def is_stokes_only_captain(captain_breakdown_rows: list[BeautifulSoup]) -> bool:
    """check if player has only played under Stokes - needs to be treated differently"""
    return len(captain_breakdown_rows) == 1


def get_table_rows_for_captain_data(soup: BeautifulSoup):
    """Filter down BeautifulSoup scraped data from Cricinfo to the relevant rows"""
    tables = soup.find_all("table")
    summary_table = tables[3]
    summary_table_elements = summary_table.find_all("tbody")
    captain_breakdown = summary_table_elements[6]
    captain_breakdown_rows = captain_breakdown.find_all("tr")[1:]
    return captain_breakdown_rows


if __name__ == "__main__":
    df = pl.DataFrame(get_players_data())
    print(df)

    print(
        "Stokes & McCullum have increased average of batters per innings by: ",
        round(
            df.with_columns(pl.col("increase").cast(pl.Float32).fill_nan(0.0))
            .select(pl.col("increase").sum())
            .item(),
            1,
        ),
    )
