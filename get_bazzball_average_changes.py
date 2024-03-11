# Get data on how much England mens batters averages have increased due to Bazzball
import requests
from bs4 import BeautifulSoup
import polars as pl

headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36"
}

def get_player_data():
    player_codes = [
        "665053",
        "521637",
        "887207",
        "303669",
        "911707",
        "297433",
        "311158",
        "364788",
    ]
    player_data = []
    for player_code in player_codes:
        url = f"https://stats.espncricinfo.com/ci/engine/player/{player_code}.html?class=1;template=results;type=allround"
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, "html.parser")

        name = get_player_name(soup)
        print(name)

        captain_breakdown_rows = get_table_rows_for_captain_data(soup)

        # loop over rows check if captain is Stokes, and get averages
        if is_stokes_only_captain(captain_breakdown_rows):
            player_data_element = get_player_data_for_stokes_only(captain_breakdown_rows, name)
        else:
            player_data_element = get_player_data_for_multiple_captains(captain_breakdown_rows, name)
        player_data.append(player_data_element)
    return player_data


def get_player_name(soup):
    name_element = soup.find("div", class_="icc-home")
    return name_element.text.split("/")[2].strip()

def is_stokes_only_captain(captain_breakdown_rows: list[str]) -> bool:
    return len(captain_breakdown_rows) == 1

def get_player_data_for_stokes_only(captain_breakdown_rows, name):
    elements = captain_breakdown_rows[0].find_all("td")
    stokes_average = float(elements[4].text)
    return {
            "player": name,
            "Stokes_ave": stokes_average,
            "not_stokes_ave": "nan",
            "increase": "nan",
        }

def get_player_data_for_multiple_captains(captain_breakdown_rows, name):
    not_stokes_runs = 0
    not_stokes_dismissals = 0
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
    return {
            "player": name,
            "Stokes_ave": stokes_average,
            "not_stokes_ave": round(not_stokes_average, 2),
            "increase": round(stokes_average - not_stokes_average, 2),
        }


def get_table_rows_for_captain_data(soup):
    tables = soup.find_all("table")
    summary_table = tables[3]
    summary_table_elements = summary_table.find_all("tbody")
    captain_breakdown = summary_table_elements[6]
    captain_breakdown_rows = captain_breakdown.find_all("tr")[1:]
    return captain_breakdown_rows


if __name__ == "__main__":
    df = pl.DataFrame(get_player_data())
    print(df)

    print(
        "Stokes has increased average of batters per innings by: ",
        round(
            df.with_columns(pl.col("increase").cast(pl.Float32).fill_nan(0.0))
            .select(pl.col("increase").sum())
            .item(),
            1,
        ),
    )