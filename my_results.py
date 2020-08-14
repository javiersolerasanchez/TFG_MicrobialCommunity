#!/usr/bin/python3

# Script to take the output generated on atr2.

#MODIFIED: 03/05/2020 Javier Solera Sánchez

#Este script se ejecuta desde el directorio que contiene a su vez el directorio con cada uno de los experimentos a parsear.
#Se llama al script teniendo como único argumento la carpeta que contiene todas las simulaciones.
import os
import sys
from shutil import copy as cp
import tarfile
import mmodes
from mmodes.vis import plot_comm
import dill as pickle
from matplotlib import rcParams, rcParamsDefault, get_backend, rcParamsOrig
from shutil import rmtree

def make_tarfile(output_filename, source_dir):
    ''' Tar.gz from directory '''
    with tarfile.open(output_filename, "w:gz") as tar:
        tar.add(source_dir, arcname=os.path.basename(source_dir))

dest_dir = sys.argv[1]
curr_dir = sys.argv[1]
if dest_dir.endswith('/'): # set a clean path to dest directory
    dest_dir = dest_dir + "results"
else:
    dest_dir = dest_dir + "/results"
    curr_dir = curr_dir + "/" #importante poner la / para que no de errores de paths después.

#Al usar la función os.path.isdir(f), no funcionaba, hay que poner el path entero, no el directorio concreto ya que se ejecuta desde
#la carpeta anterior
dirs = [f for f in os.listdir(curr_dir) if os.path.isdir(curr_dir+"/"+f) and f.startswith("atr2")]

curr_path = os.getcwd()
if not os.path.exists(dest_dir):
    os.mkdir(dest_dir)
else:
    rmtree(dest_dir)
    os.mkdir(dest_dir)#Como no sobreescribe, borramos y la volvemos a crear.
i = 1
l = 0
n = len(dirs)
for d in dirs:
    sys.stdout.write(f"Working on {d}... ({i}/{n})\n")
    #sys.stdout.flush()
    if len(os.listdir(f"{curr_dir}{d}"))==7:
        i += 1
        l += 1
        prefix=d.split(".")
        #comm=pickle.load(open(f"{d}/cons.p", "rb"))
        #comm.outplot="{d}/{d}_plot.png"
        #plot_comm(comm)
        #print(curr_dir)
        cp(f"{curr_dir}{d}/fluxes_equi.tsv", f"{dest_dir}/equi_fluxes_{prefix[0]}_{l}.tsv")
        cp(f"{curr_dir}{d}/plot_filtered.tsv", f"{dest_dir}/biomass_{prefix[0]}_{l}.tsv")
        cp(f"{curr_dir}{d}/fluxes_filtered.tsv", f"{dest_dir}/fluxes_{prefix[0]}_{l}.tsv")
        if os.path.isfile(f"{curr_dir}{d}/{d}_plot.png"):
            cp(f"{curr_dir}{d}/{d}_plot.png", f"{dest_dir}/{prefix[0]}_{l}_plot.png")       
    else:
        print(f"\tSimulation {d} incomplete.")
        i += 1
        pass

inc_dirs = [f for f in os.listdir(curr_dir) if os.path.isdir(curr_dir+"/"+f) if f.startswith("atr2") and len(os.listdir(f"{curr_dir}{f}"))!=7]      
# make a tar.gz to send it
make_tarfile("results.tar.gz", dest_dir)
print("\n\n***RESULTS***")
print(f"Total of incomplete simulations: {len(inc_dirs)}")
print(f"Total of complete simulations: {(i-1)-len(inc_dirs)}")
print(f"Incomplete simulations: {inc_dirs}")
print(f"Directory with MMODES results: {curr_path}/{dest_dir}")
print("\nDONE!")