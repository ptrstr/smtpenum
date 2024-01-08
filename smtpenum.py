import smtplib
import sys
from typing import List
from tqdm import tqdm

class SmtpEnum:
    def __init__(self, host, port):
        self._host = host
        self._port = port
        self._sess = None

    def open(self):
        if self._sess is None:
            self._sess = smtplib.SMTP(host=self._host, port=self._port)

    def close(self):
        if self._sess is not None:
            self._sess.close()
            self._sess = None

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

    def test_user(self, user: str, retries: int = 1) -> bool:
        ex = smtplib.SMTPServerDisconnected()
        
        while retries >= 0:
            try:
                status, msg = self._sess.vrfy(user)
                return status != 550
            except smtplib.SMTPServerDisconnected as tex:
                ex = tex
                retries -= 1
                self.close()
                self.open()

        raise ex

    def enum_users(self, users: List[str]) -> List[str]:
        return list(filter(self.test_user, users))

def main(argv) -> int:
    proc_name = argv[0] if len(argv) > 0 else __file__
    if len(argv) != 4:
        print(f'Usage: {proc_name} HOST PORT WORDLIST')
        return 1

    host = argv[1]
    port = int(argv[2])
    wordlist = argv[3]
    with open(wordlist, 'r') as f:
        wordlist = [x.strip() for x in f.readlines()]

    with SmtpEnum(host, port) as sess:
        users = sess.enum_users(tqdm(wordlist))
        
        for user in users:
            print(user)
    
    return 0

if __name__ == '__main__':
    exit(main(sys.argv))
