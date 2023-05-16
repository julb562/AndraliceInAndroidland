# Pelikenttä on tallennettu erilliseen tiedostoon tasot.txt
# Mikäli tasot.txt -tiedosto ei löytyisi, on sen sisältö
# tämän tiedoston lopussa

# Pelissä on tarkoitus matkata kohti kentän ylälaidan ovea hyppimällä tasolta toiselle
# pisteitä saa hiukan kiipeämisestä ja kolikoita keräämällä
# Haamuihin koskeminen vähentää pisteitä

# Pelin häviää, jos:
#   1. Pisteet menevät miinukselle haamujen kanssa törmäillessä
#   2. Pelaajahahmo robotti putoaa liian nopeasti/korkealta

# Pelissä pääsee tasolta seuraavalle saavuttamalla kentän ylälaidan oven
# Tason kasvaessa kolikoista saa lineaarisesti enemmän pisteitä, mutta haamut syövät
# pisteitä eksponentiaalisesti nopeammin

import pygame
import random

class Tausta_verkot:
    def __init__(self, naytto: pygame.display) -> None:
        self.naytto= naytto
        self.vari=(0,100,100)
        self.leveys=10
        self.korkeus=8
        self.ruutukoko=100
        self.taustakokokerroin=0.8

    def piirra(self, poikkeama_x: float, poikkeama_y: float):       
        if poikkeama_x> self.ruutukoko: poikkeama_x-=self.ruutukoko
        if poikkeama_x<-self.ruutukoko: poikkeama_x+=self.ruutukoko
        if poikkeama_y> self.ruutukoko: poikkeama_y-=self.ruutukoko
        if poikkeama_y<-self.ruutukoko: poikkeama_y+=self.ruutukoko
        vari_tummennus=0.7
        vari_vali=(self.vari[0]*vari_tummennus, self.vari[1]*vari_tummennus, self.vari[2]*vari_tummennus)
        vari_tausta=(vari_vali[0]*vari_tummennus, vari_vali[1]*vari_tummennus, vari_vali[2]*vari_tummennus)
        origo_x=self.naytto.get_width()/2
        origo_y=self.naytto.get_height()/2
        range_x=range(round(-self.leveys/2 ), round(self.leveys/2))
        range_y=range(round(-self.korkeus/2), round(self.korkeus/2))
        scale = self.taustakokokerroin
        for y in range_y:
            for x in range_x:
                # 3D-verkosto piirretään kuutio kerrallaan kunkin tausta mukaan lukien.
                # Luuppeja tarvitaan tällöin 1 kolmen sijasta, mutta hintana on,
                # että osan kuutioista tausta piirtyy seuraavan päälimmäisen kerroksen viivojen yli
                # aiheuttaen artefakteja, mutta niiden kanssa voi elää.
                # Vaihtoehto olisi piirtää kolmessa luupissa ensin kaikkien kuutioiden tausta,
                # seuraavana Z-palkit ja viimeisenä lähimmät sivut
                tausta_x_vasen=(x*    self.ruutukoko+poikkeama_x) * scale +origo_x
                tausta_x_oikea=((x+1)*self.ruutukoko+poikkeama_x) * scale +origo_x
                tausta_y_yla=  (y    *self.ruutukoko+poikkeama_y) * scale +origo_y
                tausta_y_ala=  ((y+1)*self.ruutukoko+poikkeama_y) * scale +origo_y
                coord_tausta_1 = (tausta_x_vasen, tausta_y_yla)
                coord_tausta_2 = (tausta_x_oikea, tausta_y_yla)
                coord_tausta_3 = (tausta_x_vasen, tausta_y_ala)
                pygame.draw.line(self.naytto, vari_tausta, coord_tausta_1, coord_tausta_2, 4)
                pygame.draw.line(self.naytto, vari_tausta, coord_tausta_1, coord_tausta_3, 4)
                etu_x_vasen=(x*    self.ruutukoko+poikkeama_x )+origo_x
                etu_x_oikea=((x+1)*self.ruutukoko+poikkeama_x )+origo_x
                etu_y_yla=  (y    *self.ruutukoko+poikkeama_y )+origo_y
                etu_y_ala=  ((y+1)*self.ruutukoko+poikkeama_y )+origo_y
                coord_etu_1 = (etu_x_vasen, etu_y_yla)
                coord_etu_2 = (etu_x_oikea, etu_y_yla)
                coord_etu_3 = (etu_x_vasen, etu_y_ala)
                pygame.draw.line(self.naytto, vari_vali, coord_tausta_1, coord_etu_1, 4)
                pygame.draw.line(self.naytto, vari_vali, coord_tausta_2, coord_etu_2, 4)
                pygame.draw.line(self.naytto, vari_vali, coord_tausta_3, coord_etu_3, 4)
                pygame.draw.line(self.naytto, self.vari, coord_etu_1, coord_etu_2, 4)
                pygame.draw.line(self.naytto, self.vari, coord_etu_1, coord_etu_3, 4)
                
