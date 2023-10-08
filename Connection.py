import sqlite3

class Connection:
    def __init__(self, name, codePin):
        self.name = name
        self.codePin = codePin
        self.solde = 0

    def Connect(self):
        conn = sqlite3.connect('bank.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE name = ? AND pinCode = ?", (self.name, self.codePin))
        results = c.fetchall()
        if results:
            c.execute("SELECT solde FROM users WHERE name = ? AND pinCode = ?", (self.name, self.codePin))
            self.solde = c.fetchone()[0]
            print("Bienvenue sur votre compte XEFI Bank !")
            print("Solde actuel :", self.solde)
            return True
        else:
            return False
