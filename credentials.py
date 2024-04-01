# -*- coding: utf-8 -*-
from __future__ import annotations

import win32crypt
import binascii

from pathlib import Path
from typing import Optional, Union, Tuple, Any
from dataclasses import dataclass

from .utils import CredentialToClixml


class InvalidCredentialError(Exception):
    pass


class PasswordTypeError(Exception):
    pass


@dataclass
class Credential:
    name: str
    username: str
    password: Union[bytes, str]

    def get_password(self) -> str:
        """
        UNSECURE!
        Return decrypted string representation of password.
        """
        password = self.password
        if isinstance(password, bytes):
            password, _ = CredentialManager.decrypt(password=password)
        elif not isinstance(password, str):
            raise PasswordTypeError
        return password

    @staticmethod
    def exists(name: str) -> bool:
        """
        Check if Credential with scpecified name exists in CredentialManager path.
        """
        return Path(CredentialManager.get_xml_path(cred_name=name)).exists()


class CredentialManager:  # thanks to https://dev.to/samklingdev/use-windows-data-protection-api-with-python-for-handling-credentials-5d4j
    path: Path = Path(__file__).absolute().parent / "secrets"
    encoding: str = "utf-16-le"
    cred_to_xml_script_path: Path = (
        Path(__file__).absolute().parent / "Export-CredentialToClixml.ps1"
    )

    @classmethod
    def encrypt(
        cls,
        password: str,
        desc: Optional[str] = "",
        entropy: Optional[bytes] = None,
        flags: int = 0,
        ps: Optional[Any] = None,
    ) -> bytes:
        """
        Encrypt by Windows Data Protection API.
        """
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
        """
        UNSECURE!
        Decrypt Windows Data Protection API.
        """
        desc, password = win32crypt.CryptUnprotectData(
            password, entropy, None, ps, flags
        )
        password: str = password.decode(cls.encoding)
        return password, desc

    @classmethod
    def get_xml_path(cls, cred_name: str) -> str:
        return str(cls.path / f"{cred_name}.xml")

    @classmethod
    def read(cls, cred_name: str) -> Credential:
        """
        Read user's credential (Import-Clixml PowerShell command).
        Credentials still will be secured using Windows Data Protection API.
        """
        with open(
            cls.get_xml_path(cred_name=cred_name), "r", encoding=cls.encoding
        ) as file:
            xml = file.read()
            # Parse file with credentials.
            username: str = xml.split('<S N="UserName">')[1].split("</S>")[0]
            password: str = xml.split('<SS N="Password">')[1].split("</SS>")[0]
            # Return the binary string that is represented by any hexadecimal string.
            password: bytes = binascii.unhexlify(password)
            return Credential(name=cred_name, username=username, password=password)

    @classmethod
    def write(
        cls,
        cred_name: str,
        prompt_message: str = "",
        username: str = "",
    ) -> None:
        """
        Simple solution to call Windows prompt for credentials through PowerShell
        command Get-Credential. Result of command above will be exported in xml
        using Windows Data Protection API (Export-Clixml PowerShell command).
        """
        process = CredentialToClixml(
            source=str(cls.cred_to_xml_script_path),
            export_path=cls.get_xml_path(cred_name=cred_name),
            prompt_message=prompt_message,
            username=username,
        ).call()
        if process.stderr:
            raise InvalidCredentialError(process.stderr)