class Esine:
    def __init__(self, naytto: pygame.display, kuva: pygame.image, x: float=0.0, y: float=0.0) -> None:
        # Kaikkien esineiden sijainti (x & y) tarkoittaa pistettä, joka on esineen kuvan alareunassa ja 
        # sivusuunnassa keskellä. Tämä helpottaa esineiden ja lattiatasojen kohtaamisen seuraamista
        self.kuva=kuva
        self.x=x
        self.y=y
        self.korkeus=kuva.get_height()
        self.leveys=kuva.get_width()
        self.naytto=naytto
        self.nayttoleveys=naytto.get_width()/2+self.leveys
        self.nayttokorkeus=naytto.get_height()/2+self.korkeus

    def piirra(self, globaali_x: float, globaali_y: float):
        piirto_x=self.x-globaali_x+self.nayttoleveys-self.leveys*1.5
        piirto_y=self.y-globaali_y+self.nayttokorkeus-self.korkeus*2
        if piirto_x>-self.leveys and piirto_x<self.naytto.get_width() and piirto_y>0-self.korkeus and piirto_y<self.naytto.get_height():
            #esine on koordinaatistossa riittävän lähellä näkyvää näyttöä, joten piirretään se
            self.naytto.blit(self.kuva, (round(piirto_x), round(piirto_y)))

class Hahmo(Esine):
    def __init__(self, naytto: pygame.display, kuva: pygame.image, x: float = 0, y: float = 0) -> None:
        super().__init__(naytto, kuva, x, y)
        self.nopeus_x=0.0
        self.nopeus_y=0.0
        self.putoamiskiihtyvyys=0.4

    def tormaa_seinaan(self, vasen_seina: int, oikea_seina: int)->float:
        # Tarkastaa, törmääkö hahmo seinään, jos jatkaa samalla
        # nopeudella x-akselilla.
        # Palauttaa 0, jos törmäystä ei ole tai 0:sta poikkeavana arvona
        # etäisyyden seinään
        if (self.x+self.nopeus_x-self.leveys/2<vasen_seina): return vasen_seina-self.x+self.leveys/2+1
        if (self.x+self.nopeus_x+self.leveys/2>oikea_seina): return oikea_seina-self.x-self.leveys/2-1
        return 0
    
    def tormaa_tasoon(self, tasot: list)->tuple:
        # taso = tuple ( X-coord (keskikohta) , Y-coord , leveys )
        # Palautusarvot tuplessa 0: taso alla, 1: 0, jos kohtaamista ei tapahdu tai absoluuttinen y-arvo,
        # johon hahmo tulee asettaa, jotta se jää tason päälle
        palautus_taso_alla=False
        palautus_tasoon_matkaa=0

        for taso in tasot:
            if self.x>=taso[0]-taso[2]/2 and self.x<taso[0]+taso[2]/2:
                # Tämä taso on sivusuunnassa hahmon kanssa samassa linjassa siten, että hahmo
                # on vähintään puoliksi sen kanssa kohdikkain
                if taso[1]>=self.y and self.y+self.nopeus_y>taso[1]:
                    # Taso hahmon alapuolella ja hahmo tuntuisi ohittavan
                    # tason, jos jatkaisi liikettä nykyisellä nopeudella alas                    
                    palautus_taso_alla=True
                    palautus_tasoon_matkaa= taso[1]-1
                if abs(taso[1]-self.y)<=2 and abs(self.y-taso[1])<2: 
                    # Taso on hahmon kanssa samalla tasolla alle 2:n pikselin tarkkuudella
                    # Joten jätetään hahmo tasolle.
                    # 2 pikseliä todettu käytännössä tarvittavaksi toleranssiksi
                    palautus_taso_alla=True
                    palautus_tasoon_matkaa= taso[1]-1
        return (palautus_taso_alla, palautus_tasoon_matkaa)

    def liiku(self, tasot: list=[], reuna_vasen: int=0, reuna_oikea: int=640):
        self.nopeus_y+=self.putoamiskiihtyvyys  
        # Kaikki hahmot pyrkivät putoamaan kiihtyvällä nopeudella.
        # Nopeus nollataan myöhemmin, jos alla on taso

        seinatormays=self.tormaa_seinaan(reuna_vasen, reuna_oikea)
        if seinatormays!=0: self.x+=seinatormays
        else: self.x+=self.nopeus_x

        taso_alla, matkaa_tasoon =self.tormaa_tasoon(tasot)
        if abs(matkaa_tasoon)>0.5 and taso_alla and self.nopeus_y>=0:
            self.y=matkaa_tasoon
            self.nopeus_y=0
        else: self.y+=self.nopeus_y
        
