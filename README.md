# clixmlcreds

<p align="center">
  <img alt="Static Badge" src="https://img.shields.io/badge/WDP-API-badge?style=flat&color=blue">
  <img alt="Static Badge" src="https://img.shields.io/badge/Credentials-Clixml?style=plastic&color=white">
  <img alt="Static Badge" src="https://img.shields.io/badge/XML-hashed?style=flat-square&color=purple">
</p>


Simple solution to call Windows prompt for credentials through PowerShell command Get-Credential. Result of command above will be exported in xml using Windows Data Protection API (Export-Clixml PowerShell command).

Allow you to store your credentials and reuse it in scripts by `CredentialManager.read(...)`.
All credentials are hashed and stored in the [secrets](src/clixmlcreds/secrets) folder `<cred_name>.xml`.

Very handy when you just need to store credentials for different services and call them based on different `<cred_name>`.


## Usage

```python
from clixmlcreds import Credential, CredentialManager


cred_name: str = 'Name_of_secret_xml_file'  # cred name without file extension


if not Credential.exists(name=cred_name):
    CredentialManager.write(
        cred_name=cred_name,
        username='Your_username',
        prompt_message='Input username and password:'
    )
cred = CredentialManager.read(cred_name=cred_name)
username = cred.username
password = cred.get_password()  # return unsecure password string
```
