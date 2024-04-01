# clixmlcreds

> Simple solution to call Windows prompt for credentials through PowerShell command Get-Credential. Result of command above will be exported in xml using Windows Data Protection API (Export-Clixml PowerShell command).
> Allow you to store your credentials and reuse it in scripts by `CredentialManager.read(...)`.

## Usage

```python
from credentials import Credential, CredentialManager


if not Credential.exists(name='Name_of_secret_xml_file'):
    CredentialManager.write(
        cred_name='Name_of_secret_xml_file',
        username='Your_username',
        prompt_message='Input username and password:'
    )
cred = CredentialManager.read(cred_name='Name_of_secret_xml_file')
username = cred.username
password = cred.get_password()  # return unsecure password string
```
