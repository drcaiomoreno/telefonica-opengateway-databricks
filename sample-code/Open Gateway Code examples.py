# Databricks notebook source
# MAGIC %md
# MAGIC #Get authorized with CIBA
# MAGIC This authorization flow is the same for all the APIs that uses a backend flow authentication.
# MAGIC The code example next below must work just changin the content of client_id, client_secret and purpose that you need.

# COMMAND ----------

# Credentials, headers and imports needed
import requests
import base64

client_id = "your-client-id"
client_secret = "your-client-secret"
purpose = "dpv:Purpose#API"

credentials = f"{client_id}:{client_secret}"
credentials = base64.b64encode(credentials.encode()).decode()

headers = {
    "accept": "application/json",
    "content-type": "application/x-www-form-urlencoded",
    "authorization": f"Basic {credentials}"
}


# COMMAND ----------

# Authentication: step 1 (auth_req_id)

url_auth = "https://sandbox.opengateway.telefonica.com/apigateway/bc-authorize"

payload_auth = {
    "purpose": f"{purpose}",
    "login_hint": "tel:+34666555343"
}

auth_res = requests.post(url_auth, data=payload_auth, headers=headers)

print(auth_res)
print(auth_res.text)

# COMMAND ----------

# Authentication: step 2 (token)

url_token = "https://sandbox.opengateway.telefonica.com/apigateway/token"
auth_res = auth_res.json().get("auth_req_id")

payload_token = {
    "auth_req_id": f"{auth_res}",
    "grant_type": "urn:openid:params:grant-type:ciba"
}

token = requests.post(url_token, data=payload_token, headers=headers)

print(token)
print(token.text)
token = token.json().get("access_token")

# COMMAND ----------

# Headers needed for calls

headers_calls = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {token}"
}

# COMMAND ----------

# MAGIC %md
# MAGIC # KyC code example
# MAGIC Make sure the value purpose at the top of the page is similar to dpv:FraudPreventionAndDetection#kyc

# COMMAND ----------

# Check if the customer name matches

url_kycmatch = "https://sandbox.opengateway.telefonica.com/apigateway/kyc-match/v0/match"

payload = {
    "phoneNumber": "+34629255833",
    "idDocument": "66666666q",
    "name": "Federica Sanchez Arjona",
    "email": "abc@example.com",
    "country": "UK"
}

response = requests.post(url_kycmatch, json=payload, headers=headers_calls).json()
nameMatch = response.get("nameMatch")
status = [response.get("status"), response.get("code"), response.get("message")]

if nameMatch is None:
    print(f"Error {status[0]}: {status[1]}\n{status[2]}")
elif nameMatch == "true":
    print("The customer name matches")
else:
    print("The customer name doesn't match")
    

# COMMAND ----------

# MAGIC %md
# MAGIC # SIM Swap code example
# MAGIC Make sure the value purpose at the top of the page is similar to dpv:FraudPreventionAndDetection#sim-swap
# MAGIC

# COMMAND ----------

# Check if the SIM of phoneNumber value was swapped in the last 100 days

url_simswap_check = "https://sandbox.opengateway.telefonica.com/apigateway/sim-swap/v0/check"

payload_checkswap = {
       "phoneNumber": "+34666555343",
        "maxAge": 2400
}

response = requests.post(url_simswap_check, json=payload_checkswap, headers=headers_calls).json()
status = [response.get("status"), response.get("code"), response.get("message")]
swapped = response.get("swapped")

if swapped is None:
        print(f"Error {status[0]}: {status[1]}\n{status[2]}")
elif swapped == "true":
        print("Sim was swapped in the last 100 days")
else:
        print("Sim wasn't swapped")

# COMMAND ----------

# Get when the SIM swapped for last time

url_latestsimswap = "https://sandbox.opengateway.telefonica.com/apigateway/sim-swap/v0/retrieve-date"

payload_lastswap = {
       "phoneNumber": "+34679768182",
}

response = requests.post(url_latestsimswap, json=payload_lastswap, headers=headers_calls).json()
status = [response.get("status"), response.get("code"), response.get("message")]
latestSimChange = response.get("latestSimChange")

if latestSimChange is None:
        print(f"Error {status[0]}: {status[1]}\n{status[2]}")
else:
       print(f"SIM was swapped for the last time in {latestSimChange}")