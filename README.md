# irish-passport-tracking-python

A Python library used to query information from the Irish Passport Service to track the progress of a passport application.

<h2>Motivation</h2>
The only way to currently query information is through a browser with JavaScript enabled. This presents a barrier to 
tracking an application. 

The motivation behind this project is to provide the user a simple single event action to get 
data about their application that can be used in further applications to alert the user about updates from the Passport 
Service.

<h2>Usage</h2>
To get information about your passport application:

```python
from passport_tracking_client import PassportTrackingClient

client = PassportTrackingClient()

status_data = client.get_status(reference="REFERENCE")
```

Even though the reference's for applications are numeric, a string has been used to ensure that if a reference starts 
with 0, that no digits are trimmed. 

This will return a dict object containing the expected completion date as well as the current status of the application.

<h2>Authentication</h2>
The service operates with a single-phase authentication process. The initial GET request sends the user a request token 
which must be provided in the subsequent POST request to retrieve data. Not sending the token will result in a 500 response.

<h2>Contributing</h2>
Pull requests are welcomed. Currently the client only retrieves information about the current status and does not return 
the history of the application.