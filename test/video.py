from requests import post

TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTYxOTE5Mzc1MiwianRpIjoiMDljYzIyYmMtODdiMC00N2IzLWIzZDUtNzdlMzk4MDYxZTU2IiwibmJmIjoxNjE5MTkzNzUyLCJ0eXBlIjoiYWNjZXNzIiwic3ViIjoxLCJleHAiOjE2MTkxOTczNTJ9.LVgZwBmlr76EdBcLaGGFRgDtOjTDlsFu2JYln5M-7ho"
files = {"file": open("Test.mp4", "rb")}
response = post(
    "http://localhost:4610/videos/",
    files=files,
    headers={"Authorization": "Bearer " + TOKEN},
    data={"title": "Imposter", "authors": "", "description": "AMOGUS"},
)
print(response.json())
