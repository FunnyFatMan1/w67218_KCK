import requests
import time

def get_puuid(nickname, tagline, api_key):
    url = f"https://europe.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{nickname}/{tagline}"
    response = requests.get(url, headers={"X-Riot-Token": api_key})
    if response.status_code == 200:
        return response.json().get("puuid")
    elif response.status_code == 404:
        return None
    else:
        raise Exception(f"Błąd pobierania PUUID: {response.status_code} - {response.text}")

def get_match_ids(puuid, count, region, api_key):
    url = f"https://{region}.api.riotgames.com/tft/match/v1/matches/by-puuid/{puuid}/ids?count={count}"
    response = requests.get(url, headers={"X-Riot-Token": api_key})
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Błąd pobierania listy meczów: {response.status_code} - {response.text}")

def get_match_data(match_id, region, api_key):
    url = f"https://{region}.api.riotgames.com/tft/match/v1/matches/{match_id}"
    while True:
        response = requests.get(url, headers={"X-Riot-Token": api_key})
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            time.sleep(1)  # limit rate, czekaj i próbuj ponownie
        else:
            raise Exception(f"Błąd pobierania danych meczu: {response.status_code} - {response.text}")

def analyze_matches(matches, puuid):
    placements = []
    for match in matches:
        participants = match.get("info", {}).get("participants", [])
        for p in participants:
            if p.get("puuid") == puuid:
                placements.append(p.get("placement"))
                break

    top1 = sum(1 for x in placements if x == 1)
    top4 = sum(1 for x in placements if x <= 4)
    avg = round(sum(placements) / len(placements), 2) if placements else None

    return {
        "total": len(placements),
        "average": avg,
        "top1_percent": round((top1 / len(placements)) * 100, 1) if placements else 0,
        "top4_percent": round((top4 / len(placements)) * 100, 1) if placements else 0,
        "placement_distribution": {str(i): placements.count(i) for i in range(1, 9)}
    }
