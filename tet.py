import requests

account_name = "fitpackcourse"
secret_key = "dCnlLJwQjnR1eqhvZNySeIE2DqIeAFS1rQvGbDrUCOIWp2l4chiXwRwEUUrgSHROCFVSia47dOF1N2t1RLsMRZVrOfpNrxMcPEJiAy7sAik8Q8eN4FzzrOkcCze5KuWK"

url = f"https://{account_name}.getcourse.ru/pl/api/account/groups"
params = {
    "key": secret_key
}

response = requests.get(url, params=params)

if response.status_code == 200:
    groups = response.json()
    print("✅ Список групп:")
    print(groups)
else:
    print(f"❌ Ошибка: {response.status_code}")
    print(response.text)