class Pelaaja(Hahmo):
    pass

class Tiedostopalvelu:
    def hae_tasot(self, tiedosto_nimi: str)->list:
        # Hae tiedostosta pelitason kartta
        palautuslista=[]
        with open(tiedosto_nimi) as tiedosto:
            for rivi in tiedosto:
                lista=rivi[0:-1].split(",")
                palautuslista.append( ( int(lista[0]), int(lista[1]), int(lista[2]) ))
        return palautuslista


class Peli:
    def __init__(self, naytto: pygame.display) -> None:
        self.naytto=naytto
        self.tausta=Tausta_verkot(naytto)
        self.pelin_vasen_laita=-400
        self.pelin_oikea_laita=400
        self.kuvat=[pygame.image.load("robo.png"), pygame.image.load("kolikko.png"), pygame.image.load("hirvio.png"), pygame.image.load("ovi.png")]
        self.tiedostopalvelu=Tiedostopalvelu()
        self.pause=False
        self.peliseissyy="   Tervetuloa pelaamaan!"
        self.kuolemaputousnopeus=17
        self.nollaa_peli()

    def arvo_hahmoja(self):
        if random.randrange(0, 1000)>990:
            self.haamut.append(Hahmo(naytto, self.kuvat[2], random.randrange(self.pelin_vasen_laita+60, self.pelin_oikea_laita-60), self.pelaaja.y-self.naytto.get_width()))
            self.haamut[-1].nopeus_x=(random.randrange(0,60)-30)/10
        if random.randrange(0, 1000)>995:
            self.kolikot.append(Hahmo(naytto, self.kuvat[1], random.randrange(self.pelin_vasen_laita+60, self.pelin_oikea_laita-60), self.pelaaja.y-self.naytto.get_width()))
            
    def tarkasta_esinetormays(self, asia1: Esine, asia2: Esine)->bool:
        raja_x=asia1.leveys/2+asia2.leveys/2
        if abs(asia1.x-asia2.x)<raja_x-10:
            # Esineiden vaakasijainti on sisäkkäin
            raja_y=asia1.korkeus/2+asia2.korkeus/2-10
            if abs(asia1.y+asia1.korkeus/2-asia2.y-asia2.korkeus/2)<raja_y:
                # Esineiden pystysijaintikin on näemmä sisäkkäin
                return True
        return False

    def tarkasta_esinetormaykset(self):
        for haamu in self.haamut:
            #print(self.tarkasta_esinetormays(self.pelaaja, haamu))
            if self.tarkasta_esinetormays(self.pelaaja, haamu): self.pisteet-=0.1*self.taso*self.taso
        for indeksi in range(0,len(self.kolikot)):
            #print(self.tarkasta_esinetormays(self.pelaaja, haamu))
            if self.tarkasta_esinetormays(self.pelaaja, self.kolikot[indeksi]): 
                self.pisteet+=10*self.taso
                self.kolikot.pop(indeksi)
                break
        if self.tarkasta_esinetormays(self.pelaaja, self.ovi):
            self.taso+=1
            self.nollaa_pelikentta()
        

    def mittaa_taustan_liikutus(self)->tuple:
        # Laskee pelaajan sijainnin poikkeamaa ruudun keskiosalta
        # ja palauttaa nopeusvektorin, jolla taustan keskustaa on hyvä skrollata
        # pelaajan sijaintia kohden
        siirto_y=0
        if abs(self.pelaaja.y-self.globaali_y-100)>10: siirto_y=(self.pelaaja.y-self.globaali_y-100)/50
        siirto_x=0
        if abs(self.pelaaja.x+self.globaali_x)>10: 
            if self.pelaaja.x<self.globaali_x: siirto_x=(self.pelaaja.x-self.globaali_x)/30
            if self.pelaaja.x>self.globaali_x: siirto_x=(self.pelaaja.x-self.globaali_x)/30
        return(siirto_x,  siirto_y)
    
    def piirra_tiedot(self):
        self.naytto.fill((0, 0, 0), pygame.Rect(0,0,200,80))
        fontti = pygame.font.SysFont("Arial", 24)
        teksti = fontti.render(f"Pisteet: {round(self.pisteet)}", True, (0, 200, 200))
        self.naytto.blit(teksti, (10, 14))
        teksti = fontti.render(f"Taso:    {self.taso}", True, (0, 200, 200))
        self.naytto.blit(teksti, (13, 44))
    
    def piirra_tasot(self):
        for taso in self.tasot:
            if abs(self.globaali_y-taso[1])<self.naytto.get_height()/2+30:
                # Tämän tason korkeus on näkyvällä alueella
                #        piirto_x=self.x+globaali_x+self.nayttoleveys-self.leveys*1.5
                #        piirto_y=self.y-globaali_y+self.nayttokorkeus-self.korkeus*2

                x1=taso[0]-taso[2]/2 -self.globaali_x+self.naytto.get_width()/2
                x2=taso[0]+taso[2]/2 -self.globaali_x+self.naytto.get_width()/2
                y1=taso[1]           -self.globaali_y+self.naytto.get_height()/2
                y2=taso[1]+2         -self.globaali_y+self.naytto.get_height()/2

                pygame.draw.line( self.naytto, (0,180,180), (x1, y2), (x2, y2), 5)
                pygame.draw.line( self.naytto, (0,255,255), (x1, y1), (x2, y1), 1)

    def piirra_seinat(self):
        if self.pelin_vasen_laita-self.globaali_x+self.naytto.get_width()/2>-12:
            piirto_x = self.pelin_vasen_laita-self.globaali_x+self.naytto.get_width()/2
            pygame.draw.line( self.naytto, (0,180,180), (piirto_x,   0), (piirto_x, self.naytto.get_height()) , 5)
            pygame.draw.line( self.naytto, (0,255,255), (piirto_x+2, 0), (piirto_x, self.naytto.get_height()) , 1)
        if self.pelin_oikea_laita-self.globaali_x<self.naytto.get_width()/2+12:
            piirto_x = self.pelin_oikea_laita-self.globaali_x+self.naytto.get_width()/2
            pygame.draw.line( self.naytto, (0,180,180), (piirto_x,   0), (piirto_x, self.naytto.get_height()) , 5)
            pygame.draw.line( self.naytto, (0,255,255), (piirto_x-2, 0), (piirto_x, self.naytto.get_height()) , 1)

    def nollaa_pelikentta(self):
        # Kutsutaan, kun pelikenttä pitää nollata esimerkiksi tason vaihtuessa
        self.hengissa=True    
        self.globaali_x=0
        self.globaali_y=0      
        self.siirtonopeus_x=0
        self.siirtonopeus_y=0
        self.viimeisin_korkeus=0
        self.pelaaja=Pelaaja(naytto, self.kuvat[0], 0, 200)
        self.haamut=[]
        self.kolikot=[]
        self.ovi=Esine(self.naytto, self.kuvat[3], 0, -1100)
        self.tasot=self.tiedostopalvelu.hae_tasot("tasot.txt")

    def nollaa_peli(self):
        # Kutsutaan, kun aloitetaan kokonaan uusi peli
        self.pisteet=0.0
        self.taso=1
        self.nollaa_pelikentta()

    def pelaa(self):        
        (self.siirtonopeus_x, self.siirtonopeus_y) = self.mittaa_taustan_liikutus()
        self.globaali_x+=self.siirtonopeus_x
        self.globaali_y+=self.siirtonopeus_y        
        if self.pelaaja.nopeus_y>self.kuolemaputousnopeus: 
            # Nyt pudotaan liian lujaa, joten game ooveri
            self.hengissa=False
            self.peliseissyy="     Tuli vähän syöksyttyä!"
        if self.pelaaja.y<self.viimeisin_korkeus:
            self.pisteet+=-(self.pelaaja.y-self.viimeisin_korkeus)/10
            self.viimeisin_korkeus=self.pelaaja.y
            #print(f"Pisteet: {round(self.pisteet)}")
        self.arvo_hahmoja()
        #print(f"G: {round(self.globaali_y)}  P: {round(self.pelaaja.y)}")
        #print(f"G: {round(self.globaali_x)}  P: {round(self.pelaaja.x)}")
        self.pelaaja.liiku(self.tasot, self.pelin_vasen_laita, self.pelin_oikea_laita)
        for haamuindeksi in range(0, len(self.haamut)):
            self.haamut[haamuindeksi].liiku(self.tasot, self.pelin_vasen_laita, self.pelin_oikea_laita)
            # poistetaan haamut, jotka yli näytön korkeuden verran pelaajan alapuolella
            if self.haamut[haamuindeksi].y>self.pelaaja.y+self.naytto.get_width():
                self.haamut.pop(haamuindeksi)
                break 
                # haamun popauttaminen listasta aiheuttaisi
                # indkeksiylityksen, joten katkaistaan silmukka.
                # Break aiheuttaa, ettei listan muiden haamujen
                # liikkumista toteuteta, mutta tämä ei käytännössä
                # näy pelissä
        for kolikkoindeksi in range(0, len(self.kolikot)):
            self.kolikot[kolikkoindeksi].liiku(self.tasot, self.pelin_vasen_laita, self.pelin_oikea_laita)
            # poistetaan kolikot, jotka yli näytön korkeuden verran pelaajan alapuolella
            if self.kolikot[kolikkoindeksi].y>self.pelaaja.y+self.naytto.get_width():
                self.kolikot.pop(kolikkoindeksi)
                break 
                # Samat huomiot kuin edellisessä haamujen kanssa
        self.tarkasta_esinetormaykset()
        if self.pisteet<0:
            self.hengissa=False
            self.peliseissyy="   Haamut söivät pisteesi"
        self.tausta.piirra(-self.globaali_x % self.tausta.ruutukoko, -self.globaali_y % self.tausta.ruutukoko)
        self.piirra_tasot()
        self.piirra_seinat()
        self.ovi.piirra(self.globaali_x, self.globaali_y)
        for haamu in self.haamut:
            haamu.piirra(self.globaali_x, self.globaali_y)
        for kolikko in self.kolikot:
            kolikko.piirra(self.globaali_x, self.globaali_y)
        self.pelaaja.piirra(self.globaali_x, self.globaali_y)
        self.piirra_tiedot()

    def pelivalikko(self):
        self.naytto.fill((0, 0, 0), pygame.Rect(50,50,nayttoleveys-100,nayttokorkeus-100))
        fontti = pygame.font.SysFont("Arial", 44)
        teksti = fontti.render(f"Andraliisa Matrixmaassa", True, (0, 200, 200))
        self.naytto.blit(teksti, (80, 140))
        fontti = pygame.font.SysFont("Arial", 24)
        teksti = fontti.render(f"{self.peliseissyy}", True, (0, 200, 200))
        self.naytto.blit(teksti, (160, 210))
        teksti = fontti.render(f"Pisteesi: {round(self.pisteet)}", True, (0, 200, 200))
        if peli.pisteet>0:
            self.naytto.blit(teksti, (230, 290))
        teksti = fontti.render(f"Paina välilyöntiä pelataksesi", True, (0, 200, 200))
        self.naytto.blit(teksti, (160, 400))


