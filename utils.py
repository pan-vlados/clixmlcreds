# -*- coding: utf-8 -*-
import subprocess

from dataclasses import dataclass, field


@dataclass
class PShellFunction:
    source: str
    name: str = field(init=False)
    input_: str = field(init=False)

    def call(self) -> subprocess.CompletedProcess:
        """
        Запуск процесса вызова функции в PowerShell скрипте через консоль.
        """
        return subprocess.run(
                    [
                        'powershell.exe',
                        f". \"{self.source}\";",
                        f"&{self.name} {self.input_}"
                        ],
                    capture_output=True,
                    text=True
                )

@dataclass
class CredentialToClixml(PShellFunction):
    export_path: str
    prompt_message: str
    username: str

    def __post_init__(self) -> None:
        self.name = 'Do-Main'
        self.input_ = f"'{self.export_path}' '{self.prompt_message}' '{self.username}'"
