import os
import json
import requests
import folium
from geopy.distance import lonlat, distance
from dotenv import load_dotenv
from pprint import pprint


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(
        base_url,
        params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        },
    )
    response.raise_for_status()
    found_places = response.json()["response"]["GeoObjectCollection"]["featureMember"]

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant["GeoObject"]["Point"]["pos"].split(" ")
    return lon, lat


def main():
    load_dotenv()
    apikey = os.environ["YA_API"]

    with open("coffee.json", "r", encoding="CP1251") as my_file:
        file_contents = my_file.read()

    user_location = input("Где вы находитесь? ")
    user_lonlat = fetch_coordinates(apikey, user_location)

    coffee_shops = json.loads(file_contents)
    nearby_shops = []
    for shop in coffee_shops:
        shop_location = dict()
        shop_location["title"] = shop["Name"]
        shop_location["distance"] = distance(
            lonlat(*user_lonlat),
            lonlat(shop["Longitude_WGS84"], shop["Latitude_WGS84"], 0),
        ).km
        shop_location["longitude"] = shop["Longitude_WGS84"]
        shop_location["latitude"] = shop["Latitude_WGS84"]
        nearby_shops.append(shop_location)

    def get_distance(coffee_shop):
        return coffee_shop["distance"]

    result = sorted(nearby_shops, key=get_distance)
    top_5 = result[:5]

    map_result = folium.Map(location=user_lonlat[::-1], zoom_start=12)
    folium.Marker(
        location=user_lonlat[::-1],
        tooltip="Вы тут",
        popup=user_lonlat,
        icon=folium.Icon(color="green"),
    ).add_to(map_result)

    for shop in top_5:
        folium.Marker(
            location=[shop["latitude"], shop["longitude"]],
            tooltip="Просмотр",
            popup=shop["title"],
            icon=folium.Icon(color="orange"),
        ).add_to(map_result)
    map_result.save("map.html")

    pprint(top_5, sort_dicts=False)


if __name__ == "__main__":
    main()
