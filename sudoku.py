#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from typing import Union  # per specificare campi multipli nelll'input funzione
import numpy as np
from collections import defaultdict
#---------------------------------------------------------------------------------#
# CREAZIONE CLASSE
#---------------------------------------------------------------------------------#
class sudoku:
   """ Classe per lavorare con sudoku. Possiede metodi per:
      - Mostrare a schermo il sudoku (metodo show);
      - Risolvere sudoku (metodo solve);
      - Controllare eventuale errori (metodo check);
      - Identificare gli errori (metodo find_errors);
      - Dare suggerimenti (metodo suggest).
      
      Le funzioni di default vengono applicate sullo schema passato in input. 
      all'inizializzazione della classe, tuttavia possono essere utilizzate anche su schemi forniti direttamente alle funzioni stesse.
   """
   #---------------------------------------------------------------------------------#
   #Definire cosa fare e cosa richiedere quando si chiama questo oggetto.
   # region INIT
   def __init__(self,
                X : Union[list, np.ndarray],
                verbose: bool = False ):
      """Inizializzare la classe.  
      Va passata una matrice 9x9, che sarà il sudoku da risolvere. La matrice può essere fornita in input come una:
         - lista di liste;
         - np.array.
      Input:
         - X ((list, np.ndarray), default None) schema del sudoku;
         - verbose (bool, default False) se mostrare più o meno output testuale.
      """
      # Controllare che il sudoku in input sia nel formato giusto.
      self.__input_check__(X)      

      # Convert to NumPy array se lo schema iniziale  è una lista, se invece è un array numpy  lasciare cosi.
      if   isinstance(X,list):
         matrix = np.array(X)
      else:
         matrix = X 
         
      self.original_schema =  matrix.copy()
      
      # Inizializzare il contatore dei suggerimenti, verrà utilizzata dalla funzione 'suggest'.
      self.suggerimento = 0
      
      # Ricavare il numero di numeri da inserire (celle vuote indicate tramite zeri).
      self.numeri_mancanti = np.count_nonzero(matrix.flatten()==0)
      if verbose:
         # Contare il numero di zeri (numeri mancanti) e restituirlo.
         print(f"Numeri mancanti: {self.numeri_mancanti}")

      # Definire le coordinate dei quadranti.
      self.coordinate_quadranti = { 1:[(0, 0), (0, 1), (0, 2),(1, 0), (1, 1), (1, 2),(2, 0), (2, 1), (2, 2)],
                                    2:[(0, 3), (0, 4), (0, 5),(1, 3), (1, 4), (1, 5),(2, 3), (2, 4), (2, 5)],
                                    3:[(0, 6), (0, 7), (0, 8),(1, 6), (1, 7), (1, 8),(2, 6), (2, 7), (2, 8)],
                                    
                                    4:[(3, 0), (3, 1), (3, 2),(4, 0), (4, 1), (4, 2),(5, 0), (5, 1), (5, 2)],
                                    5:[(3, 3), (3, 4), (3, 5),(4, 3), (4, 4), (4, 5),(5, 3), (5, 4), (5, 5)],
                                    6:[(3, 6), (3, 7), (3, 8),(4, 6), (4, 7), (4, 8),(5, 6), (5, 7), (5, 8)],

                                    7:[(6, 0), (6, 1), (6, 2),(7, 0), (7, 1), (7, 2),(8, 0), (8, 1), (8, 2)],
                                    8:[(6, 3), (6, 4), (6, 5),(7, 3), (7, 4), (7, 5),(8, 3), (8, 4), (8, 5)],
                                    9:[(6, 6), (6, 7), (6, 8),(7, 6), (7, 7), (7, 8),(8, 6), (8, 7), (8, 8)]}
      
      self.reverse_quadranti = { # Primo quadrante 
                                 (0, 0): 1,(0, 1): 1, (0, 2): 1, (1, 0): 1, (1, 1): 1, (1, 2): 1, (2, 0): 1,(2, 1): 1,(2, 2): 1,
                                 
                                 # Secondo quadrante
                                 (0, 3): 2, (0, 4): 2,(0, 5): 2,(1, 3): 2,(1, 4): 2,(1, 5): 2,(2, 3): 2,(2, 4): 2,(2, 5): 2,
                                 
                                 # Terzo quadrante
                                 (0, 6): 3, (0, 7): 3,(0, 8): 3,(1, 6): 3,(1, 7): 3,(1, 8): 3,(2, 6): 3,(2, 7): 3,(2, 8): 3,
                                 
                                 # Quarto quadrante 
                                 (3, 0): 4, (3, 1): 4,(3, 2): 4,(4, 0): 4,(4, 1): 4,(4, 2): 4,(5, 0): 4,(5, 1): 4,(5, 2): 4,
                                 
                                 # Quinto quadrante 
                                 (3, 3): 5, (3, 4): 5,(3, 5): 5,(4, 3): 5,(4, 4): 5,(4, 5): 5,(5, 3): 5,(5, 4): 5,(5, 5): 5,
                                 
                                 # Sesto quadrante
                                 (3, 6): 6, (3, 7): 6,(3, 8): 6,(4, 6): 6,(4, 7): 6,(4, 8): 6,(5, 6): 6,(5, 7): 6,(5, 8): 6,
                                 
                                 # Settimo quadrante
                                 (6, 0): 7, (6, 1): 7,(6, 2): 7,(7, 0): 7,(7, 1): 7,(7, 2): 7,(8, 0): 7,(8, 1): 7,(8, 2): 7,
                                 
                                 # Ottavo quadrante
                                 (6, 3): 8, (6, 4): 8,(6, 5): 8,(7, 3): 8,(7, 4): 8,(7, 5): 8,(8, 3): 8,(8, 4): 8,(8, 5): 8,
                                 
                                 # Nono quadrante
                                 (6, 6): 9, (6, 7): 9,(6, 8): 9,(7, 6): 9,(7, 7): 9,(7, 8): 9,(8, 6): 9,(8, 7): 9,(8, 8): 9}

   def __input_check__(self,
                       X : Union[list, np.ndarray],
                       ):
      """Funzione per controllare che il sudoku sia nel formato giusto.
         Input:
            - X (list, np.ndarray) è il sudoku di cui bisogna controllare il formato.
      """
      # Controllo input
      ## Se l'input non è una lista sollevare un errore
      if  not isinstance(X,(list,np.ndarray)):
         raise TypeError("L'input deve essere una matrice")

      ## Se 
      if len(X) != 9:
         raise TypeError("La matrice deve essere in formato 9x9")

      for i in X:
         if len(i) != 9:
            raise TypeError("La matrice deve essere in formato 9x9")              
   # endregion
   #---------------------------------------------------------------------------------#
   # SHOW
   def show(self,
            schema : Union[list, np.ndarray] = None,
            coordinate : list = [],
            colore : str = "\033[1;32m",
            ):
      """
         Funzione per mostrare a schermo il sudoku di input della classe.
         Se viene passata una matrice al posto della variabile schema printa questa nuova matrice.
         Input:
            - schema ((list, np.ndarray),default None)
            - coordinate (list, default []), fornita una lista di coordinate in input queste verranno printate in nel colore scelto.
            - colore (str, default  "\033[1;31m") colore di default rosso. Verde: "\033[1;32m".
      """
      
      # Se non viene passato uno schema viene mostrato a schermo quello assegnato alla classe.
      if schema is None:
         schema = self.original_schema.copy()
      else:
         self.__input_check__(schema)      

      print(" -----------------------")
      for i in range(0,9):
         for j in range(0,9):
               if j== 0 :
                  print("| ",end="")
               if  j == 2 or j== 5  :
                     if (len(coordinate) > 0) & ((i,j) in coordinate): # Se ci sono dei colori da inserire in particolari celle li inserisce
                        print(f"{colore}{schema[i][j]}\033[0m", end = ' | ')
                     else:
                        print(schema[i][j], end = ' | ')

               else:
                  if (len(coordinate) > 0) & ((i,j) in coordinate): # Se ci sono dei colori da inserire in particolari celle li inserisce
                     print(f"{colore}{schema[i][j]}\033[0m",end = ' ')
                  else:
                     print(schema[i][j], end = ' ')
                     
         print('|')
         
         if i == 2 or i == 5 or i == 8 :
               print(" -----------------------")
   #---------------------------------------------------------------------------------#
   # region CHECK
   def __check_rows__(self,
                      schema : np.array):
      """Controllare per errori nelle righe.
         Output:
         -  True se non ci sono errori.
         -  False se ci sono errori.
      """

      # Iterate over the rows
      for row_id in range(0,9):

         # Assegnare ad una variabile la i-esima riga
         row = schema[row_id,:]

         # Il primo valore viene assegnato, poi si itera sugli altri per capire se ci sono duplicati e quindi errori.
         row_values = [row[0]]
         for i in  range(1,9):
            if row[i] in row_values:
               return False

            row_values.append(row[i])
      return True
   
   def __check_columns__(self,
                         schema : np.array):
      """Controllare per errori nelle colonne.
         Output:
         -  True se non ci sono errori.
         -  False se ci sono errori.
      """
      # Iterate over the columns
      for col_id in range(0,9):

         # Assegnare ad una variabile la i-esima riga
         col = schema[:,col_id]

         # Il primo valore viene assegnato, poi si itera sugli altri per capire se ci sono duplicati e quindi errori.
         col_values = [col[0]]
         for i in  range(1,9):
            if col[i] in col_values:
               return False

            col_values.append(col[i])
      return True

   def __check_quadranti__(self,
                           schema : np.array):
      """Controllare per errori nei quadranti.
         Output:
         -  True se non ci sono errori.
         -  False se ci sono errori.
      """
      # Primo loop per prendere le coordinate del ennesimo quadrante
      for quadrante in self.coordinate_quadranti.keys():
         coordinates = self.coordinate_quadranti[quadrante]

         # Secondo loop, controllare che nello stesso quadrante tutti i numeri siano diversi
         valori_quadrante = [schema[coordinates[0]]] 
         for i in range(1,9):

            valore_xy = schema[coordinates[i]] 
            if valore_xy in valori_quadrante:
               return False
            valori_quadrante.append(valore_xy)
      return True

   def check(self,
             schema : Union[list, np.ndarray] = None,
             verbose : bool = False):
      """Funzione per controllare eventuali errori nello sudoku di input della classe.
         Se viene passata una matrice al posto della variabile schema controlla questa nuova matrice.
         Input:
            - schema ((list, np.ndarray), default None)
            - verbose (bool, default False), se mostrare più o meno output testuale.
      """
      
      # se schema non è fornito in input si sta facendo il controllo sul sudoku 
      # fornito in input
      if schema is None:
         schema = self.original_schema.copy()
         
      # Se lo schema è una lista metterlo in formato numpy.
      if  isinstance(schema,list):
         schema = np.array(X)
       
      # Controllare lo schema
      self.__input_check__(schema)

      # Se ci sono errori (duplicati) in riga, in  colonna  o in quadrante c'è un errore.
      if (self.__check_columns__(schema=schema) == False) or ( self.__check_rows__(schema=schema) == False ) or (self.__check_quadranti__(schema=schema) == False):
         if verbose:
            print("Ci sono errori nella risoluzione del sudoku")
         return False
      
      else:
         if verbose:
            print("Sudoku risolto correttamente")
         return True
   # endregion   
   #---------------------------------------------------------------------------------#
   # FIND ERRORS
   def find_errors(self,
                   soluzione : Union[list, np.ndarray] = None,
                   verbose : bool = True
                  ):
      """Funzione per identificare eventuali errori nella soluzione fornita in input.
         Confronta la risoluzione dell'algoritmo con quella fornita ed individua eventuali errori restituendo la loro posizione ed il corretto numero.
         Input:
            - schema ((list, np.ndarray),default None)
            -  verbose (bool, default True) se True printa a schermo l'intero sudoku evidenziando gli errori e le soluzioni giuste.
      """
      # Controllare che il sudoku contenente la soluzione che si vuole controllare fornita input sia nel formato giusto.
      self.__input_check__(soluzione)      

      # Convert to NumPy array la soluzione è una lista, se invece è un array numpy  lasciare cosi.
      if   isinstance(soluzione,list):
         soluzione = np.array(soluzione)
         
      GREEN_BOLD = "\033[1;32m"
      RED_BOLD = "\033[1;31m"
      RESET = "\033[0m"
      coordinate_sbagliate = []

      self.solve()   
      for i in range(0,9):
         for j in range(0,9):
            if soluzione[i,j] != self.sudoku[i,j]:
               print(f"Errore in posizione {i+1,j+1}.{GREEN_BOLD} Numero corretto {self.sudoku[i,j]}{RESET},{RED_BOLD} Numero inserito {soluzione[i,j]} {RESET}.")
               coordinate_sbagliate.append((i,j))

      if verbose:
         self.show(schema=soluzione,coordinate = coordinate_sbagliate,colore="\033[1;31m")
         self.show(schema=self.sudoku.copy(),coordinate = coordinate_sbagliate,colore="\033[1;32m")
         
         

   #---------------------------------------------------------------------------------#
   # SUGGEST  
   def suggest(self,
               n_suggestions : int = 1,
               restore_suggestion : bool = False
               ):
      """Funzione per dare suggerimenti per il sudoku di input della classe.
         Input: 
            - n_suggestions (int, default 1), numeri di suggerimenti. 
            - restore_suggestion (bool, default False), la funzione se richiamata una seconda volta andrà al suggerimento successivo,
                                                        se True ricomincerà con il primo suggerimento.
      """      
      if restore_suggestion:
         self.suggerimento = 0
      
      self.solve()   
         
      for i in range(n_suggestions):
         self.suggerimento += 1
         if self.suggerimento not in self.mappatura_numeri_aggiunti.keys():
            print("Non ci sono suggerimenti disponibili")
            break
         print(f'Inserire il numero {self.mappatura_numeri_aggiunti[self.suggerimento]["soluzione"]} in posizione: {(self.mappatura_numeri_aggiunti[self.suggerimento]["cella"][0]+1,self.mappatura_numeri_aggiunti[self.suggerimento]["cella"][1]+1)}')
         
   #---------------------------------------------------------------------------------#
   # EXTRACT SCHEMA  
   def __get_schema_from_image__(self):
      """Estrarre sudoku dalle immagini"""
      pass   

   #---------------------------------------------------------------------------------#
   # region SOLVE
   def __elenco_numero_ammissibili__(self,
                                         schema : np.array,
                                         row : int ,
                                         column : int ):
      """Input:
         - un sudoku;
         - coordinate di una sua cella.
         Output in formato dictionary:
         - dizionario dei numeri NON ammissibili per quella cella : dict;
         - dizionario dei numeri ammissibili per quella cella : dict;
         - index della cella formato tupla : tuple;
         - riga della cella : int;
         - colonna della cella: int.
      """
      # region Identificare nella riga, colonna e quadrante per le coordinate fornite.
      # Identificare numeri candidati di riga e renderlo un set.
      già_in_riga = set(schema[row,:]) 
   
      # Identificare numeri candidati di colonna e renderlo un set.
      già_in_colonna = set(schema[:,column])
      
      # Identificare numeri candidati del quadrante e renderlo un sset
      quadrante = self.reverse_quadranti[(row,column)] # Ottenere il quadrante corrispondente alle 
                                                       # coordinate (row,column) in input 
      
      ## Estrarre tutte le coordinate dei numeri in un quadrante
      indici_quadrante = self.coordinate_quadranti[quadrante] 
      rows, cols = zip(*indici_quadrante) # Rendere le le coordinate dei numeri in un quadrante in un
                                          # formato adatto per estrarre tutti 
                                          # i numeri di quel quadrante da un np.array
      ## Identificare numeri candidati del quadrante                                   
      già_in_quadrante = set(schema[rows, cols]) 
      # endregion
      #----------#
      # region Identificazione numeri non ammissibili e ammissibili (numeri candidati)
      # Definire il set dei NON numeri ammisibili
      numeri_non_ammissibili = set([0]) # Aggiungere lo zero nel set perchè è il placeholder che
                                        # indica una cella da riempire, perciò non è ammissibile
                                        
      numeri_non_ammissibili.update(già_in_riga) # Aggiungere i numeri non ammissibili per quella riga
      numeri_non_ammissibili.update(già_in_colonna)  # Aggiungere i numeri non ammissibili per quella colonna
      numeri_non_ammissibili.update(già_in_quadrante)  # Aggiungere i numeri non ammissibili per quel quadrante
      
      # Rimuove i numeri non ammissibili trovati tramite le tecniche di livello 5: XY WINGS, X WING, Color Pairs, Remote pairs
      if len(self.elenco_numero_NON_ammissibili) > 0:
         if (row,column) in self.elenco_numero_NON_ammissibili.keys():
            non_ammissibili_tramite_tecniche_livello5 = self.elenco_numero_NON_ammissibili[(row,column)]
            numeri_non_ammissibili.update(non_ammissibili_tramite_tecniche_livello5)

      # Rimuovere i numeri non ammissibili dai numeri possibili, ovvero 1,2,3,4,5,6,7,8,9
      numeri_candidati = set([1,2,3,4,5,6,7,8,9]).difference(numeri_non_ammissibili)
      # endregion
      return {"numeri_candidati":numeri_candidati,
              "numero_non_ammissibili": numeri_non_ammissibili,
              "row":row,
              "column":column,
              "index":(row,column)}
   
   def __elenco_numeri_ammissibili_quadrante__(self):
      """Questa funzione restituisce un dizionario contenente ogni quadrante i possibili numeri candidati per ogni cella."""
      
      # Dizionario per salvare i numeri ammissibili per ogni quadrante.
      self.numeri_ammissibili_quadrante = {}
      for i in range(1,10): # Iterare sui quadranti
         
         # Dizionario dei possibili numeri per ogni cella
         candidati_per_cella  = self.numeri_ammissibili_cella.copy() #

         # Mappatura cella - quadrante. Tramite questo   dizionario tramite coordinate di una cella # si può identificare il suo quadrante 
         coordinate_quadrante = self.coordinate_quadranti[i]     
         
         # Per un singolo quadrante estrarre tutti i numeri candidati per ogni cella.
         candidati_per_cella_del_quadrante = {coppia: candidati_per_cella[coppia] for coppia in coordinate_quadrante 
                                                               if coppia in candidati_per_cella.keys()}
      

         # Inizializzare dizionario. Questo dizionario conterrà per ogni numero le posizioni in cui può
         # essere posizionato. Viene usata la classe defaultdict dalle collections perchè defaultdict previene errori
         # Avendo valori di default per chiavi non esistenti nel dizionario.
         numeri_posizioni = defaultdict(list) 
         for cella,valori_possibili in candidati_per_cella_del_quadrante.items():
            for numero in valori_possibili:
               numeri_posizioni[numero].append(cella)
               
         self.numeri_ammissibili_quadrante[i]=numeri_posizioni
         
   def __elenco_numeri_ammissibili_riga_colonna__(self):
      """Questa funzione restituisce un dizionario contenente ogni riga e colonna i possibili numeri candidati per ogni cella."""
   
      # Inizializzare dizionario per tutti i possibili candidati di una riga con la loro posizione
      self.numeri_ammissibili_riga = {}
      
      # Inizializzare dizionario per tutti i possibili candidati di una colonna con la loro posizione
      self.numeri_ammissibili_colonna = {}
      
      # Entrambi i dizionari precedenti hanno come chiavi i numeri di riga/colonna.
      # Come valori una lista contenente i numeri candidati per ogni  cella di quella riga/colonna.
      
      # Iterare sul numero di riga e colonna
      for i in range(0,8):
         # Dizionari per salvare tutta una riga/colonna sotto unica chiave.
         dizionario_riga_provvisorio = {}
         dizionario_colonna_provvisorio = {}         

         # Iterare sui numeri ammissibili di ogni cella
         for key,value in self.numeri_ammissibili_cella.items():
            
            # Quando si ha una chiave appartenente all'iesima riga inserirla nel dizionario delle righe
            if key[0] == i :
               dizionario_riga_provvisorio[key] = value
               
            # Quando si ha una chiave appartenente all'iesima riga inserirla nel dizionario delle colonne
            if key[1] == i :
               dizionario_colonna_provvisorio[key] = value

         if len(dizionario_riga_provvisorio) > 0:
            self.numeri_ammissibili_riga[i] = dizionario_riga_provvisorio
      
         if len(dizionario_colonna_provvisorio) > 0:
            self.numeri_ammissibili_colonna[i] = dizionario_colonna_provvisorio
     
   def __basic_solver__(self): 
      """Compila le celle vuote seguendo il criterio più semplice basato sul controllo delle possibili 
         soluzioni di una determinata cella. Se controllando riga, colonna e quadrante c'è una sola soluzione possibile per quella cella questa viene inserita.
      """

      
      # While loop per la risoluzione del sudoku. Affinchè in ogni loop completo su righe e colonne si trova almeno una soluzione
      # questo while loop continuerà l'esecuzione. Qualora in un loop intero non si trova soluzione significa che l'algoritmo è bloccato e il while loop viene fermato.
      while True:
         
         self.numeri_ammissibili_cella = {} # Dizionario che tiene conto di ogni soluzione ammissibile per ogni cella da risolvere.
         # region Risoluzione con controllo di riga colonna e quadrante (se in quella riga c'è una sola soluzione possibile assegnarla)
         soluzione_trovata_in_questa_iterazione = False 
         for riga in range(0,9): 
            for colonna in range(0,9):
               
               # Zero è il placeholder dei numeri che bisogna identificare.
               # Perciò se il numero della cella di index (riga,colonna) è uno ZERO bisogna trovare i numeri candidati per quella posizione.
               if self.sudoku[riga,colonna] == 0: 

                  # Trovare l'elenco dei numeri ammissibili e non ammissibili per la cella in considerazione.
                  output__elenco_numero_ammissibili__= self.__elenco_numero_ammissibili__(self.sudoku.copy(),
                                                                                          riga,
                                                                                          colonna)
                  
                  # Assegnare i numeri candidati ad una nuova variabile così da rendere il codice più leggibile
                  numeri_candidati = output__elenco_numero_ammissibili__["numeri_candidati"]            

                  # Salvare il set numeri ammissibili per la cella in considerazione.
                  self.numeri_ammissibili_cella[(riga,colonna)] = numeri_candidati
               
                  # Adesso che si hanno i numeri candidati per la posizione (riga,colonna) se c'è un solo candidato
                  # ovvero len(set) == 1 inserire in quella posizione quel numero.
                  if len(numeri_candidati) == 1:
                     soluzione = numeri_candidati.pop() # Estrarre il numero che rappresenta la soluzione
                     
                     # Assegnare la soluzione nel dizionario che tiene traccia delle soluzioni
                     self.numeri_aggiunti += 1
                     self.mappatura_numeri_aggiunti[self.numeri_aggiunti] = {"cella":(riga,colonna),
                                                                             "soluzione":soluzione}
                     
                     # Assegnare la soluzione 
                     self.sudoku[riga,colonna] = soluzione # Estrarre l'elemento 
                     soluzione_trovata_in_questa_iterazione = True # Aggiornare questo parametro in modo da fare un nuovo loop visto che una soluzione è stata trovata.  

         # endregion      
      
         # Se non ci sono zeri nel sudoku significa che è stato risolto quindi fermare il loop.
         if 0 not in self.sudoku.flatten():
            self.solved = True      
            break   
         

         # Se in un'intera iterazione nessuan soluzione è stata trovata il risolutore è bloccato, perciò fermare il loop.         
         if soluzione_trovata_in_questa_iterazione == False:
            break 

   def __solver_per_quadrante__(self):
      """Questa funzione controlla  riga colonna e quadrante, se in tutte le altre celle del quadrante quel numero non può essere assegnato metterlo nell'unico posto possibile."""
      

      
      # Runnare la funzione che permette di identificare per ogni quadrante le possibili soluzioni
      self.__elenco_numeri_ammissibili_quadrante__()
      for i in range(1,10): # Iterare sui quadranti
         
         numeri_posizioni = self.numeri_ammissibili_quadrante[i]

         # Scorrere per tutte le possibili soluzioni per ogni numero
         for numero,lista_possibili_posizioni in numeri_posizioni.items():
            # Se un numero ha una sola possibile soluzione assegnarla.
            if len(lista_possibili_posizioni) == 1:
            
               self.sudoku[lista_possibili_posizioni[0]] = numero
               self.numeri_aggiunti += 1
               self.mappatura_numeri_aggiunti[self.numeri_aggiunti] = {"cella":(lista_possibili_posizioni[0]),
                                                                       "soluzione":numero}
         
         # Se non ci sono zeri nel sudoku significa che è stato risolto quindi fermare il loop.
         if 0 not in self.sudoku.flatten():
            self.solved = True
            break    
         
   def __solver_per_riga__(self):
      """Guarda su ogni riga se c'è una cella con posizione univoca e la completa."""
      for i in range(0,9):
         numeri_posizioni = defaultdict(list) 
         if i in self.numeri_ammissibili_riga.keys():
            for cella,valori_possibili in self.numeri_ammissibili_riga[i].items():
               for numero in valori_possibili:
                  numeri_posizioni[numero].append(cella)
                  
            # Scorrere per tutte le possibili soluzioni per ogni numero
            for numero,lista_possibili_posizioni in numeri_posizioni.items():
               # Se un numero ha una sola possibile soluzione assegnarla.
               if len(lista_possibili_posizioni) == 1:
                  self.sudoku[lista_possibili_posizioni[0]] = numero
                  self.numeri_aggiunti += 1
                  self.mappatura_numeri_aggiunti[self.numeri_aggiunti] = {"cella":(lista_possibili_posizioni[0]),
                                                                          "soluzione":numero}

               # Se non ci sono zeri nel sudoku significa che è stato risolto quindi fermare il loop.
               if 0 not in self.sudoku.flatten():
                  self.solved = True

   def __solver_per_colonna__(self):
      """Guarda su ogni colonna se c'è una cella con posizione univoca e la completa."""
      for i in range(0,9):
         numeri_posizioni = defaultdict(list) 
         if i in self.numeri_ammissibili_colonna.keys():
            for cella,valori_possibili in self.numeri_ammissibili_colonna[i].items():
               for numero in valori_possibili:
                  numeri_posizioni[numero].append(cella)
                  
            # Scorrere per tutte le possibili soluzioni per ogni numero
            for numero,lista_possibili_posizioni in numeri_posizioni.items():
               # Se un numero ha una sola possibile soluzione assegnarla.
               if len(lista_possibili_posizioni) == 1:
                  self.sudoku[lista_possibili_posizioni[0]] = numero
                  self.numeri_aggiunti += 1
                  self.mappatura_numeri_aggiunti[self.numeri_aggiunti] = {"cella":(lista_possibili_posizioni[0]),
                                                                          "soluzione":numero}

               # Se non ci sono zeri nel sudoku significa che è stato risolto quindi fermare il loop.
               if 0 not in self.sudoku.flatten():
                  self.solved = True

   def __share_unit__(self,a, b):
      """Funzione di supporto per le funzioni:
         - __xy_wing__
         - __x_wing__
      """
      (r1, c1), (r2, c2) = a, b
      return r1 == r2 or c1 == c2 or (r1 // 3, c1 // 3) == (r2 // 3, c2 // 3)

   def __xy_wing__(self):
      """Algoritmo di risuluzione XY-WING implementato da chatGPT"""
      candidates = self.numeri_ammissibili_cella.copy()      
      bivalue_cells = [cell for cell, vals in candidates.items() if len(vals) == 2]

      for pivot in bivalue_cells:
         x, y = list(candidates[pivot])
         wings = []
         for other in bivalue_cells:
               if other == pivot:
                  continue
               if self.__share_unit__(pivot, other):
                  vals = candidates[other]
                  if x in vals or y in vals:
                     wings.append(other)

         for i in range(len(wings)):
               for j in range(i + 1, len(wings)):
                  w1, w2 = wings[i], wings[j]
                  v1, v2 = candidates[w1], candidates[w2]
                  common = (v1 | v2) - {x, y}
                  if len(common) == 1:
                     z = next(iter(common))
                     if ({x, z} == v1 and {y, z} == v2) or ({y, z} == v1 and {x, z} == v2):
                           for cell in candidates:
                              if cell not in (pivot, w1, w2):
                                 if self.__share_unit__(cell, w1) and self.__share_unit__(cell, w2):
                                       if z in candidates[cell]:
                                          self.elenco_numero_NON_ammissibili[cell].add(z)
                                          #print("__xy_wing__",cell,z)
  
   def __x_wing__(self):
      """Algoritmo di risuluzione X-WING implementato da chatGPT"""
      candidates = self.numeri_ammissibili_cella.copy()  
      
      # Controlla per righe
      for digit in range(1, 10):
         rows_with_digit = defaultdict(list)
         for (r, c), vals in candidates.items():
            if digit in vals:
                  rows_with_digit[r].append(c)

         # Cerca due righe con lo stesso set di 2 colonne
         for r1 in rows_with_digit:
            if len(rows_with_digit[r1]) == 2:
                  for r2 in rows_with_digit:
                     if r2 <= r1:
                        continue
                     if rows_with_digit[r2] == rows_with_digit[r1]:
                        c1, c2 = rows_with_digit[r1]
                        
                        # Elimina digit da altre celle nelle stesse colonne
                        for r in range(9):
                              if r not in (r1, r2):
                                 for c in (c1, c2):
                                    if digit in candidates.get((r, c), set()):
                                          self.elenco_numero_NON_ammissibili[(r, c)].add(digit)
                                          #print("__x_wing__",(r, c),digit)

      # Controlla per colonne
      for digit in range(1, 10):
         cols_with_digit = defaultdict(list)
         for (r, c), vals in candidates.items():
            if digit in vals:
                  cols_with_digit[c].append(r)

         # Cerca due colonne con lo stesso set di 2 righe
         for c1 in cols_with_digit:
            if len(cols_with_digit[c1]) == 2:
                  for c2 in cols_with_digit:
                     if c2 <= c1:
                        continue
                     if cols_with_digit[c2] == cols_with_digit[c1]:
                        r1, r2 = cols_with_digit[c1]
                        
                        # Elimina digit da altre celle nelle stesse righe
                        for c in range(9):
                              if c not in (c1, c2):
                                 for r in (r1, r2):
                                    if digit in candidates.get((r, c), set()):
                                          self.elenco_numero_NON_ammissibili[(r, c)].add(digit)
                                          #print("__x_wing__",(r, c),digit)

   def __backtracking_valide__(self,
                               idx=0,
                               scelta_corrente=None,
                               usati_primo=None, 
                               usati_secondo=None):
      if scelta_corrente is None:
         scelta_corrente = {}
      if usati_primo is None:
         usati_primo = {}
      if usati_secondo is None:
         usati_secondo = {}
         
      if idx == len(self.chiavi):
         return [scelta_corrente.copy()]
      
      tutte_soluzioni = []
      chiave = self.chiavi[idx]
      primo, secondo = chiave
      
      for v in self.dizionario[chiave]:
         if v not in usati_primo.get(primo, set()) and v not in usati_secondo.get(secondo, set()):
               usati_primo.setdefault(primo, set()).add(v)
               usati_secondo.setdefault(secondo, set()).add(v)
               scelta_corrente[chiave] = v
               
               tutte_soluzioni.extend(self.__backtracking_valide__(idx + 1, scelta_corrente, usati_primo, usati_secondo))
               
               usati_primo[primo].remove(v)
               usati_secondo[secondo].remove(v)
               del scelta_corrente[chiave]
      return tutte_soluzioni

   def solve(self,
             verbose : bool = False
             ):
      """ 
         Funzione  per risolvere  sudoku, è basata su metodi basici di controllo di riga,colonna e quadrante.
         Per i sudoku più difficile viene utilizzato un algoritmo di risoluzione basato sul backtracking.
         Input:
            - verbose (bool, default False) se True più output testuale;
            - schema (list,np.array, default None) se None risolve il sudoku passato in input alla   
                creazione della classe, altrimenti risolve il sudoku passato in input alla funzione.
         """
      
      # Copiare lo schema originale ed assegnarlo al nome sudoku 
      self.sudoku  = self.original_schema.copy()   # Al contrario del 'self.original schema', il 'self.sudoku'  
                                                   # verrà aggiornato con i numeri soluzione trovati dall'algoritmo di risoluzione.

      # Inizializzare il dizionario dei numeri non ammissibili, verrà aggiornato dalle funzioni X e XY WING
      # funzioni dedicate all'esclusione di numeri ammissibli.
      self.elenco_numero_NON_ammissibili = defaultdict(set)
         

      # Dizionario per tenere traccia di ogni soluzione trovata per ogni cella. 
      self.mappatura_numeri_aggiunti = {}     
      
       # Contatore per tenere traccia dei numeri aggiunti
      self.numeri_aggiunti = 0
      
      # Parametri per tenere sotto controllo il while loop
      self.solved = False # Per bloccare il while loop una volta trovata la soluzione
      iterazioni = 0      # Contatore i loop completi, utile per fermare l'algoritmo dopo tot iterazioni
          

      while not self.solved:
         self.__basic_solver__()
         self.__solver_per_quadrante__()


         self.__basic_solver__()
         self.__elenco_numeri_ammissibili_riga_colonna__()
         self.__solver_per_riga__()

         self.__basic_solver__()
         self.__elenco_numeri_ammissibili_riga_colonna__()
         self.__solver_per_colonna__()
         
         self.__xy_wing__()
         self.__x_wing__()
         
         # Ad ogni iterazione nel caso peggiore va inserito un solo numero
         # Perciò le iterazioni massime sono date dal numero massimo di numeri mancanti
         if iterazioni > self.numeri_mancanti:
            break 

         iterazioni += 1 
      # Se non ci sono zeri nel sudoku  e non ci sono errori significa che è stato risolto correttamente.
      if (0 not in self.sudoku.flatten()) & (self.check(self.sudoku)):
         self.solved = True
          
      else:
         
         # Risoluzione tramite il backtracking
         self.dizionario = self.numeri_ammissibili_cella.copy()
         self.chiavi = list(self.dizionario.keys())         
         
         # Disposizioni possibili tramite backtracking
         disposizioni_valide = self.__backtracking_valide__()
      
         # Controllare quale disposizione ottenuta tramite backtracking sia corretta
         for d in disposizioni_valide:
            numeri_aggiunti_provvisori = 0 # Statistica solo per print, permette di aggiornare il numero di soluzione trovate.
            schema = self.sudoku.copy()   
            mappatura_numeri_aggiunti_provvisoria = {} # Per avere una mappatura provvisorio della probabile soluzione.
            for index, numero in d.items():
               schema[index] = numero          # Inserire nello schema provvisorio la probabile soluzione
               numeri_aggiunti_provvisori += 1 # Aggiornare il contatore dei numeri provvisori inseriti
               
               # Per tenere conto della mappatura dei numeri anche se viene utilizzato il backtracking
               mappatura_numeri_aggiunti_provvisoria[numeri_aggiunti_provvisori] = {"cella":index,
                                                                                    "soluzione":numero}
            if (0 not in schema.flatten()) & (self.check(schema=schema)):
               self.solved = True
               self.sudoku = schema.copy()
               
               # Aggiornare il conteggio dei numeri aggiunti. Vengono aggiunti i numeri identificati tramite backtracking
               self.numeri_aggiunti += numeri_aggiunti_provvisori    

               # Aggiungere al dizionario originale della mappatura_numeri_aggiunti i risultati ottenuti tramite backtracking
               for chiave, elementi in mappatura_numeri_aggiunti_provvisoria.items():             
                  self.mappatura_numeri_aggiunti[chiave] = elementi
               break
      
                

      if verbose:
         if self.solved:
            print(f"Sudoku completato. Sono stati aggiunti {self.numeri_aggiunti} numeri.")      
         else:
            print(f"Sudoku non risolto. Nonostante siano stati aggiunti {self.numeri_aggiunti} numeri.")
         self.show(self.sudoku)
   # endregion
#---------------------------------------------------------------------------------#
# CREAZIONE INPUT PER TESTARE LE FUNZIONI DELLA CLASSE   
#---------------------------------------------------------------------------------#
# Creare un sudoku fittizio per fare i primi controlli su righe e colonne

if __name__ == "__main__":
   X_righe_colonne_giuste = []
   column = [ j for j in range(1,10) ]
   for i in range(1,10):
      if i > 1:
         column.append(i-1)
         column.reverse()
         column.pop()
         column.reverse()
      colonna = column.copy()
      X_righe_colonne_giuste.append(colonna)
   
   X = []
   for i in range(1,10):
      colonna = []
      for j in range(1,10):
         colonna.append(j)
      X.append(colonna)


   S = sudoku(X)
   #S.show()

   S2 = sudoku(X_righe_colonne_giuste)
   #S2.show()
   #S2.check()

   # Settimana sudoku n870, schema pagina principale (risolto)
   schema1 = [[8,2,9,7,6,5,3,4,1],
            [1,4,7,3,2,8,9,6,5],
            [5,6,3,9,4,1,8,7,2],
            [7,9,8,1,3,6,2,5,4],
            [4,1,6,5,9,2,7,8,3],
            [3,5,2,8,7,4,1,9,6],
            [6,3,5,2,8,9,4,1,7],
            [9,7,4,6,1,3,5,2,8],
            [2,8,1,4,5,7,6,3,9]] 
   S4 = sudoku(schema1)
   S4.show()
   S4.check()

   # Settimama sudoku n870, schema pagina principale (da risolvere)
   schema1_tosolve = [[8,0,0,0,0,5,0,4,1],
                     [0,4,7,3,0,0,0,0,5],
                     [0,6,3,0,0,1,8,0,0],
                     [0,9,0,1,0,0,2,0,4],
                     [0,0,0,0,9,0,0,0,0],
                     [3,0,2,0,0,4,0,9,0],
                     [0,0,5,2,0,0,4,1,0],
                     [9,0,0,0,0,3,5,2,0],
                     [2,8,0,4,0,0,0,0,9]] 
   S5 = sudoku(schema1_tosolve)
   S5.show()
   S5.check()