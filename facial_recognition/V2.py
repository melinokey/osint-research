import tkinter as tk
from tkinter import filedialog
import face_recognition
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import os
import sys
import requests
from io import BytesIO


def choisir_fichier():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    chemin_du_fichier = filedialog.askopenfilename(
        title=f"Sélectionnez une image de référence",
        filetypes=[("Images", "*.jpg *.jpeg *.png"), ("Tous les fichiers", "*.*")]
    )

    if chemin_du_fichier:
        nom_fichier = os.path.basename(chemin_du_fichier)
        print(f"Image de référence : {nom_fichier}")
        return chemin_du_fichier
    else:
        print("Aucun fichier sélectionné.")
        sys.exit()

#IMAGE DE RÉFÉRENCE
ref = choisir_fichier()

image_1 = face_recognition.load_image_file(ref)
encodage_image_1 = face_recognition.face_encodings(image_1)

if not encodage_image_1:
    print("Erreur : Aucun visage n'a été détecté sur l'image de référence.")
    sys.exit()

encodage_visage_im1 = [encodage_image_1[0]]

pers = input("Qui est-ce ? ").title()
nom_visage = [pers]

#IMAGE DE COMPARAISON (URL)
url = input("Entrez l'URL de l'image à comparer : ")

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status() 
    image_2 = face_recognition.load_image_file(BytesIO(response.content))
    print("Image URL chargée avec succès !")
    visage_image_2 = face_recognition.face_locations(image_2)
    encodage_visage_image_2 = face_recognition.face_encodings(image_2, visage_image_2)
    photo = Image.fromarray(image_2)
    draw = ImageDraw.Draw(photo) 

    compteur = 0
    trouve = False
    try:
        font = ImageFont.truetype("arial.ttf", 30) # 30 est la taille
    except:
        font = ImageFont.load_default() # Au cas où arial n'est pas trouvé    
    
    for (haut, droite, bas, gauche), encodage_visage in zip(visage_image_2, encodage_visage_image_2):
        corr = face_recognition.compare_faces(encodage_visage_im1, encodage_visage)
        distances_visage = face_recognition.face_distance(encodage_visage_im1, encodage_visage)
        best_ind = np.argmin(distances_visage)

        if corr[best_ind]: 
            compteur += 1
            nom = nom_visage[best_ind]
            marge = 30
            draw.ellipse([gauche - marge, haut - marge, droite + marge, bas + marge], outline="white", width=5)
            draw.text((gauche, haut - 35), nom, fill="white", font=font)
            trouve = True

    if not trouve:
        print(f"{pers} n'est pas sur cette photo ! ")
    else:
        print(f"{pers} apparaît {compteur} fois sur la photo !")
        photo.show()

except Exception as e:
    print(f"Erreur lors du chargement ou du traitement de l'URL : {e}")