pygame.init()
nayttoleveys=640
nayttokorkeus=480
naytto = pygame.display.set_mode((nayttoleveys, nayttokorkeus))
pygame.display.set_caption("Andraliisa Matrixmaassa")
tausta_punainen=0
tausta_vihrea=40
tausta_sininen=40

kello = pygame.time.Clock()
viimeksi_painettu=""
peli=Peli(naytto)
nappaimisto_viimeisin_painike=pygame.K_0
nappaimisto_hyppy_pohjassa=False
peli.hengissa=False


while True:
    if not peli.hengissa: peli.pelivalikko()
    if not peli.pause and peli.hengissa:
        naytto.fill((tausta_punainen, tausta_vihrea, tausta_sininen))
        peli.pelaa()
    pygame.display.flip()
    kello.tick(60)
    #print(f"kolikot: {len(peli.kolikot)} haamut: {len(peli.haamut)}")
    

    for tapahtuma in pygame.event.get():
        if tapahtuma.type == pygame.KEYDOWN:
            nappaimisto_viimeisin_painike=tapahtuma.key
            if tapahtuma.key == pygame.K_ESCAPE: exit()
            if tapahtuma.key == pygame.K_UP or nappaimisto_hyppy_pohjassa:
                nappaimisto_hyppy_pohjassa=True
                ontaso, tasoon =peli.pelaaja.tormaa_tasoon(peli.tasot)
                if ontaso:
                    peli.pelaaja.nopeus_y=-10
            if tapahtuma.key == pygame.K_LEFT : peli.pelaaja.nopeus_x=-2
            if tapahtuma.key == pygame.K_RIGHT: peli.pelaaja.nopeus_x=2
            if tapahtuma.key == pygame.K_p: peli.pause=not peli.pause
            if tapahtuma.key == pygame.K_a: peli.globaali_x-=10
            if tapahtuma.key == pygame.K_s: peli.globaali_x+=10
            if tapahtuma.key == pygame.K_r: peli.nollaa_peli()
            if tapahtuma.key == pygame.K_SPACE and not peli.hengissa: peli.nollaa_peli()
        if tapahtuma.type == pygame.KEYUP:
            if tapahtuma.key == pygame.K_UP: nappaimisto_hyppy_pohjassa=False
            if tapahtuma.key == pygame.K_LEFT  and peli.pelaaja.nopeus_x<0 : peli.pelaaja.nopeus_x=0
            if tapahtuma.key == pygame.K_RIGHT and peli.pelaaja.nopeus_x>0 : peli.pelaaja.nopeus_x=0
        if tapahtuma.type == pygame.QUIT:
            exit()

# tasot.txt -tiedosto. Tiedostossa ei saa olla tyhjiä rivejä
"""
0, 200, 100
-100,100,100
100,100,100
0,0,100
-200,-100,200
200,-100,400
350, -200, 100
-350, -200, 100
-200, -180, 70
-100, -300, 70
0, -400, 50
-100, -500, 30
-200, -600, 50
0, -600, 50
100, -700, 50
-300, -700, 50
200, -800, 50
280, -900, 70
180, -1000, 70
0, -1100, 180
"""