import sqlite3
from datetime import datetime, timedelta
import requests

class BankAccount:
    def __init__(self, db_filename='bank_database.db'):
        self.conn = sqlite3.connect(db_filename)
        self.c = self.conn.cursor()
        self.user_id = None
        self.solde = 0
        self.retrait_id = None

    def close(self):
        self.conn.close()

    def get_user_info(self, user, codePin):
        query = "SELECT id, sold, dernier_retrait FROM user_model WHERE name = ? AND pinCode = ?"
        self.c.execute(query, (user, codePin))
        row = self.c.fetchone()
        if row:
            self.user_id = row[0]
            self.solde = row[1]
            date_de_retrait_str = row[2]
            if date_de_retrait_str:
                self.dateDeRetrait = datetime.strptime(date_de_retrait_str, "%Y-%m-%d %H:%M:%S.%f")
            else:
                self.dateDeRetrait = datetime.now()
            print("Votre solde est de : ", self.solde)
        else:
            print("Aucun utilisateur correspondant trouvé dans la base de données.")

    def Retrait(self, user, codePin):
        self.get_user_info(user, codePin)

        montant = 0

        try:
            montant = int(input("Combien voulez-vous retirer ? : "))
        except ValueError:
            print("Veuillez entrer un montant valide.")

        while montant < 20 or montant % 10 != 0:
            try:
                montant = int(input("Entrez un multiple de 10 entier, le retrait minimum est de 20€ : "))
            except ValueError:
                print("Veuillez entrer un montant valide.")

        un_jour_avant = datetime.now() - timedelta(hours=24)
        self.c.execute("SELECT SUM(montant) FROM retrait_model WHERE name = ? AND date >= ?", (user, un_jour_avant))
        total_retraits_24h = self.c.fetchone()[0] or 0

        self.c.execute("SELECT COUNT(*) FROM retrait_model WHERE name = ? AND date >= ?", (user, un_jour_avant))
        nombre_retraits_jour = self.c.fetchone()[0] or 0

        if total_retraits_24h + montant > 20000:
            print("La somme des retraits des dernières 24 heures dépasse 200.00 €. Retrait impossible.")
        elif nombre_retraits_jour >= 50:
            print("Vous avez atteint la limite de 5 retraits par jour.")
        elif montant <= self.solde:
            self.c.execute("SELECT COUNT(*) FROM retrait_model WHERE name = ? AND date >= ?", (user, un_jour_avant))
            nombre_retraits_jour = self.c.fetchone()[0] or 0

            self.solde -= montant
            self.c.execute("UPDATE user_model SET dernier_retrait = ?, sold = ? WHERE name = ? AND pinCode = ?",
                           (self.dateDeRetrait.strftime("%Y-%m-%d %H:%M:%S.%f"), self.solde, user, codePin))
            self.conn.commit()
            #self.c.execute("INSERT INTO retrait_model (name, montant, date) VALUES (?, ?, ?)",
            #               (user, montant, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")))

            try:
                query = "SELECT id FROM retrait_model WHERE name = ? ORDER BY id DESC LIMIT 1"
                self.c.execute(query, (user,))
                row = self.c.fetchone()
                if row:
                    last_withdrawal_id = row[0]
                else:
                    print("Aucun retrait trouvé pour l'utilisateur", user)
                    return None
            except Exception as e:
                print("Une erreur s'est produite lors de la récupération de l'ID du dernier retrait:", str(e))
                return None

            if montant >= 50:
                petit_ou_gros = ""

                while petit_ou_gros != "p" and petit_ou_gros != "g":
                    try:
                        petit_ou_gros = input(
                            "Voulez-vous retirer des petits ou des gros billets ? Entrez 'p' ou 'g' : ").lower()
                        if petit_ou_gros == "p":
                            nb_billet_20 = montant // 20
                            reste = montant - nb_billet_20 * 20
                            nb_billet_10 = reste // 10

                            message = "Vous avez retiré :"
                            if nb_billet_20 > 0:
                                message += " " + str(nb_billet_20) + " billet(s) de 20 €"
                            if nb_billet_10 >= 1:
                                message += " " + str(int(nb_billet_10)) + " billet(s) de 10 €"
                            if nb_billet_10 > int(nb_billet_10):
                                message += " et " + str(int((nb_billet_10 - int(nb_billet_10)) * 10)) + " pièce(s) de 10 €"
                            print(message)

                        if petit_ou_gros == "g":
                            nb_billet_50 = 0
                            nb_billet_100 = montant // 100
                            reste = montant - nb_billet_100 * 100

                            while reste >= 50:
                                nb_billet_50 += 1
                                reste -= 50

                            nb_billet_20 = reste // 20
                            reste = reste % 20
                            nb_billet_10 = reste // 10

                            message = "Vous avez retiré :"
                            if nb_billet_100 > 0:
                                message += " " + str(nb_billet_100) + " billet(s) de 100 €"
                            if nb_billet_50 > 0:
                                message += " " + str(nb_billet_50) + " billet(s) de 50 €"
                            if nb_billet_20 > 0:
                                message += " " + str(nb_billet_20) + " billet(s) de 20 €"
                            if nb_billet_10 >= 1:
                                message += " " + str(int(nb_billet_10)) + " billet(s) de 10 €"
                            if nb_billet_10 > int(nb_billet_10):
                                message += " et " + str(int((nb_billet_10 - int(nb_billet_10)) * 10)) + " pièce(s) de 10 €"
                            print(message)
                        else:
                            print("Veuillez répondre par 'p' ou 'g'.")
                    except:
                        print("Veuillez entrer un caractère valide.")
                        print("Veuillez répondre par 'p' ou 'g'.")

            print(str(montant) + " € retirés")
            print("Il vous reste :", str(self.solde) + " €")

            def format_datetime(dt):
                return dt.strftime('%Y-%m-%dT%H:%M:%S')

            BASE_URL = "http://127.0.0.1:5000/"

            data = {
                "name": user,
                "pinCode": codePin,
                "dernier_retrait": format_datetime(datetime.now())
            }

            requests.patch(BASE_URL + "user/" + str(self.user_id), json=data)
            #print("MAJ de l'utilisateur :")
            #print(response.json())

            requests.get(BASE_URL + "user/" + str(self.user_id))
            #print("\nRécupération de l'utilisateur :")
            #print(response.json())

            data = {
                "name": user,
                "montant": montant,
                "date": format_datetime(datetime.now())
            }

            requests.put(BASE_URL + "retrait/" + str(last_withdrawal_id + 1), json=data)
            #print("\nAjout d'un retrait :")
            #print(response.json())

            requests.get(BASE_URL + "retrait/" + str(last_withdrawal_id + 1))
        else:
            print("Solde insuffisant sur le compte ou montant quotidien maximum atteint.")

    def History(self, user):
        try:
            self.c.execute("SELECT montant, date FROM retrait_model WHERE name = ? ORDER BY date DESC LIMIT 5", (user,))
            resultats = self.c.fetchall()

            if len(resultats) > 0:
                print("Les 5 derniers retraits de l'utilisateur", user, "sont les suivants : ")
                for row in resultats:
                    montant_retrait = row[0]
                    date_retrait = row[1]

                    date_obj = datetime.strptime(date_retrait, "%Y-%m-%d %H:%M:%S.%f")

                    date_formattee = date_obj.strftime("%d/%m/%Y %H:%M")

                    print("Date du retrait : " + date_formattee + " - Montant retiré : " + str(montant_retrait) + " €")
            else:
                print("Aucun retrait trouvé pour l'utilisateur", user)
        except Exception as e:
            print("Une erreur s'est produite lors de la récupération de l'historique des retraits:", str(e))
