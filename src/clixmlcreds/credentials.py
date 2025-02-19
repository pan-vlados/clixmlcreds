import binascii
import stat
from dataclasses import dataclass
from pathlib import Path
from typing import Any, ClassVar, Generic, Optional, Tuple, TypeVar

import win32crypt

from .errors import InvalidCredentialError, PasswordTypeError
from .utils import CredentialToClixml


_Tpwd = TypeVar('_Tpwd', str, bytes)


@dataclass
class Credential(Generic[_Tpwd]):
    name: str
    username: str
    password: _Tpwd

    def get_password(self) -> str:
        """UNSECURE!
        Return decrypted string representation of password.
        """
        if not isinstance(self.password, bytes):
            raise PasswordTypeError
        password, _ = CredentialManager.decrypt(password=self.password)
        return password

    @staticmethod
    def exists(name: str) -> bool:
        """Check if Credential with scpecified name exists in CredentialManager path."""
        return CredentialManager.get_xml_path(cred_name=name).exists()


class CredentialManager:  # thanks to https://dev.to/samklingdev/use-windows-data-protection-api-with-python-for-handling-credentials-5d4j
    path: ClassVar[Path] = Path(__file__).absolute().parent / 'secrets'
    encoding: ClassVar[str] = 'utf-16-le'
    cred_to_xml_script_path: ClassVar[Path] = (
        Path(__file__).absolute().parent / 'Export-CredentialToClixml.ps1'
    )

    @classmethod
    def encrypt(
        cls,
        password: str,
        desc: Optional[str] = '',
        entropy: Optional[bytes] = None,
        flags: int = 0,
        ps: Optional[Any] = None,
    ) -> bytes:
        """Encrypt by Windows Data Protection API."""
        return win32crypt.CryptProtectData(
            password.encode(cls.encoding), desc, entropy, None, ps, flags
        )

    @classmethod
    def decrypt(
        cls,
        password: bytes,
        entropy: Optional[bytes] = None,
        flags: int = 0,
        ps: Optional[Any] = None,
    ) -> Tuple[str, str]:
        """UNSECURE!
        Decrypt Windows Data Protection API.
        """
        desc, password = win32crypt.CryptUnprotectData(
            password, entropy, None, ps, flags
        )
        return password.decode(cls.encoding), desc

    @classmethod
    def get_xml_path(cls, cred_name: str) -> Path:
        return cls.path / f'{cred_name}.xml'

    @classmethod
    def read(cls, cred_name: str) -> 'Credential[bytes]':
        """Read user's credential (Import-Clixml PowerShell command).
        Credentials still will be secured using Windows Data Protection API.
        """
        with open(
            cls.get_xml_path(cred_name=cred_name), encoding=cls.encoding
        ) as file:
            xml = file.read()
            # Parse file with credentials.
            username: str = xml.split('<S N="UserName">')[1].split('</S>')[0]
            password: str = xml.split('<SS N="Password">')[1].split('</SS>')[0]
            # Return the binary string that is represented by any hexadecimal string.
            password_: bytes = binascii.unhexlify(password)
            return Credential(
                name=cred_name, username=username, password=password_
            )

    @classmethod
    def write(
        cls,
        cred_name: str,
        prompt_message: str = '',
        username: str = '',
    ) -> None:
        """Simple solution to call Windows prompt for credentials through PowerShell
        command Get-Credential. Result of command above will be exported in xml
        using Windows Data Protection API (Export-Clixml PowerShell command).

        The default `secrets` storage is the corresponding [folder](src/clixmlcreds/secrets)
        inside the package. All credentials are hashed and stored in this folder as a
        `<cred_name>.xml` file. You can change this behavior using:
        ```python
        from pathlib import Path
        from clixmlcreds import CredentialManager


        CredentialManager.path = Path('your_own_secrets_storage_folder')
        ```
        """
        if (
            not cls.path.exists()
        ):  # make sure that CredentialManager folder exists
            cls.path.mkdir(mode=stat.S_IRWXU, parents=False, exist_ok=True)
        process = CredentialToClixml(
            source=cls.cred_to_xml_script_path,
            export_path=cls.get_xml_path(cred_name=cred_name),
            prompt_message=prompt_message,
            username=username,
        ).call()
        if process.stderr:
            raise InvalidCredentialError(process.stderr)
