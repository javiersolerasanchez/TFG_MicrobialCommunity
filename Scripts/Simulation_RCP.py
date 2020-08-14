#!/usr/bin/python3

# Script PHASE 2 of simulation with atrazine consortium.
# 1.  SIMULATION of 5h, with 4 possible perturbations, in  particular, adding  phosphate to the medium, or incrementing the biomass of H.stevensii and/or Halobacillus sp.
# Command: 'python3 run_Atrazine_simulations.py num_processors num_simulations'

# Author: Jorge Carrasco Muriel
# Date: 30/04/2019
# Modified: 04/11/2019 by Beatriz Garcia Jimenez
# Modified: 12/03/2020 by Javier Solera Sánchez

import matplotlib as MPL
MPL.use('Agg') # change backend of display. I'm not really sure if this will work on a container
import sys, os, re
import subprocess
import json
import mmodes
import random
import dill as pickle
from time import sleep
from multiprocessing import Process, Lock
from data_gen import tsv_filter, log
from copy import deepcopy

lock = Lock() # global variable, accessed by child processes

def runn(md = ""):
    lock.acquire()
    print("Starting simulation on", md)
    lock.release()

    # make working directory based on argument
    subprocess.run(["mkdir", md])
    # clean directory if needed
    files = [f'{md}/{f}' for f in os.listdir(".") if f.find("log_template.txt") != -1 or f[-3:] == "tsv" or f[-3:] == 'png']
    if files:
        subprocess.run(["rm"]+files)

    # PARAMETERS
    # 1) Common parameters of simulation
    media_file = "4_medios.json"
    mod_dir = "/home/javi/Documentos/Root_con_P/" #Directorio donde está el modelo
    intervl = 1 # time of simulation between perturbations; total time will be 2h
    
    # 2) random parameters of simulation
    # 2.1) Medium
    with open(mod_dir + media_file) as json_file:
        gen_media = json.load(json_file) #Abrimos el contenido del archivo y lo metemos en gen_media
    # 2.2) Biomasses
    brand = lambda: random.uniform(0.000013, 0.000055) #Función lambda, se crea así y hace lo que está detras de ':'
    #cada vez que llamemos a lambda se nos generará un número random entre ese intervalo
    biomasses = [brand()] # BGJ: Biomass for athrobacter that always will be in the consortium
    # we want to take all the possibilities with *equal* probabilities
    # BGJ: add 2 additional values to the biomasses vector, that could be only one, both ones or any.
    
    #Este bloque lo que hace es que de manera aleatoria genera unas biomasas iniciales distintas para cada microorganismo 
    #Para que cada experimento sea distinto. Por ello, siempre habrá athrobacter (cantidad aleatoria), pero las cantidades de las otras dos
    #Las ponemos de manera aleatoria, poniendo solo uno de ellos, los dos o ninguno. 
    chosen = random.random() #Generamos un número aleatorio entre cero y uno.
    if chosen > 0.75:
        biomasses += [brand(), 0]
    elif chosen > 0.5:
        biomasses += [0, brand()]
    elif chosen > 0.25:
        biomasses += [brand(), brand()]
    else:
        biomasses += [0,0]
    #Ponemos cada uno de los valores de biomasa en tres variables que usaremos después.
    ar, hb, hl = biomasses # BGJ: split biomasses in 3 different variables
 
    # SIMULATION
    # 1) instantiate Consortium
    volume_petri = 2*3.141593*45*45*15*1e-6 # 2pi*r²*h -> mm³ to L
    cons = mmodes.Consortium(stcut = 1e-8, v = volume_petri, comets_output = False,
    manifest = f"{md}/fluxes.tsv", work_based_on = "id", max_growth = 10,
    mets_to_plot = ["cpd03959_e0", "cpd00027_e0"], title = "Atrazine "+md)

    # 2.1) add models, with random biomass
    cons.add_model(mod_dir+"Arthrobacter_CORRECTED.json", float(ar), solver = "glpk", method = "fba")
    cons.add_model(mod_dir+"Halobacillus_sp_CORRECTED.json", float(hb), solver = "glpk", method = "fba")
    cons.add_model(mod_dir+"Halomonas_stevensii_CORRECTED.json", float(hl), solver = "glpk", method = "fba")

    #Se mete el ID de las bacterias. Si recorremos cons.models, ahí está el nombre de cada modelo, Arthrobacter empieza por k,
    #por eso no nos interesa almacenarlo. Solo almacenamos los otros dos, que serán los que se añadan como perturbación.
    st_ids = [id for id in cons.models if not id.startswith("k")] 
    print(f"Models were loaded on {md}.")

    # 2.2) define initial medium => medium or exudate, already in JSON file
    #root = deepcopy(gen_media[1])
    del(gen_media[0]) # choose medium or exudate
    del(gen_media[1])
    del(gen_media[1])

    # 2.3) add several random perturbations : strain | both | none
    fix_biomass=0.000034  # BGJ: fix biomass to add in the perturbation as probiotics
    for pert in range(3): # BGJ: 2019.11.08 #SI QUEREMOS CAMBIAR EL NÚMERO DE PERTURBACIONES POR SIMULACIÓN, ES AQUÍ.
        # perturbations always carry atrazine
        gen_media.append({"MEDIA" : {"cpd03959_e0" : 0.15}, "PERTURBATION" : "ATRAZINE"}) #Metemos una nueva entrada al diccionario
        chosen = random.random()
        if chosen > 0.75:
            gen_media[-1]["MEDIA"][st_ids[0]] = fix_biomass*100 #Esto lo que hace es meter una nueva entrada en el diccionario dentro de "MEDIA"
            #Con ese id y ese valor. Esta entrada se mete al últmo diccionario de gen_media que es lo último que appendeamos.
            gen_media[-1]["PERTURBATION"] = st_ids[0] #Nos referimos al último diccionario, al key "PERTURBATION" y lo cambiamos por ese valor.
        elif chosen > 0.5: # 2019.11.12: BGJ: to increase biomass 2nd strain: st_ids[1]
            gen_media[-1]["MEDIA"][st_ids[1]] = fix_biomass*100
            gen_media[-1]["PERTURBATION"] = st_ids[1]
        elif chosen > 0.25:
            gen_media[-1]["PERTURBATION"] = st_ids[0] + "_" + st_ids[1]
            gen_media[-1]["MEDIA"][st_ids[0]] = fix_biomass*100
            gen_media[-1]["MEDIA"][st_ids[1]] = fix_biomass*100
   #    elif chosen > 0.2:
   #        gen_media[-1]["MEDIA"] = root["MEDIA"]
   #        gen_media[-1]["PERTURBATION"] = "ROOT_EXUDATE"
        else:
            gen_media[-1]["MEDIA"]['cpd00009_e0'] = 1
            gen_media[-1]["PERTURBATION"] = 'PHOSPHATE'       
       #else: none perturbation (only atrazine)

    # 2.3) add 2nd perturbation (nothing)
    # we need this to evaluate the last state of the consortium because the
    # reward function in MDPbiome for this particular case evaluates degradation of
    # atrazine 1 h after the simulation
    gen_media.append({"MEDIA" : {"cpd03959_e0" : 0.15}, "PERTURBATION" : "ATRAZINE"})

    # 3) Write log
    lock.acquire()
    log(cons, gen_media) #Escribe en un archivo el objeto cons (nuestro experimento), junto con gen_media (están descritas las perturbaciones)
    lock.release()

    it = 1
    t_pers = []
    pers = []
    for mper in gen_media:
        if it == 1:
            # 4) instantiate media
            cons.media = cons.set_media(mper["MEDIA"], True) #El primer diccionario es el medio, lo instanciamos.
        else:
            for k in mper["MEDIA"]: # not needed at all... #Realizamos cambios en el medio.
                if mper["MEDIA"][k] == 0: #Si no hay de un metabolito, cambiamos su valor en el cons.media
                    cons.media[k] = 0
            cons.add_mets(mper["MEDIA"], True) #El resto de metabolitos los añadimos 
        pers.append(mper["PERTURBATION"]) #Metemos en esa lista el valor de la perturbación al final de cada vuelta de bucle.
        # 5) run it
        t_pers.append(cons.T[-1]) 
        cons.run(verbose=False, plot=False, maxT = intervl+cons.T[-1], integrator = "FEA",
        stepChoiceLevel=(0.00027,0.5,100000.), outp = f'{md}/{md}_plot.png', outf = f'{md}/plot.tsv')
        it += 1 
    txpers = { t_pers[i]: pers[i] for i in range(len(t_pers)) } #creamos un diccionario een el que se guardan las perturbaciones en el orden que suceden (no termino de entenderlo)

    # 6. Save simulation
    with open(f'{md}/cons.p', 'wb') as f:
        pickle.dump(cons, f) #El pickle es para guardar objetos en ficheros
    with open(f'{md}/txpers.p', 'wb') as f:
        pickle.dump(txpers, f)
    tsv_filter(f'{md}/plot.tsv', f'{md}/fluxes.tsv', txpers, inplace= False, v = cons.v) #plot.tsv es el output de correr cons. fluxes.tsv se crea al instanciar Consortium.
    if os.path.isfile(f'{md}/fluxes_filtered.tsv'): 
        os.unlink(f'{md}/fluxes.tsv')
    mmodes.vis.plot_comm(cons) 

    lock.acquire()
    print(f"\033[1;32;40mProcess with directory {md} out!\033[0m")
    lock.release()

    del(cons)
    del(txpers)
    del(gen_media)

    return

def main():
    prev_sims = sorted([int(d[5:]) for d in os.listdir(".") if d.startswith("atr2.")])
    if prev_sims:
        prev_sims = prev_sims[-1] + 1
    else:
        prev_sims = 1
    runn("atr2."+str(prev_sims))
    return

if __name__ == "__main__":
    main()

## cons.media contiene todos los metabolitos de los GEM con sus respectivas concentraciones. Si no metemos ningún medio, las concentraciones por defecto
## son cero, al meter el medio, las concentraciones de aquellos metabolitos que están en el medio cambian.

