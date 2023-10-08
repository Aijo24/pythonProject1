from Connection import *
from BankAccount import *
import sqlite3
import sys


while True:
    user = input("Entrez votre nom : ")
    codePin = input("Entrez votre codePin : ")

    MAX_TRIALS = 3
    trials = MAX_TRIALS

    while trials > 0:
        compte = BankAccount()
        tryConnect = Connection(user, codePin)
        autre_action = ''

        if tryConnect.Connect():
            while autre_action != 'q':
                while True:
                    try:
                        choix = int(input("Voulez-vous retirer (1) ou afficher vos dernières transactions (2) ? : "))
                        if choix == 1:
                            compte.Retrait(user, codePin)
                            break
                        elif choix == 2:
                            compte.History(user)
                            break
                        else:
                            print("Veuillez choisir 1 pour retirer ou 2 pour afficher l'historique.")
                    except ValueError:
                        print("Veuillez entrer 1 ou 2.")

                autre_action = input("Voulez-vous effectuer une autre action ou quitter ? a/q : ")

                while autre_action.lower() != 'a' and autre_action.lower() != 'q':
                    print("Entrer (a) ou (q)")
                    autre_action = input("Voulez-vous effectuer une autre action ou quitter ? a/q : ")

                if autre_action.lower() == 'a':
                    continue
                elif autre_action.lower() == 'q':
                    print("Merci pour votre confiance, à bientôt chez XEFI Bank !")
                    sys.exit()
        else:
            trials -= 1
            print("Nom ou code PIN incorrect, il vous reste " + str(trials) + " essais.")
            user = input("Entrez votre nom : ")
            codePin = input("Entrez votre codePin : ")
