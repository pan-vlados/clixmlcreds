import unittest
from pathlib import Path

from src.clixmlcreds import Credential, CredentialManager


def write_credential_for_test() -> None:
    CredentialManager.write(
        cred_name=TestCredentials.cred_name,
        username=TestCredentials.username,
        prompt_message=TestCredentials.prompt_message,
    )


class TestCredentials(unittest.TestCase):
    cred_name: str = 'test'
    username: str = 'test_user'
    prompt_message: str = 'Test prompt message:'

    @classmethod
    def setUpClass(cls):
        CredentialManager.path = Path(__file__).absolute().parent

    def setUp(self):
        if not Credential.exists(name=self.cred_name):
            write_credential_for_test()
        self.credential: Credential = CredentialManager.read(
            cred_name=self.cred_name
        )

    def test_write(self):
        write_credential_for_test()
        self.assertTrue(Credential.exists(name=self.cred_name))

    def test_read(self):
        credential: Credential = CredentialManager.read(
            cred_name=self.cred_name
        )
        self.assertEqual(credential.username, self.username)

    def test_get_password(self):
        password = self.credential.get_password()
        decrypted_password, _ = CredentialManager.decrypt(
            password=self.credential.password
        )
        self.assertEqual(password, decrypted_password)

    def test_encrypt_decrypt(self):
        password = self.credential.get_password()
        encrypted_password = CredentialManager.encrypt(password=password)
        decrypted_password, _ = CredentialManager.decrypt(
            password=encrypted_password
        )
        self.assertEqual(password, decrypted_password)

    @classmethod
    def tearDownClass(cls):
        Path(CredentialManager.get_xml_path(cred_name=cls.cred_name)).unlink()


if __name__ == '__main__':
    unittest.main(verbosity=2)
