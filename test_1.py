import requests

url = "https://movies-tv-shows-database.p.rapidapi.com/"

querystring = {"year":"2020","page":"1"}

headers = {
	"Type": "get-movies-byyear",
	"X-RapidAPI-Key": "202fdfb8c7mshef5d2122d4c5d9ap1210b4jsn91783e932c90",
	"X-RapidAPI-Host": "movies-tv-shows-database.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())