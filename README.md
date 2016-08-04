# ZRisk

##ZRisk plugin za procenu zemljotresnog rizika zgrada

ZRisk je plugin za računanje stepena oštećenja zgrada i gubitka ljudi na osnovu ulaznog parametra ubrzanja tla i funkcija povredljivosti koje se zadaju u posebnom lejeru. Krive povredljivosti se zadaju u delimited text lejeru sa numeričkim podacima o ubrzanju na površini lokalnog tla, stepenu oštećenja objekta za zadato ubrzanje i procentu gubitka stanovništva za svaku krivu. Podaci su zadati po kolonama i ne postoji ograničenje broja krivih. Na primer: 
Za krivu 1 format je a1, p1, h1, što označava:
* a1– ubrzanje za krivu 1, 
* p1 – physical loss function za krivu 1 i 
* h1 – human loss function za krivu 1. 

Zatim slede podaci za krivu 2 a2,p2,h2 itd. U lejeru u kojem su definisani objekti (zgrade), potrebno je za svakom unesenom objektu pridružiti tip krive povredljivosti za objekat (pi) i tip krive povredljivosti za stanovništvo (hi), kao i ukupan broj stanara u objektu. Rezultat rada su sračunate vrednosti oštećenja i gubitka ljudi za svaku zgradu kao posebna polja lejera sa objektima.


Category: Vector 
Tags: seismology 
More info: homepage   bug_tracker   code_repository

Author: Dejan Dragojević, Nemanja Paunić

Installed version: 0.1 (in /home/nemanja/.qgis2/python/plugins/ZRisk)
