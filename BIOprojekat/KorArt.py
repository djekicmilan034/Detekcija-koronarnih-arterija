import cv2
import numpy as np
from matplotlib import pyplot as plt
import glob
import os
import png
import pydicom


source_folder = 'SE000004\SE000004' #Folder sa fotografijama DICOM formata koje je potrebno pretvoriti u PNG.
output_folder = 'BIO\BIOpng' #Folder u kom se cuvaju pretvorene DICOM fotografije u PNG formatu.

def dicom2png(source_folder, output_folder):
    list_of_files = os.listdir(source_folder)
    for file in list_of_files:
        try:
            ds = pydicom.dcmread(os.path.join(source_folder, file)) #Citanje dcm formata fotografija.
            shape = ds.pixel_array.shape

            #Pretvaranje u float da bismo izbegli prelivanja i gubitke.
            image_2d = ds.pixel_array.astype(float)

            #Skaliranje.
            image_2d_scaled = (np.maximum(image_2d, 0) / image_2d.max()) * 255.0

            #Pretvaranje u uint
            image_2d_scaled = np.uint8(image_2d_scaled)

            #Cuva PNG fotografije sa istim imenom kao i sto su zadate u DICOM formatu.
            with open(os.path.join(output_folder, file) + '.png', 'wb') as png_file:
                w = png.Writer(shape[1], shape[0], greyscale=True)
                w.write(png_file, image_2d_scaled)
        except:
            print('Could not convert: ', file)


dicom2png(source_folder, output_folder) #Funkcija koja vrsi pretvaranje DICOM fotografija u PNG fotografije.



niz = [] #Niz u koji smesta ucitane fotografije iz foldera u kom se nalaze png fotografije.
for filename in glob.glob('BIO/BIOpng/*.png'):
    niz.append(filename)


#For petlja koja iz foldera BIOpng uzima svaku sliku, vrsi oznacavanje koronarne i smesta u drugi folder.
for i in range(len(niz) - 1, 0, -1):

    img_rgb = cv2.imread('BIO/BIOpng/CT000' + str(i - 1) + '.png')  #Ucitavnje fotografije iz niza.
    img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY) #Konvertuje fotografiju da bude siva
    template = cv2.imread('BIO/primer.png', 0) #Uzorak koronarne arterije koju koristi u pretrazi.

    height, width = template.shape[::] #Cuvanje duzine i sirine unutar promeljivih height i width

    res = cv2.matchTemplate(img_gray, template, cv2.TM_SQDIFF) #Podudaranje sablona, koristimo modifikator TM_SQDIFF jer daje najbolje rezultate.
    plt.imshow(res, cmap='gray') #Mapa verovatnoce.

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res) #Da bismo pronasli sitne tacke na mapi verovatnoce

    top_left = min_loc #Gornji levi ugao kao referentni okvir i minimalna lokacija, gde zapravo pocinje podudaranje i detekcija.
    bottom_right = (top_left[0] + width, top_left[1] + height)

    cv2.rectangle(img_rgb, top_left, bottom_right, (0, 0, 255), 2) #Oznacavanje arterije crvenim okvirom.

    cv2.imshow("Zadata fotografija", img_gray)
    cv2.imshow("Obradjena fotografija", img_rgb) #Kao izlaz iz programa prikazuju se dve fotografije, zadata i obradjenja(detektovana k.a.).
    cv2.imwrite("BIO/Detektovane/ "+"CT000"+str(i-1)+".png",img_rgb) #Cuvanje u posebnom folderu fotografije sa detektovanom koronoarnom arterijom.

    cv2.waitKey() #Funkcija koja na svaki klik bilo kog tastera menja fotografije iz foldera tako da mozemo da vidimo sve primerke iz foldera zadatih i obradjenih.
cv2.destroyAllWindows()