import subprocess
from dataclasses import dataclass, field
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from pathlib import Path


@dataclass
class PShellFunction:
    source: 'Path'
    name: str = field(init=False)
    input_: str = field(init=False)

    def call(self) -> subprocess.CompletedProcess:
        """Start the process of calling a function in a PowerShell script via the console."""
        return subprocess.run(
            [
                'powershell.exe',
                f'. "{self.source!s}";',
                f'&{self.name} {self.input_}',
            ],
            capture_output=True,
            text=True,
            check=False,
        )


@dataclass
class CredentialToClixml(PShellFunction):
    export_path: 'Path'
    prompt_message: str
    username: str

    def __post_init__(self) -> None:
        self.name = 'Do-Main'
        self.input_ = (
            f"'{self.export_path!s}' '{self.prompt_message}' '{self.username}'"
        )
