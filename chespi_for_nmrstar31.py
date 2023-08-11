# -*- coding: utf-8 -*-
logo = """

Modified CheSPI for NMR-STAR 3.1

Original file is located at
    https://colab.research.google.com/github/pokynmr/POKY/blob/master/Jupyter_Notebooks/CheSPI_SS_prediction.ipynb

by Woonghee Lee, Ph.D. and Karen Pham 
(woonghee.lee@ucdenver.edu;POKY Team, Department of Chemistry, University of Colorado Denver)
    
August 5, 2023

Original CheSPI is from Mulder Laboratory.
by Jakob Toudahl Nielsen and Frans A A Mulder.

CheSPI: chemical shift secondary structure population inference

Please cite: 

CheSPI: chemical shift secondary structure population inference.
Jakob Toudahl Nielsen and Frans A A Mulder, J. Biomol. NMR, 2021 Jul;75(6-7):273-291.

https://doi.org/10.1007/s10858-021-00374-w

"""


# Uncomment below if you wish to use your own condition not from the BMRB file.
# pH = 7
# temperature = 298
# atm = 1
# ionic_strength = 0.1
# sequence = 'MVF...'
# physical_state = 'native'

print(logo)

import os, sys
from requests_html import HTMLSession
import requests
import ssl
import re
ssl._create_default_https_context = ssl._create_unverified_context

try:
    in_file = sys.argv[1]
except:
    print(f'\tUSAGE: python ./chespi_for_nmrstar31.py bmr0000.str') 
    print(f'\t\t or')
    print(f'\tUSAGE: python ./chespi_for_nmrstar31.py 0000')
    print(f'\t\t if you want to download from BMRB')

if not os.path.exists(in_file):
    bmrbID = ''.join(re.findall(r'\d+', os.path.basename(in_file)))
    print('getting bmrb file ' + bmrbID)
    bmrpath = f'https://bmrb.io/ftp/pub/bmrb/entry_directories/bmr{bmrbID}/bmr{bmrbID}_3.str'
    session = HTMLSession()
    try:
        r = session.get(bmrpath, timeout=100000)
        r.html.render(timeout=100000)
        response = r.html.html
    except:
        print('Error in downloading from BMRB')
        sys.exit(1)
    in_file = f'bmr{bmrbID}_3.str'
    f = open(in_file, 'w')
    f.write(response)
    f.close()

f = open(in_file, 'r')
lines = f.readlines()
f.close()


# Get sequence information
aa13dict={'A': 'ALA', 'C': 'CYS', 'E': 'GLU', 'D': 'ASP', 'G': 'GLY',
          'F': 'PHE', 'I': 'ILE', 'H': 'HIS', 'K': 'LYS', 'M': 'MET',
          'L': 'LEU', 'N': 'ASN', 'Q': 'GLN', 'P': 'PRO', 'S': 'SER',
          'R': 'ARG', 'T': 'THR', 'W': 'TRP', 'V': 'VAL', 'Y': 'TYR'}
aa31dict = {v: k for k, v in aa13dict.items()}

atom_list = ['H', 'N', 'CA', 'CB', 'C', 'HA', 'HA2', 'HA3', 'HB', 'HB2', 'HB3']

if 'sequence' not in locals():
    sequence, nfirst, nseqcol = '', -1, -1
    for i in range(len(lines)-10):
        if sequence != '':
            break
        line = lines[i].strip()
        if line == '_Entity_comp_index.ID':
            for j in range(i+1, len(lines)):
                line2 = lines[j].strip()
                if line2 == '_Entity_comp_index.Comp_ID':
                    nseqcol = j-i
                    break
                if nseqcol != -1:
                    break
            if nseqcol == -1:
                print(f'\tSequence information cannot be found. Quitting...')
                sys.exit(1)
        for j in range(i+1, len(lines)):
            line2 = lines[j].strip()
            if line2 == 'stop_':
                break

            sp_list = line2.split()
            if len(sp_list) < nseqcol:
                continue
            try:
                a = aa31dict[sp_list[nseqcol]]
                sequence += a
                if nfirst == -1:
                    nfirst = int(sp_list[0])
            except:
                continue
print(f'SEQUENCE: {sequence}')

# Get pH, temperature, atm and ionic_strength information
for i in range(len(lines)-10):
    line = lines[i].strip()
    if line == '_Sample_condition_variable.Type':
        for j in range(i+1, len(lines)):
            line2 = lines[j].strip()
            if line2 == 'stop_':
                break
            sp_list = line2.split()
            if len(sp_list) < 2:
                continue
            if 'pH' not in locals() and sp_list[0] == 'pH':
                pH = float(sp_list[1])
            if 'temperature' not in locals() and sp_list[0] == 'temperature':
                temperature = float(sp_list[1])
            if 'atm' not in locals() and sp_list[0] == 'pressure':
                atm = float(sp_list[1])
            if 'ionic_strength' not in locals() and sp_list[0:2] == ["'ionic", "strength'"]:
                ionic_strength = float(sp_list[2])
                if 'mM' in sp_list:
                    ionic_strength /= 1000.0
                
        else:
            continue
        break

if 'pH' in locals():
    print(f'\tpH:\t{pH}')
else:
    pH = 7.0
    print(f'\tpH is not defined. We use 7.0 as a default.')

if 'temperature' in locals():
    print(f'\ttemperature:\t{temperature}')
else:
    temperature = 298
    print(f'\ttemperature is not defined. We use 298 as a default.')

if 'atm' in locals():
    print(f'\tpressure:\t{atm}')
else:
    atm = 1
    print(f'\tpressure is not defined. We use 1 as a default.')

if 'ionic_strength' in locals():
    print(f'\tionic strength:\t{ionic_strength}')
    if ionic_strength == 0:
        ionic_strength = 0.001
        print(f'\tWARNING: zero ionic strength is not supported. We use 0.001 as a default.')
else:
    ionic_strength = 0.1
    print(f'\tionic strength is not defined. We use 0.1 as a default.')

# Get physical state information
if 'physical_state' not in locals():
    physical_state = ''
for i in range(len(lines)-10):
    line = lines[i].strip()
    ncol = -1
    if physical_state == '' and line == '_Entity_assembly.ID':
        for j in range(i+1, len(lines)):
            line2 = lines[j].strip()
            if line2 == 'stop_':
                break
            if line2 == '_Entity_assembly.Physical_state':
                ncol = j-i
                break
        if ncol != -1:
            for j in range(i+1, len(lines)):
                line2 = lines[j].strip()
                if line2 == 'stop_':
                    break
                sp_list = line2.split()
                try:
                    if line2.find("'") == -1:
                        physical_state = sp_list[ncol]
                        break
                    else:
                        physical_state = sp_list[ncol+1]
                        break
                except:
                    continue            
            else:
                continue
            break
physical_state = physical_state.strip()
if physical_state != '':
    print(f'\tphysical state:\t{physical_state}')
else:
    physical_state = 'native'
    print(f'\tphysical state is not defined. We use native as a default.')
# Get chemical shift information
ncol = [-1,] * 7
fields = ['_Atom_chem_shift.Seq_ID', '_Atom_chem_shift.Comp_ID', 
          '_Atom_chem_shift.Atom_ID', '_Atom_chem_shift.Atom_type', 
          '_Atom_chem_shift.Val', '_Atom_chem_shift.Val_err', 
          '_Atom_chem_shift.Ambiguity_code']

content='''    loop_
       _Atom_shift_assign_ID
       _Residue_seq_code
       _Residue_label
       _Atom_name
       _Atom_type
       _Chem_shift_value
       _Chem_shift_value_error
       _Chem_shift_ambiguity_code
       
'''

line2 = ''
for i in range(len(lines)-10):
    line = lines[i].strip()
    if line2 == 'stop_':
        break 
    if line == '_Atom_chem_shift.ID':
        for j in range(i+1, len(lines)):
            line2 = lines[j].strip()
            if line2 == 'stop_':
                break
            if line2 in fields:
                ncol[fields.index(line2)] = j - i
        if -1 in ncol:
            if ncol.index(-1) not in [5, 6]:
                print(f'\t{fields[ncol.index(-1)]} data is missing. Quitting...')
                sys.exit(1)
            else:
                if ncol[5] == -1:
                    print(f'\tWARNING: Chem_shift_value_error is not given. We use 0 as a default.')
                if ncol[6] == -1:
                    print(f'\tWARNING: Ambiguity_code is not given. We use 1 as a default.')
        for j in range(i+1, len(lines)):
            lines2 = lines[j].strip()
            if lines2.find('_Atom_chem') == 0 or lines2 == '' or \
                    lines2 == 'stop_' or lines2 == 'save_':
                continue
            sp_list = lines2.split()
            try:
              val_err = sp_list[ncol[5]]              
            except:
              val_err = '0.000'
            try:
                amb_code = sp_list[ncol[6]]
                if amb_code not in ['1', '2', '3', '4', '5', '6', '9', '.']:
                    amb_code = '1' # ambiguity code is not in the field.
            except:
                amb_code = '1'
            try:
                temp = '%5s %5s %3s %5s %5s %8.3f %6s %s\n' % \
                        (sp_list[0], sp_list[ncol[0]], sp_list[ncol[1]], 
                        sp_list[ncol[2]], sp_list[ncol[3]],
                        float(sp_list[ncol[4]]), val_err, amb_code)
            except:
                continue
            content += temp

content += '\nstop_\n'

chespi_star = in_file.replace('.str', '_chespi.str')
if chespi_star == in_file:
    chespi_star = in_file + '_chespi.str'
ID = os.path.basename(chespi_star).replace('_chespi.str', '')
f = open(chespi_star,'w')
f.write(content)
f.close()

#@title **Add header information**
def add_shifts_header(filename):
    shifts_header='''
save_assigned_chem_shift_list_1
   _Saveframe_category               assigned_chemical_shifts

   _Details                          .

'''
    f = open(filename, 'r')
    text=f.read()
    f.close()
    text = shifts_header + text + '\n\nsave_\n\n'
    f = open(filename, 'w')
    f.write(text)
    f.close()

def add_dss(filename):
    dss='''
	################################
	#  Chemical shift referencing  #
	################################

save_chemical_shift_reference_1
   _Saveframe_category   chemical_shift_reference

   _Details              .

   loop_
      _Mol_common_name
      _Atom_type
      _Atom_isotope_number
      _Atom_group
      _Chem_shift_units
      _Chem_shift_value
      _Reference_method
      _Reference_type
      _External_reference_sample_geometry
      _External_reference_location
      _External_reference_axis
      _Indirect_shift_ratio

      DSS C 13 'methyl protons' ppm 0 internal indirect . . . 0.25144953
      DSS H  1 'methyl protons' ppm 0 internal direct   . . . 1.0
      DSS N 15 'methyl protons' ppm 0 internal indirect . . . 0.101329118

   stop_

save_

    '''
    f = open(filename, 'r')
    text=f.read()
    f.close()
    text = dss + text
    f = open(filename, 'w')
    f.write(text)
    f.close()

# Molecular Weight Dictionary
AA_MW='''Alanine	Ala	A	89.1
Arginine	Arg	R	174.2
Asparagine	Asn	N	132.1
Aspartate	Asp	D	133.1
Cysteine	Cys	C	121.2
Glutamate	Glu	E	147.1
Glutamine	Gln	Q	146.2
Glycine	Gly	G	75.1
Histidine	His	H	155.2
Isoleucine	Ile	I	131.2
Leucine	Leu	L	131.2
Lysine	Lys	K	146.2
Methionine	Met	M	149.2
Phenylalanine	Phe	F	165.2
Proline	Pro	P	115.1
Serine	Ser	S	105.1
Threonine	Thr	T	119.1
Tryptophan	Trp	W	204.2
Tyrosine	Tyr	Y	181.2
Valine	Val	V	117.1'''
AA_MW_lines = AA_MW.split('\n')
AA_MW_list = list(map(lambda x: (x.split()[2], float(x.split()[3])),
                      AA_MW_lines))
AA_MW_dict = dict(AA_MW_list)
One2Three_list = list(map(lambda x: (x.split()[2], x.split()[1].upper()),
                      AA_MW_lines))
One2Three_dict = dict(One2Three_list)

mol_temp='''
    ########################
    #  Monomeric polymers  #
    ########################

save_entity
   _Saveframe_category                          monomeric_polymer

   _Mol_type                                    polymer
   _Mol_polymer_class                           protein
   _Name_common                                 entity
   _Molecular_mass                              $MW
   _Mol_thiol_state                             .
   _Details                                     .

   	##############################
   	#  Polymer residue sequence  #
   	##############################

      _Residue_count                               $NUMSEQ
   _Mol_residue_sequence
;
$ONESEQ
;
   loop_
      _Residue_seq_code
      _Residue_label

$THREESEQ

   stop_

   _Sequence_homology_query_date                .
   _Sequence_homology_query_revised_last_date   .

save_

'''

def add_mol_seq(filename, fasta):
    # the number of sequence
    mol = mol_temp.replace('$NUMSEQ', str(len(fasta)))

    # Molecular weight
    mw = 0
    for i in range(len(fasta)):
        mw += AA_MW_dict[fasta[i]]
    mol = mol.replace('$MW', str(mw))

    # one-letter
    fasta10 = ''
    for i in range(0,  len(fasta), 10):
        fasta10 += fasta[i:i+10]+'\n'
    mol = mol.replace('$ONESEQ', fasta10)

    # three-letter
    seq5 = ''
    for i in range(0, len(fasta), 5):
        subfasta = fasta[i:i+5]
        subseq = ''
        for j in range(len(subfasta)):
            aaa = One2Three_dict[subfasta[j]]
            nseq = i+j+1
            subseq += '%4d %s' % (nseq, aaa)
        if subseq != '':
            seq5 += '    ' + subseq + '\n'
    mol = mol.replace('$THREESEQ', seq5)

    # rewrite
    f = open(filename, 'r')
    text=f.read()
    f.close()
    text = mol + text
    f = open(filename, 'w')
    f.write(text)
    f.close()

phy_state_temp = '''
##################################
#  Molecular system description  #
##################################

save_assembly
   _Saveframe_category         assembly
   _System_physical_state      $state

save_
'''
def add_physical_state(filename, physical_state):
    ps = phy_state_temp.replace('$state', physical_state)

    # rewrite
    f = open(filename, 'r')
    text=f.read()
    f.close()
    text = ps + text
    f = open(filename, 'w')
    f.write(text)
    f.close()

cond_temp='''
#######################
#  Sample conditions  #
#######################
save_sample_conditions_1
   _Saveframe_category   sample_conditions

   _Details              .

   loop_
      _Variable_type
      _Variable_value
      _Variable_value_error
      _Variable_value_units

      pH            $pH . pH
      pressure      $bar . atm
      temperature   $temperature . K

   stop_
save_
'''
def add_condition(filename, pH='7', temp='298', bar='1'):
    f = open(filename, 'r')
    text=f.read()
    f.close()
    cond = cond_temp.replace('$pH', str(pH))
    cond = cond.replace('$temperature', str(temp))
    cond = cond.replace('$bar', str(bar))
    text = cond + text
    f = open(filename, 'w')
    f.write(text)
    f.close()

# add, header, DSS and mol residue information
add_shifts_header(chespi_star)
add_dss(chespi_star)
add_mol_seq(chespi_star, sequence)
add_condition(chespi_star, pH=str(pH), temp=str(temperature), bar=str(atm))
add_physical_state(chespi_star, physical_state)

import time
from numpy import *
import operator
from pylab import *
from random import choice as randchoice
from random import lognormvariate, normalvariate, randint, uniform, random
from numpy.random import rand
from numpy.random import random_integers
from scipy.special import erfc
from scipy.optimize import curve_fit
from scipy.interpolate import RectBivariateSpline
import numpy as np
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

VERB=False #change this to True for verbose logfile POTENCI
PLOT12=True

def initfil2(filename):
    fil=open(filename,'r')
    buf=fil.readlines()
    fil.close()
    for i in range(len(buf)):
        buf[i]=buf[i].split()
    return buf

def initfil(filename):
    fil=open(filename,'r')
    buf=fil.readlines()
    fil.close()
    return buf

aa3s=list(aa31dict.keys());aa3s.sort()#introduce ordering
##aa1s=aa13dict.keys();aa1s.sort()
aa3s=['ALA','ARG' ,'ASP' ,'ASN' ,'CYS' ,'GLU' ,'GLN' ,'GLY' ,'HIS' ,'ILE' ,'LEU' ,'LYS' ,'MET' ,'PHE' ,'PRO' ,'SER' ,'THR' ,'TRP' ,'TYR' ,'VAL']
aa1s3=[aa31dict[k] for k in aa3s]

def visSS8max(segm,mini,maxi):
    cols={'H':'r','G':'m','T':'g','E':'b','S':'k','-':'0.5'}
    ax=plt.gca()
    for ss in '-STGHEB':
        if ss in segm:
            for ind in segm[ss]:
                wid=segm[ss][ind]
                first=ind
                last=ind+wid
                if ss in 'EB':
                    arrow = mpatches.Arrow(first, 0.5, wid, 0.0, width=1.5,color='b')
                    ##arrow = mpatches.FancyArrow(first, 0.5, wid, 0.0, width=0.5,color='b',length_includes_head=True,shape='full')
                    ##arrow = mpatches.FancyBboxPatch((first, 0.5), wid, 0.0, boxstyle='rarrow',color='b',mutation_aspect=0.5)
                    ax.add_patch(arrow)
                elif ss in 'GH':
                    if ss=='H':tn=3.6
                    else:tn=3.0
                    n_turns = int(round((last - first)/tn*2,0))/2.0
                    x_val = linspace(0, n_turns * 2*pi, 100)
                    y_val = (-0.4*sin(x_val) + 1) / 2
                    lw=3.0
                elif ss=='T':
                    n_turns = 0.5
                    x_val = linspace(0, n_turns * 2*pi, 100)
                    y_val = (0.3*sin(x_val) + 1) / 2
                    lw=2.0
                if ss in 'GHT':
                    x_val *= (last-first) / (n_turns * 2*pi)
                    x_val += first
                    plot(x_val, y_val, linewidth=lw, c=cols[ss])
                if ss in '-S':
                    if ss=='S':lw=2.0
                    else:lw=1.5
                    x_val = array((first,last))
                    y_val = ones(2)*0.5
                    plot(x_val, y_val, linewidth=lw, c=cols[ss])
        ax.set_ylim(0,1)
        ax.set_xlim(mini,maxi)


class Population(list):

    def __init__(self):
        list.__init__(self)
        print('initializing population')
        self.splitlib=[]

    def append(self,val):
        list.append(self,val)

    def mergewithchildren(self):
        for child in self.children:self.append(child)
        del self.children

    def fill_from_random(self,num,cls):
        for i in range(num):
            obj=cls.initialize_random(self.envi)
            ##print 'random:',obj,obj.energy
            self.append(obj)

    def sort(self,attr):
        list.sort(self,key=operator.attrgetter(attr))
        ##for i,val in enumerate(self):val.rank=i

    def getbest(self):
        self.sort('energy')
        return self[0]

    def get_clone(self,obj):
        return obj.clone(self)

    def selectNormal(self,selrat,size):
        if selrat>1.0:return randint(0,size-1)
        i=99999
        while i>size-1:
            i=int(abs(normalvariate(0,selrat))*size)
        return i

    def mergewith_FAIL(self,other):#dont use!
        incommon=0
        for id in other.iddct:
            if not id in self.iddct:
                self.append(other.iddct[id])
            else:incommon+=1
        print('individuals in common:',incommon)

    def mergewith(self,other):
        incommon=0
        dct={}
        for obj in self:dct[obj.getid()]=obj
        for obj in other:
            id=obj.getid()
            if not id in dct:
                self.append(obj)
                dct[id]=obj
            else:incommon+=1
        print('individuals in common:',incommon)

    def cull(self,num):
        if num<=0:
            print('note: population size is < 100:',100+num)
            return
        for i in range(len(self)-num):self.pop(-1)

    def getspread(self):
        tot=0.0
        N=len(self)
        for i in range(N):
            obji=self[i]
            for j in range(i+1,N):
                objj=self[j]
                tot+=obji.calc_distance(objj)
        return tot/(N**2-0.5*N)

    def derive_stats(self,cnt):
        eners=array([obj.energy for obj in self])
        ##genestd=self.getspread()
        genestd=self[0].getspread_simple(self)
        print('average energy: %9.3f %9.3f %8.4f %7.4f %4d %3d'%(average(eners),min(eners),std(eners),genestd,cnt,len(eners)), end=' ')
        print(self[0].getid())

    def breed(self,limitfac=100.0,expandfac=1.0,temperature=1.0,probs=(0.4,0.4,0.2),
              growthmode='replace',selrats=(0.5,2.0),sortnum=10):
        children=Population()
        cnt=0;numrep=0
        size=len(self)
        dct={}
        self.iddct=dct
        for obj in self:dct[obj.getid()]=obj
        print('breeding population',size,limitfac,temperature,growthmode)
        while cnt<size*limitfac and len(children)<size*expandfac:
            #find mates (only one in case of mutation)
            i=self.selectNormal(selrats[0],size)
            obji=self[i]
            ##print 'breeding object',i##,onum
            #find breeding operation - and breed mates
            rn=uniform(0.0,1.0)
            psum=0.0;onum=None
            for j in range(len(probs)):
                psum+=probs[j]
                if rn<psum:break
            prevener=obji.energy
            if j==0:
                #---mutation---
                child=obji.mutate()#consider multiple mutations?
                repi=i
            elif j==1:
                #---crossover---(reproduce)
                onum=i
                while onum==i:onum=self.selectNormal(selrats[1],size)
                objo=self[onum]
                prevenero=objo.energy
                child=obji.crossover(objo)
                if prevener>=prevenero:repi=i
                else:repi=onum
            elif j==2:
                #---multicrossover---(non-biological reproduction)
                onum=-1;repi=-1;objo=self[-1]
                child=objo.multicrossover(self,selrats[0],size)
            child.calculate_fitness(self.envi)
            #consider acceptance of child
            childid=child.getid()
            if childid in dct:
                pass##dct[childid]+=1
                ##print 'note child allready used',childid,dct[childid],cnt
                ##print 'note child allready used',childid,cnt
            else:
                childener=child.energy
                ptest=999
                if childener>prevener:
                    ptest=exp(-(childener-prevener)/temperature)
                    if repi==0:ptest=-999#to ensure that very best individual survives!
                if ptest>uniform(0.0,1.0):
                    print('breedinfo: using',j,i,onum,childener,prevener,ptest)
                    print(child,childener)
                    dct[childid]=child
                    numrep+=1
                    if growthmode=='append':children.append(child)
                    elif growthmode=='replace':
                        self[repi]=child
                        if numrep%sortnum==0:
                            self.sort('energy')
                            #below is only for diagnostics
                            self.derive_stats(cnt)
                ##else:print 'breedinfo: rejecting',j,i,onum,childener,prevener,ptest
            cnt+=1
        if growthmode=='append':self.children=children

    def multi_breed(self,pops,limitfac=100):
        print('merging populations',len(pops))
        ##for popul in pops:popul.breed() must be breed before
        merged=pops[0]
        for i in range(1,len(pops)):merged.mergewith(pops[i])
        merged.sort('energy')
        merged.derive_stats(-1)
        merged.cull(30)
        merged.breed(limitfac=limitfac)
        return merged


class Schema:

    def __init__(self,maxiter,population,environment):
        self.maxiter=maxiter
        self.population=population
        self.envi=environment

    def initializeall(self):
        for obj in self.population:
            obj.initialize(self.envi)
            obj.calculate_fitness()

    def tournament_selection(self,rounds=0):
        #TODO: implement diversity reward
        rounds=0
        pop=self.population
        i=randint(0,len(pop)-1)
        best=pop[i]
        bestener=best.energy
        cnt=0
        while cnt<rounds-0.1:
            if 0.1<rounds-cnt<0.99:
                if uniform(0.0,1.0)>rounds-cnt:break
                #else: complete final round
            i=randint(0,len(self.population)-1)
            cand=pop[i]
            ener=cand.energy
            ##ener+=pop.getdiversityreward(cand)
            if ener<bestener:
                bestener=ener
                best=cand
            cnt+=1
        return best,i

    def full_breed_evolve_steady_state(self,shift,pref):
        self.initialize_fullatom()
        pop=self.population
        pop.runanneals(frac=2.0,temp=15,numiter=25)
        pop.runoptimize(0.15,25)
        Np=len(pop)
        pop.evaluate(size=Np,divweight=5.0)
        ##pop.runmutations(self.envi,nummut=30)
        ##pop.runoptimize(0.05,10)
        ##sizes=[Np for _ in range(4)]
        sizes=[12,10,9,8]
        for i in range(len(sizes)):
            sr=[3.0,2.0,1.5,0.9,0.6][i]
            ss=[2.5,1.6,1.4,1.2,1.0][i]
            ts=[15.0,10.0,6.0,3.0,1.0]
            pop.breed(limitfac=16.0,temperature=ts[i],growthmode='replace',selrats=(sr,sr),stepstd=ss,
                      probs=(0.1,0.2-(i*0.04),0.8+(i*0.04)),nummut=30)##,forcefield=self.forcefield)
                      ##probs=(0.0,0.0,1.0),nummut=30)
            pop.runoptimize(0.12-i*0.02,25)
            pop.evaluate(size=sizes[i],divweight=3.5-i*0.5)
        pop.write('final'+pref+'_'+str(shift)+'_',writenum=8)

    def runmutate1(self,mutnum=0):
        so0=self.population[mutnum]
        so0.rstlst=self.envi.restrlstfg
        so0.stagnation=0
        so0.mutSCShistory=[]
        ##so0.initialize(self.envi)
        T0=time.time()
        f=3.0;cnt=0;T=20.0
        if so0.energy==None:so0.calculate_energy()
        fgener0=so0.energy
        so0.sched.usefg=False
        so0.rstlst=self.envi.restrlstcg
        so0.optimize(50,0.05)##WithReplace()#temperature, etc...
        so0.sched.usefg=True
        so0.rstlst=self.envi.restrlstfg
        so0.reinitializ_schedule()
        so0.calculate_energy()
        fgener1=so0.energy
        print('total time:',time.time()-T0)
        print('cmpeners',fgener0,fgener1,fgener0-fgener1)
        for i in range(self.maxiter):
            ##so0.mutate(self.envi,self.population)##WithReplace()#temperature, etc...
            so0.mutateSCS(f,T,useweights=so0.stagnation>2,size=10,fw=1.0)
            ##so0.mutateSCS(f,T,useweights=False,size=10,fw=1.0)
            cnt+=1
            f=3.0/ (1+cnt)
            T=20.0/(1+cnt)
        so0.calculate_fitness()
        print('total time:',time.time()-T0)
        ##so0.finalize_mutations()



class Environment:

    def __init__(self):
        pass


class GenericIndividual:

    def optimize(self):
        pass

    def calculate_fitness(self):
        pass

    def initialize(self):
        pass

    def mutate(self):
        pass

    def crossover(self,other):
        pass


debug=False

CORVALS6={'S3': ([0.019297, -0.094793, -0.083282, -0.068386, 0.090053, -0.104272, -0.085991, 0.005078, -0.013203, 0.104949, 0.092084, -0.131694, 0.063985, 0.105626, -0.019636, -0.03724, -0.022005, 0.063985, 0.026745, 0.089376, -0.102352, -0.049893, 0.087213, 0.19717, 0.154051, -0.080507, 0.023307, 0.381334, 0.078355, -0.1202, -0.242098, -0.043727, -0.013698, -0.078256, -0.10214, 0.026768, 0.024173, -0.021797, 0.003835, -0.121151, 0.230337, -0.03542, 0.038242, 0.085508, -0.479109, 0.058991, -0.199417, 0.755504, -0.28204, 0.001946, 0.459819, 0.091298, -0.155048, 0.051129, -0.09531, -0.091634, -0.102752, -0.251163, -0.154145, 0.070728, -0.845705, -0.145957, -0.204061, 0.340223, -0.867145, 0.162739, 0.109487, 0.235985, -0.243657, 0.273138, 0.836179, -0.191254, -0.267832, -0.705895, 0.230487, -0.818174, 1.548207, 0.544215, -0.338394, 0.347815, -1.429054, -0.055009, 0.265881, 0.741496, -0.160088, 0.275586, 0.330748, -0.924739, 0.175424, 0.580246, 0.90136, -0.082104, 0.179998, -0.57338, -0.574114, -0.975988, 1.494797, -0.3816, -0.609989, 0.824502, -1.169818, -0.443678, 0.165266, 0.461652, 0.177442, -0.230154, -0.129505, -0.07551, 0.293978, 0.42363, 0.45598, -0.487084, 0.105452, 0.146928, -0.77955, -0.156553, 0.872732, -0.012506, -0.259474, 0.644184, 0.117907, -0.002655, -0.064557, 0.006359, -0.031836, 0.123499, -0.027743, 0.283833, -0.030267, 0.030764, 0.069089, -0.048582, -0.242873, -0.176067, -0.046966, 0.153613, 0.103514, -0.253534, -0.097297, 0.132821, -0.012767, 0.062714, 0.055099, 0.045244, -0.059578, 0.068985, 0.056891, -0.00336, 0.008735, -0.069433, -0.060922, 0.087128, -0.042332, -0.069881, 0.012991, 0.024638, 0.014559, -0.042332, -0.017694, -0.05913, 0.005553, -0.027277, -0.023965, -0.019678, 0.025913, -0.030005, -0.024744, 0.001461, -0.003799, 0.030199, 0.026498, -0.037895, 0.018412, 0.030394, -0.00565, -0.010716, -0.006332, 0.018412, 0.007696, 0.025718], [-3.303419, -2.32803, -3.303419, -0.016556, 0.0, -1.264831, -1.324356, 0.844647, -0.407314, -1.139833, -0.407314, 0.815569, 0.0, -0.371819, -0.71221, 1.021171, 0.007454, 0.007454, 0.007454, 0.278549, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.813301, 4.148781, 1.813301, -0.513694, 0.0, 2.837482, -0.149075, -0.681484, -1.030215, -1.030215, -1.030215, -0.595953, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], {'E': -1.7158476121583721}), 'H3': ([0.016902, -0.083026, -0.072945, -0.059898, 0.078875, -0.091329, -0.075317, 0.004448, -0.011564, 0.091922, 0.080654, -0.115347, 0.056043, 0.092515, -0.017198, -0.032617, -0.019274, 0.056043, 0.023425, 0.078282, 0.068276, -0.027794, 0.379696, 0.284777, -0.06832, 0.062718, 0.02146, 0.156209, -0.140892, -0.340025, 0.029414, -0.003318, -0.042999, -0.100716, -0.362916, 0.152408, -0.109102, 0.363125, -0.004845, -0.318485, 0.432229, -0.195096, 1.025242, 0.866008, -0.282587, 0.075837, -0.080095, 1.496001, -0.255277, -1.428452, 0.130298, -0.20298, -0.036936, -0.177784, -0.487258, 0.657956, -0.088554, 0.233622, -0.300204, -1.387172, -0.158365, -0.527157, 0.913767, 0.938573, -0.002197, -0.185551, -0.281133, 1.139697, -0.237475, -1.407211, -0.468014, -0.713746, -0.431746, 0.375367, -0.106703, 0.8511, 0.692366, 0.658922, 0.129892, -1.182611, -0.341706, -0.655192, 0.833114, 1.083583, 0.021501, -0.306867, -0.395378, 1.015675, -0.372099, -1.180254, -0.464843, -0.912272, -0.294979, 0.566274, -0.725341, 0.67131, 1.498849, 0.652473, 0.498861, -1.194352, -0.567007, -0.320082, 0.111328, 0.020692, -0.1444, -0.243006, -0.27593, -0.659604, 0.231462, -0.237005, -0.715649, -0.414186, -0.271575, 0.524896, 0.938853, 0.196389, 1.013458, 0.530417, 0.431615, -0.149038, 0.287626, 0.151548, -0.266745, 0.1636, 0.180682, -0.072662, 0.082173, -0.039798, 0.297714, -0.387268, -0.037008, 0.212527, 0.27661, 0.33008, -1.579739, 0.519656, 0.371394, 0.004977, 0.027079, -0.524461, 0.14927, 0.171132, -0.601497, 0.034013, 0.001475, 0.004467, 0.259549, 0.313364, 0.102029, -0.130831, -0.168214, 0.147413, 0.149936, 0.005993, -0.9716, 0.678854, 0.504068, -0.150845, -0.134087, -0.366061, 0.152295, 0.040592, -0.402998, -0.046839, 0.142796, -0.055765, 0.041138, 0.009792, 0.090214, -0.019392, 0.023735, -0.0069, 0.145085, 0.210865, -0.613031, 0.349961, 0.233031, -0.0279, -0.074266, -0.192709], [-0.169048, -1.354317, 0.332187, 1.187221, 0.0, -1.210275, -1.395698, -1.315874, -1.324041, -2.154139, -5.121323, 0.525122, 0.0, -1.256065, -0.608352, 0.616314, 0.007494, 0.007494, 0.007494, -0.367024, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.473185, 1.129782, -0.418936, -0.545882, 0.0, 0.78871, -0.134299, -0.872918, 2.020503, 1.154101, 2.859188, -0.23951, 0.0, 1.177741, -0.109159, -0.578724, 1.237389, 0.418519, -4.168514, -0.477856, 0.0, 0.660119, -0.136622, -0.570944, 0.0, -0.504011, 3.949269, 0.0, 0.0, -0.212523, -0.253022, -0.186672], {'I': -0.43578376036291577, 'H': -4.2875265599317629, 'G': -2.6039052591824543}), 'C2': ([-0.011513, 0.056555, 0.049687, 0.0408, -0.053727, 0.06221, 0.051303, -0.00303, 0.007877, -0.062614, -0.054939, 0.078571, -0.038175, -0.063018, 0.011715, 0.022218, 0.013129, -0.038175, -0.015957, -0.053323, -0.001591, 0.007817, 0.006868, 0.005639, -0.007426, 0.008599, 0.007091, -0.000419, 0.001089, -0.008655, -0.007594, 0.01086, -0.005276, -0.00871, 0.001619, 0.003071, 0.001815, -0.005276, -0.002206, -0.00737, -0.069429, -0.183587, -0.071014, -0.232471, 0.450971, -0.074927, -0.364461, 0.218651, 0.002279, -0.210438, 0.04939, -0.266197, 0.047476, 0.459647, -0.474595, -0.113231, -0.411385, 1.070877, 0.418234, -0.245402, -0.311386, -0.372702, -0.01311, -0.253133, 0.800152, -0.01685, -0.282143, 0.675802, -0.216926, -0.405474, -0.233432, -0.530627, -0.071811, 0.697198, -0.861939, -0.055011, -0.25023, 1.380601, 0.72294, -0.401629, -0.250824, -0.155861, -0.202254, -0.221995, 0.662654, 0.084564, -0.234737, 0.255738, -0.203486, -0.351441, -0.287829, -0.357467, 0.137013, 0.6444, -0.427378, -0.012925, -0.086805, 0.790734, 0.507895, -0.289044, -0.288791, -0.107123, -0.308008, -0.232845, 0.76657, 0.041008, 0.072485, -0.00094, 0.278675, -0.121536, -0.433312, -0.082689, 0.164773, 0.396109, -0.422095, -0.031069, 0.086353, 0.246503, 0.278673, -0.301115, -0.057633, 0.131847, -0.209584, -0.038489, 0.283526, -0.037604, 0.025777, -0.428691, 0.348055, 0.088627, -0.002926, 0.114242, 0.207263, 0.251996, -0.26375, -0.233412, -0.124511, -0.016152, 0.00328, -0.040446, 0.071215, -0.004993, -0.023451, -0.047435, -0.020315, 0.05808, 0.026935, -0.070755, 0.018869, 0.020112, 0.04945, 0.014315, 0.086986, 0.026531, -0.090886, -0.04637, -0.035347, 0.005809, -0.050376, 0.011298, -0.01422, 0.069855, 0.061372, 0.050395, -0.066362, 0.07684, 0.063368, -0.003742, 0.00973, -0.077339, -0.067859, 0.097048, -0.047152, -0.077838, 0.01447, 0.027443, 0.016216, -0.047152, -0.019709, -0.065863], [-0.620416, -2.218624, -4.370647, 1.370144, 0.0, -0.837909, -0.585708, 1.331203, -2.257623, -2.353085, -1.774456, 0.806094, 0.0, -1.395036, -0.612215, 0.926923, -0.841501, 0.300464, 2.576216, 0.321511, 0.0, -0.208211, -0.015878, 0.395845, -0.187998, -0.187998, -0.187998, -0.399284, 0.0, 0.0, 0.0, 0.0, 2.541123, 1.993562, 0.161946, 0.512771, 0.0, 1.300772, 0.348045, 0.582803, 0.642463, 0.464591, 4.297175, 0.177106, 0.0, 0.510622, 0.263577, -0.119125, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], {'S': 0.043730941745910329, 'B': 1.7551649939745402, '-': 0.43127825832484107, 'T': 0.14224085606541886}), 'H2': ([0.053891, 0.210572, 0.158722, 0.005727, 0.136836, -0.116847, -0.052947, -0.077817, -0.480907, 0.56649, 0.401963, -0.055737, 0.403438, -0.515266, -0.404307, -0.12314, 0.13538, -0.488768, -0.196173, 0.440166, 0.098288, -0.002428, 0.080368, 0.070648, -0.367072, 0.117246, -0.01639, 0.011411, -0.221699, 0.153164, 0.234889, 0.083777, -0.146235, -0.06146, -0.493187, 0.058816, 0.103165, -0.01316, 0.066846, 0.241064, 0.056013, -0.295993, 0.379047, 0.112046, -0.099413, -0.011486, -0.319687, 0.452022, -0.429472, -0.329578, 0.191922, -0.218375, 0.134039, 0.712881, -0.811749, -0.169542, -0.323844, 0.997429, 0.345622, -0.373991, -0.425557, -0.500074, 0.170009, -0.077748, 0.200528, -0.208609, -0.453405, -0.170735, -0.061482, -0.392944, -0.289311, -0.723037, -0.338123, 1.446232, -1.149086, -0.165572, 0.110977, 2.324752, 1.326307, -0.623939, -0.489723, -0.556035, 0.35124, 0.486403, -0.056762, -0.313886, -0.449979, -0.152774, 0.255675, -0.520603, -0.442453, -0.768406, -0.337325, 1.462106, -1.394757, -0.19974, 0.231002, 2.397598, 1.383143, -0.885671, -0.461466, -0.101982, -0.160264, 0.005113, 0.048279, -0.253828, -0.433891, -0.609095, 0.214916, -0.267761, -0.610293, -0.385543, -0.385645, 0.837201, -0.198791, 0.139321, 0.493509, 1.7648, 0.902942, -0.536613, 0.117175, 0.056316, -0.516494, 0.049812, 0.496965, -0.065667, -0.091879, -0.009451, 0.117445, -0.255462, -0.007491, 0.074726, 0.09172, 0.749437, -1.731941, 0.335395, 0.049041, 0.698054, 0.313857, -0.472126, 0.06693, 0.062904, -0.883512, -0.120213, 0.28943, -0.111282, 0.126737, 0.376625, 0.162795, -0.017365, -0.051101, 0.062551, 0.310635, 0.419425, -1.48042, 0.482244, 0.388334, 0.173651, 0.091998, -0.351005, 0.085786, -0.107138, -0.511446, -0.081781, 0.334426, -0.170218, -0.02662, 0.090397, 0.093659, 0.076839, 0.072413, -0.059976, 0.27633, 0.484808, -0.782233, 0.136299, 0.162101, 0.040065, 0.035373, -0.148328], [-0.568022, -1.228166, -2.12798, 0.857818, 0.0, -1.039672, -1.264544, 1.222694, -1.574924, -2.726251, -3.49241, 0.518611, 0.0, -2.220848, -0.409316, 1.363355, -0.354565, -0.354565, -0.354565, 0.007024, 0.0, 0.0, 0.0, 0.0, 0.732379, 0.732379, 0.732379, 0.49283, 0.0, 0.0, 0.0, 0.0, 2.69116, 1.895308, 1.6825, -0.114174, 0.0, 1.438733, 0.389946, 1.153049, 2.351776, 1.59278, 1.034833, 0.438442, 0.0, 1.652219, 0.410843, 0.373064, 1.351246, 0.518379, -1.198268, -0.500413, 0.0, 1.051329, 0.092276, 0.234091, 0.297208, 0.297208, 0.297208, 0.16187, 0.0, 0.0, 0.0, 0.0], {'I': 3.6728441311871309, 'H': -1.4424616957371339, 'G': -0.62390277372380787}), 'S2': ([0.006481, -0.031836, -0.027971, -0.022968, 0.030245, -0.03502, -0.02888, 0.001706, -0.004434, 0.035247, 0.030927, -0.04423, 0.02149, 0.035475, -0.006595, -0.012507, -0.007391, 0.02149, 0.008982, 0.030017, -0.312594, 0.183356, -0.126925, -0.093, 0.337411, -0.444332, 0.065436, 0.092627, -0.105097, -0.222316, -0.101035, 0.01346, 0.009455, -0.007828, -0.467176, 0.203825, -0.05412, 0.848554, 0.404996, -0.222989, -0.135818, -0.104985, -0.415735, -0.105279, -0.257476, -0.324974, -0.078537, 0.065705, -0.763219, -0.191165, 0.31633, -0.279162, 0.101098, 0.740843, -0.960984, -0.018922, -0.328864, 2.005625, 0.891693, -0.156082, -0.339465, -0.297233, -0.241795, -0.14444, -0.40449, -0.49183, -0.326966, -0.361649, -0.685884, 0.240882, 0.464904, -0.445891, 0.067776, 1.046562, -1.600321, -0.732665, 0.272788, 2.977915, 1.196574, -0.194756, -0.263217, -0.112437, -0.342238, -0.537323, -0.051121, -0.435927, -0.212585, -1.719168, -0.219721, 0.606721, 0.624364, -0.057537, 0.510209, 1.314712, -2.179204, -0.953595, 0.363954, 2.317296, 1.263458, 0.084273, -0.418612, -0.055765, -0.475487, -0.45423, 0.331273, -0.573757, -0.166787, -1.413296, -0.016631, 0.634181, 0.283512, -0.086214, 0.589623, 1.031666, -1.053459, -0.379786, -0.03447, 1.103297, 0.830659, 0.328336, -0.049866, 0.219954, -0.222015, -0.230284, -0.343827, -0.30999, -0.030972, -0.68201, -0.115196, 0.249271, 0.180839, 0.183604, 0.238905, 0.315296, 0.144228, -0.112538, -0.01612, 0.2527, 0.167655, 0.161356, 0.022082, 0.22053, -0.372208, -0.216005, -0.122562, -0.215098, 0.063035, -0.317289, 0.081328, 0.180715, 0.038678, 0.1667, 0.23771, 0.129368, 0.026091, -0.092662, -0.029499, 0.061609, 0.005716, 0.132644, -0.017489, 0.085909, 0.075477, 0.061977, -0.081614, 0.0945, 0.077932, -0.004602, 0.011966, -0.095114, -0.083455, 0.119352, -0.057989, -0.095727, 0.017795, 0.03375, 0.019943, -0.057989, -0.024239, -0.081], [-1.765275, -2.111555, -1.765275, 0.838273, 0.0, -1.17632, -0.712087, 1.432711, -2.018762, -3.118377, -2.018762, 0.986857, 0.0, -1.377637, -0.99621, 0.335201, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.275746, 1.56442, 2.275746, 0.62496, 0.0, 1.495842, 0.480409, -0.053309, 0.994857, 0.298115, 0.994857, 0.20504, 0.0, 0.684797, 0.395525, 0.164271, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], {'E': 1.7353469890102504}), 'S1': ([0.003759, -0.018464, -0.016222, -0.01332, 0.017541, -0.02031, -0.016749, 0.000989, -0.002572, 0.020442, 0.017936, -0.025651, 0.012463, 0.020574, -0.003825, -0.007254, -0.004286, 0.012463, 0.005209, 0.017409, 0.105833, -0.045178, 0.166537, -0.032797, -0.246479, 0.292665, 0.119152, 0.014348, 0.011552, -0.126296, -0.162307, -0.003401, 0.155428, -0.0947, 0.524113, -0.095772, -0.046766, -0.167862, -0.226083, -0.143311, 0.088698, 0.134438, 0.134746, -0.099281, -0.535256, 0.303995, 0.228167, 0.047843, -0.081847, -0.071302, -0.280127, 0.186708, 0.043792, -0.257151, 0.683348, 0.011857, 0.144857, -0.421473, -0.252415, -0.011869, -0.889206, 0.151215, 0.379658, 0.477985, -0.952623, -0.028081, 0.125162, 1.485723, 0.325688, 0.012765, -0.954942, 0.180169, -0.591743, -0.510153, 1.193146, 0.303179, 0.291762, -0.688136, -0.466673, 0.153172, -1.312293, -0.100455, 0.688891, 0.885142, -0.803266, -0.339668, -0.258984, 1.891989, 0.204246, -0.061183, -1.041934, -0.226161, -0.663249, -0.448264, 2.762249, 0.21693, 0.234071, -1.116091, -0.67858, 0.168749, -0.710279, -0.213556, 0.678281, 0.56135, -0.637422, 0.002345, -0.068983, 1.284395, 0.267971, -0.370731, -0.865081, 0.067992, -0.846238, -0.635997, 2.544875, 0.360065, 0.385211, -0.948474, -0.881541, 0.025753, 0.22377, 0.023554, 0.236927, 0.056209, -0.335044, 0.133434, 0.109227, 0.267487, -0.1418, -0.263181, -0.332164, 0.102998, -0.230919, -0.483248, 1.358206, 0.350329, 0.211525, -0.716548, -0.441824, -0.130021, 0.132466, -0.024184, 0.36998, 0.292735, -0.078496, 0.20899, 0.068264, 0.387793, -0.052279, -0.399234, -0.226062, 0.106014, -0.2938, -0.397115, 0.589402, 0.27321, 0.06433, -0.424651, -0.292476, -0.306162, -0.070979, -0.078862, -0.04565, -0.00255, 0.105987, -0.165565, -0.110549, 0.092279, -0.035241, 0.069231, 0.021315, -0.13591, -0.050435, 0.061879, 0.095062, 0.024076, 0.024079, 0.050209, 0.086453, 0.066185], [1.296443, 1.57336, 1.296443, -1.444339, 0.0, 2.201076, 1.153357, 0.290709, -0.188015, 2.103762, -0.188015, -0.386847, 0.0, 0.713608, 0.25244, -0.170405, 1.450347, 0.437104, 1.450347, -0.123811, 0.0, 0.545148, -0.144264, -0.999612, 0.20134, 0.20134, 0.20134, 0.29245, 0.0, 0.0, 0.0, 0.0, 4.794824, 5.135499, 4.794824, -1.69814, 0.0, 2.548461, 1.467883, -0.191631, 0.350998, 0.350998, 0.350998, -0.819839, 0.0, 0.0, 0.0, 0.0, -0.084472, -0.084472, -0.084472, -0.01627, 0.0, 0.0, 0.0, 0.0, 0.205896, 0.205896, 0.205896, 0.46936, 0.0, 0.0, 0.0, 0.0], {'E': -5.9219104095682722}), 'H1': ([0.017031, 0.051095, 0.072339, -0.088944, -0.035706, 0.075669, 0.022786, -0.059481, -0.02955, -0.039307, -0.074265, -0.075268, -0.022913, -0.021082, 0.047528, 0.001599, -0.025678, 0.138807, 0.014411, 0.030388, -0.075236, 0.069022, -0.159461, -0.260538, -0.112775, 0.098074, 0.1139, 0.128628, 0.074889, 0.183093, -0.057416, 0.033818, 0.140781, -0.128689, -0.0586, -0.059489, 0.130768, -0.178779, -0.037052, 0.154239, -0.210008, 0.026868, -0.73665, -0.854465, -0.073073, -0.035793, 0.020652, -0.554005, 0.040314, 0.838486, 0.045112, 0.063236, 0.142367, 0.284481, -0.082631, -0.43572, 0.148818, 0.12228, 0.404597, 0.846106, -0.349442, 0.342585, -1.20954, -1.21563, 0.93597, -0.262294, 0.240567, -2.166636, 0.353777, 1.469947, -0.190774, 0.209423, 0.086138, 0.419722, -0.293075, -0.628836, 0.215707, -0.282495, 0.581154, 1.750341, -0.463491, 0.166051, -0.886156, -1.173658, 1.176084, -0.231968, 0.129561, -2.945353, 0.021377, 1.427869, -0.227082, 0.101642, -0.258151, 0.416593, 1.017873, -0.672322, 0.313489, -0.168414, 0.510016, 1.755578, -0.197635, 0.214712, -0.38891, -0.667086, 0.845649, -0.064954, 0.205525, -2.074377, -0.110372, 0.823993, -0.230721, 0.117781, -0.308548, 0.094613, 1.21813, -0.23567, 0.314195, -0.657567, -0.002121, 1.109933, 0.009891, -0.036252, -0.187451, -0.156133, 0.361397, -0.068243, -0.101829, -0.968412, -0.210364, 0.541349, 0.455727, 0.026588, -0.072189, 0.390666, -0.38644, -0.317169, -0.246264, 0.143229, 0.197947, 0.626662, 0.170819, 0.062853, -0.171708, -0.097707, 0.161934, -0.033718, 0.032111, -0.28738, 0.042295, 0.120963, 0.244928, 0.115684, 0.05066, 0.046744, -0.699233, 0.05448, -0.002876, 0.053844, -0.012145, 0.147344, 0.087971, -0.033279, -0.051289, -0.074708, 0.002631, 0.036923, 0.006204, -0.080366, 0.017994, 0.053713, 0.083914, -0.021654, 0.119178, 0.061335, -0.11082, -0.064439, -0.047269, 0.025284, -0.050507, 0.039], [4.038058, 2.772504, 4.449804, -0.384963, 0.0, 2.663041, 1.336909, -0.190261, 0.821741, 0.415391, -1.473309, 0.49438, 0.0, 0.662561, 0.26029, 0.192578, 0.246727, 0.246727, 0.246727, -0.009358, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 2.951545, 2.348245, 1.440757, -1.721506, 0.0, 2.027398, 0.258536, -1.357026, 1.842676, 1.509158, -0.671787, -0.320621, 0.0, 1.066915, 0.190608, 0.085043, 0.939906, 0.252484, -4.649888, 0.443972, 0.0, 0.880032, 0.383249, 0.82022, 0.287387, 0.115121, 3.500917, -0.271279, 0.0, 0.416463, -0.02441, 0.181315], {'I': 1.631761050317559, 'H': -0.20266170750306003, 'G': -0.04727467326743362}), 'C1': ([-0.015394, 0.07562, 0.066438, 0.054554, -0.071839, 0.083182, 0.068598, -0.004051, 0.010533, -0.083722, -0.07346, 0.105058, -0.051044, -0.084262, 0.015664, 0.029708, 0.017555, -0.051044, -0.021336, -0.071299, -0.007596, 0.037312, 0.032781, 0.026918, -0.035447, 0.041043, 0.033847, -0.001999, 0.005197, -0.04131, -0.036246, 0.051837, -0.025186, -0.041576, 0.007729, 0.014658, 0.008662, -0.025186, -0.010527, -0.03518, -0.063036, 0.049698, -0.047798, -0.165288, 0.031789, 0.055527, 0.080633, -0.339358, 0.065787, 0.13215, -0.109262, -0.025672, 0.078777, 0.036867, 0.017689, -0.030938, 0.101907, -0.030422, 0.041158, 0.12, -0.046749, 0.244909, -0.116223, 0.03073, 0.111395, 0.093773, 0.200335, -0.579402, 0.351403, 0.168917, -0.202084, 0.344402, -0.062488, -0.133672, 0.159322, 0.108495, 0.343798, -0.878996, -0.216614, 0.079492, -0.081116, 0.148644, -0.068493, 0.046116, -0.332684, 0.174208, 0.319966, -0.744681, 0.403546, 0.147273, 0.056553, 0.262408, -0.354054, -0.014651, 0.334494, 0.036166, 0.124067, -0.475516, -0.219724, 0.237181, -0.108485, 0.205527, 0.171707, 0.121125, -0.596519, 0.260578, 0.422689, -0.295089, 0.324511, -0.234685, -0.150712, 0.236616, -0.260482, -0.247293, 0.451803, 0.183401, 0.277392, -0.537166, -0.307948, 0.080869, 0.005012, -0.011833, 0.048475, 0.078813, -0.216644, -0.006694, 0.046703, -0.185226, 0.017384, 0.051314, 0.004401, 0.06953, 0.072302, -0.104543, 0.614752, 0.082092, 0.155763, -0.449025, -0.199635, -0.072544, -0.02132, -0.020752, -0.006945, 0.005364, 0.03072, -0.045645, -0.028029, 0.033574, -0.009824, 0.01316, -0.003469, -0.03538, -0.020898, 0.008264, 0.033473, 0.013866, 0.011581, 0.006171, 0.021758, 0.014608, 0.077772, 0.096574, -0.190793, 0.054505, 0.146039, -0.257947, -0.065042, 0.002225, 0.051043, -0.022028, 0.132507, 0.113453, -0.039149, 0.023216, -0.124319, 0.098196, -0.060908, 0.014516, -0.025664, -0.02307], [2.093946, 1.198701, 2.471223, -1.849251, 0.0, 1.555381, 0.694143, -1.674472, 1.087839, 1.014636, 1.389677, -0.667612, 0.0, 0.514959, 0.116431, -0.661216, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 3.297104, 2.63113, -0.151369, -2.173729, 0.0, 1.624755, 0.800817, -1.932933, 0.110641, 0.416232, 1.301578, -0.688812, 0.0, 0.558761, 0.251317, -0.940482, -0.218471, -0.296236, 0.069338, -0.431974, 0.0, -0.343009, -0.086612, -0.539977, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0], {'S': -0.76867475295761878, 'B': -3.6800701434993641, '-': -1.7534436965186453, 'T': 0.51994034394359812}), 'C3': ([-0.01358, 0.066711, 0.05861, 0.048127, -0.063375, 0.073382, 0.060516, -0.003574, 0.009292, -0.073858, -0.064805, 0.09268, -0.04503, -0.074335, 0.013819, 0.026208, 0.015486, -0.04503, -0.018822, -0.062899, 0.157626, -0.028872, 0.024623, 0.154616, -0.122028, 0.013447, 0.126714, 0.12675, -0.059952, -0.242948, -0.029283, 0.157758, 0.12048, -0.217961, -0.008447, 0.08367, -0.156421, 0.229774, -0.102359, -0.227667, 0.193014, -0.127227, 0.268292, 0.217053, 0.179447, 0.058184, 0.113688, 0.594422, -0.140355, -0.53371, -0.072686, -0.006329, -0.042972, -0.366099, -0.210114, 0.303601, -0.142105, 0.313616, -0.157675, -0.443203, -0.066303, -0.283844, 0.343003, 0.394526, 0.173943, -0.003257, 0.05773, 1.388811, -0.152793, -0.497575, -0.271928, -0.311122, -0.124239, -0.51925, -0.233288, 0.191564, -0.13758, 0.426298, -0.017027, -0.35867, -0.057771, -0.34284, 0.196352, 0.254201, -0.475032, 0.146641, -0.124946, 1.181146, -0.061944, -0.400732, -0.204686, -0.228107, -0.01399, -0.064517, 0.158763, 0.156986, -0.411093, 0.481945, -0.155355, -0.037516, -0.232973, -0.06048, 0.011917, 0.308685, -0.052535, 0.146091, 0.162202, 0.554023, 0.102752, -0.130564, -0.510288, -0.022423, -0.169576, -0.399666, 0.130154, 0.06993, 0.097847, -0.020514, 0.093832, -0.078574, -0.085287, 0.161906, -0.033471, 0.310127, -0.054548, 0.058614, 0.153987, -0.231733, 0.112381, -0.038922, -0.223307, 0.026776, -0.050397, 0.188764, -0.173008, -0.066302, 0.082301, -0.103682, 0.026262, -0.060118, 0.007411, -0.036403, -0.031983, -0.026262, 0.034583, -0.040043, -0.033023, 0.00195, -0.00507, 0.040303, 0.035363, -0.050574, 0.024572, 0.040563, -0.007541, -0.014301, -0.008451, 0.024572, 0.010271, 0.034323, -0.010617, 0.052153, 0.04582, 0.037625, -0.049545, 0.057368, 0.04731, -0.002794, 0.007264, -0.057741, -0.050663, 0.072455, -0.035203, -0.058113, 0.010803, 0.020489, 0.012107, -0.035203, -0.014715, -0.049173], [-1.682374, -2.667147, -3.65282, 0.392675, 0.0, -1.056631, -0.820034, 0.346631, -2.090677, -1.786418, -1.264079, 0.647951, 0.0, -1.315875, -0.644846, 0.568705, -0.82573, 0.568651, 1.749435, 0.007364, 0.0, -0.226907, -0.057752, 0.352672, -0.291729, -0.291729, -0.291729, -0.567364, 0.0, 0.0, 0.0, 0.0, 1.763447, 1.359592, 0.387768, -0.880739, 0.0, 0.617453, -0.093232, -0.864193, -0.046581, -0.000491, 2.914719, -0.243511, 0.0, 0.267809, 0.080352, -0.893181, -0.186544, 0.184376, 0.635293, -0.29657, 0.0, -0.200325, 0.046413, -0.808526, -0.427351, -0.427351, -0.427351, -0.304478, 0.0, 0.0, 0.0, 0.0], {'S': -1.2711633183073912, 'B': -0.39322404566068681, '-': -0.3108707306825868, 'T': -0.88741012687103238})}

def choose_random_consecutive(numelem,p=0.2):
    ##first=random.random_integers(0,1)
    first=random_integers(0,1)
    lst=[]
    app=lst.append
    for i in range(numelem):
        if rand()<p:
            other=1-first
            app(other)
            first=other
        else:
            app(first)
    return lst
    ##print ''.join([str(x) for x in lst])
    #takes ca. 0.03 ms for numelem==100

def shannon(p):
    z=p==0
    c=p*log(p)
    c[z]=0.0
    return sum(c)

def getramp(buf):
    dct={}
    for i in range(64):
        for j in range(4):
            rgb=[float(x)/255 for x in buf[i][4*j+1:4*j+4]]
            dct[i+j*64]=rgb
    return dct

def getColor(f,ramp):
    return ramp[int(255*f)]

def calc_corr(P):
    ap0=average(P[:,0])
    ap1=average(P[:,1])
    std0=std(P[:,0])
    std1=std(P[:,1])
    return average((P[:,0]-ap0)*(P[:,1]-ap1))/std0/std1

def getobsfromzfile(bmrid,pref):
    buf=initfil2('CheZOD%s/zscores%s.txt'%(pref,bmrid))
    resis  =array([eval(lin[1]) for lin in buf])
    zscores=array([eval(lin[2]) for lin in buf])
    pc1sobs=array([eval(lin[3]) for lin in buf])
    pc2sobs=array([eval(lin[4]) for lin in buf])
    ##return resis,pc1sobs,pc2sobs
    return resis,pc1sobs,pc2sobs,zscores

def getpcdata(bmrid,selpcnum,selss,seq,sec,pref,minnumsh=12.5,return3=False):
    conv={'H':'H', 'S':'E', 'C':'-', 'U':'-'}
    conv4={'H':'H', 'S':'S', 'C':'C', 'U':'C'}
    conv8to3={'G':'H', 'H':'H', 'I':'H', 'E':'S', 'B':'C','T':'C', 'S':'C', '-':'C','U':'U'}
    dat=[]
    pref14='7hits14'
    ##xseq=['n','n','n','n']+list(seq)+['c','c','c','c']
    xseq=['G','G','G','G']+list(seq)+['G','G','G','G']
    xsec=['-','-','-','-']+[conv[x] for x in sec]+['-','-','-','-']
    xse4=['C','C','C','C']+[conv4[x] for x in sec]+['C','C','C','C']
    buf=initfil2('CheZOD%s/zscores%s.txt'%(pref,bmrid))
    buf14=initfil2('CheZOD%s/zscores%s.txt'%(pref14,bmrid))
    zscores=[eval(lin[2]) for lin in buf]
    for lin in buf:
        resi=int(lin[1])
        ##ss8=lin[8]
        ss8=lin[6]
        if not ss8 in 'UZ_':xsec[resi+3]=ss8
        ss4=lin[7]
        if not ss4 in 'UZ_':xse4[resi+3]=ss4
        #zsco=lin[2]
    ##if return3: return xseq[4:],xsec[4:],xse4[4:]
    if return3: return xseq[4:-4],xsec[4:-4],xse4[4:-4]
    first=int(buf[0][1])
    for i,lin in enumerate(buf):
        ##ss4=lin[7]
        ss4=conv8to3[lin[6]]
        if ss4 in 'UZ_':ss4='C' #TAKEBACK if training again!
        # "_" means no shift data for center residue and DSSP might be different from coil
        ##auth,hb,rsa,cistrans,phi,psi,numsh=lin[9:]
        numsh='999'
        if ss4 == selss and eval(numsh)>minnumsh:
            lin14=buf14[i]
            resn=lin[0]
            resi=int(lin[1])
            ##zsco=eval(lin[2])
            ##zsco=lin[2]
            zsco=lin14[2]
            ##pcs=[eval(x) for x in lin[3:6]]
            pcs=[eval(x) for x in lin14[3:6]]
            ss8=lin[8]
            if ss8 in 'UZ_':ss8='-'
            seqsegm=''.join(xseq[resi-1:resi+8])
            secsegm=''.join(xsec[resi-1:resi+8])
            se4segm=''.join(xse4[resi-1:resi+8])
            dat.append((bmrid,pcs[selpcnum],seqsegm,secsegm,se4segm,resi,zsco))
            ##print 'data: %5s %7.3f %9s %9s %9s %3d'%dat[-1][:-1],resn,ss8,ss4,se4segm[4],
    if debug:print('found pcs:',bmrid,selss,selpcnum,len(dat))
    return dat

subss8={'H':'HGI','S':'E','C':'-TSB'}


def avenscorr(params,probs,numres):
    pari=params[0]
    ##print pari['H'][1][0,1,0],probs[0,5]
    #probability weighted sum of N in windows of +-4
    #TODO same prob weighted sum for A
    X=array([[[[[[params[pc][ss][1][direc,k,j]*probs[j,n] for j in range(8)] for n in range(numres)] for k in range(4)] for direc in (0,1)] for ss in 'HSC'] for pc in (0,1)])
    if debug:print(X.shape)
    if False:
    ##for ss in 'HSC':
        N=pari[ss][1]
        for n in range(numres):
            for direc in (0,1):
                for k in range(4):
                    sndk=sum([N[direc,k,j]*probs[j,n] for j in range(8)])
    A=sum(X,axis=(2,3,5))
    if debug:print(A.shape)
    return A #returns ANS
    imshow(A,interpolation='none',cmap=cm.RdBu,vmax=9,vmin=-9)
    show(block=False);1/0
    1/0

def writepredout(bmrid,resis,seq,pc1s,pc2s):
    out=open('predpcsnew%s.txt'%bmrid,'w')
    if debug:print([len(x) for x in (resis,seq,pc1s,pc2s)])
    if debug:print([x[0] for x in (resis,seq,pc1s,pc2s)])
    for i,ri in enumerate(resis):
        aai=seq[int(ri)-1]
        out.write('%3d %1s %7.3f %7.3f\n'%(ri,aai,pc1s[i],pc2s[i]))
    out.close()

def init_corvals():
    ##corvals=eval(open('corvals6.txt','r').readline())
    corvals=CORVALS6
    ##corvals=eval(open('corvals.txt','r').readline())
    params=[{},{},{}]
    ss3s='HSC'
    allss8='HGIE-TSB'
    gnums=(0,3,4)
    for sellab in corvals:
        ss=sellab[0]
        pcnum=int(sellab[1])-1
        aar,ssr,dct8=corvals[sellab]
        A=array(aar).reshape((9,20))
        N=array(ssr).reshape((2,4,8))
        ##print ss,pcnum,average(A),average(N),std(A),std(N)
        if not 'D0' in params[pcnum]:params[pcnum]['D0']=dct8
        else:params[pcnum]['D0'].update(dct8)
        params[pcnum][ss]=A,N
    Hs=([0.8896,0.1104,0.0001],'HGI')
    Cs=([0.5621,0.2402,0.1736,0.0241],'-TSB')
    ssprobs={'H':Hs,'C':Cs}
    for pcnum in range(3):
        params[pcnum]['NS']=[]
        ##print pcnum,params[pcnum]['D0']
        for i,ss in enumerate(ss3s):
            A,N=params[pcnum][ss]
            if True:
                refval=params[pcnum]['D0'][allss8[gnums[i]]]
                nsum=sum(sum(N,axis=1),axis=0)
                if ss=='S':gsnsum=nsum[gnums[i]]
                else:
                    probs,labs=ssprobs[ss]
                    gsnsum=average([nsum[gnums[i]+k] for k in range(len(probs))],weights=probs)
                ##print 'gsnsum',pcnum,ss,refval,gsnsum,gsnsum+refval
                params[pcnum]['NS'].append(gsnsum)
            if False:
                subplot(331+pcnum*3+i)
                title('%s%s %8.4f'%(ss,pcnum+1,gsnsum+refval))
                ##imshow(hstack((N[0,:,:],N[1,:,:])),interpolation='none',cmap=cm.RdBu,vmax=5,vmin=-5)
                imshow(vstack((N[0,list(range(3,-1,-1)),:],N[1,:,:])),interpolation='none',cmap=cm.RdBu,vmax=5,vmin=-5)
                ##xticks(arange(16),allss8+allss8)
                xticks(arange(8),allss8)
                ##yticks(arange(4),'0123')
                yticks(arange(8),['i-4','i-3','i-2','i-1','i+1','i+2','i+3','i+4'])
            if False:
                subplot(331+pcnum*3+i)
                title('%s%s %8.4f'%(ss,pcnum+1,std(A)))
                imshow(A,interpolation='none',cmap=cm.RdBu,vmax=2,vmin=-2)
                xticks(arange(20),aa1s3)
                yticks(arange(0,9,2),arange(0,9,2)-4)
    ##show();1/0
    return params

def updateparamswithseq(params,seq):
    subss8={'H':'HGI','S':'E','C':'-TSB'}
    indss3={'H':[0,1,2],'S':[3],'C':[4,5,6,7]}
    indss8={'G':1,'I':2,'T':5,'S':6,'B':7}
    allss8='HGIE-TSB'
    ss3s='HSC'
    ##numres=len(seq)-4;print numres
    numres=len(seq)
    if debug:
        print(numres)
        print(''.join(seq))
    s8mats=[]
    seq4=seq+['G','G','G','G']
    for pcnum in range(3):
        S=zeros((3,numres))
        S8=zeros((8,numres))
        for i,ss in enumerate(ss3s):
            A,N=params[pcnum][ss]
            for n in range(numres):
                    ##cgn=sum([A[k+4][aa1s3.index(seq[n+k])] for k in range(-4,5)])
                cgn=sum([A[k+4][aa1s3.index(seq4[n+k])] for k in range(-4,5)])
                ##print i,n,pcnum,ss,cgn
                S[i,n]=cgn
                for j in indss3[ss]:
                    S8[j,n]=cgn+params[pcnum]['D0'][allss8[j]]
            ##if pcnum==0:##imshow(S,interpolation='none',cmap=cm.RdBu,vmax=2,vmin=-2)
            if False:
                subplot(311+pcnum)
                imshow(S8[:,:100],interpolation='none',cmap=cm.RdBu,vmax=5,vmin=-5)
                xticks(arange(100),seq[:100])
                yticks(arange(8),allss8)
        params[pcnum]['S8']=S8
        s8mats.append(S8)
    ##show();1/0
    ##return s8mats

def read_priors(name):
    buf=initfil2(name)[2:]
    #probabilities are in the order of H G I E B T S L(loops), the 8 secondary structure types used in DSSP
    ##cols=[x for x in 'rmwbcgk']+['0.5']
    cols=['r','m','w','g','k','0.5','c','b']
    priors=[]
    for lin in buf:
        resi=eval(lin[0])
        ##fracs=[eval(x) for x in lin[3:]]
        ##fracs=[eval(lin[3+i]) for i in (0,1,2,5,6,7,4,3)] for visuals
        fracs=[eval(lin[3+i]) for i in (0,1,2,3,7,5,6,4)]
        priors.append(fracs)
        ##acum=cumsum([0.0]+fracs)
        ##[bar(resi,fracs[i],bottom=acum[i],color=cols[i],edgecolor=cols[i]) for i in range(8)]
    ##axis([0,resi,0,1])
    ##show()
    return array(priors).transpose()

def visprobs3(S,mini=1,maxi=None):
    allss8='HGIE-TSB'
    cols=['r','m','w','g','k','0.5','c','b']
    reord=[0,1,2,5,6,4,7,3]
    if maxi==None:maxi=len(S[0])-1
    for n in range(len(S[0])):
        if maxi>=n>=mini-1:
            fracs=S[:,n][reord]
            acum=cumsum([0.0]+list(fracs))##*10.0
            ##[bar(n,fracs[i]*10.0,bottom=acum[i],color=cols[i],edgecolor=cols[i]) for i in range(8)]
            [bar(n+0.5,fracs[i]*1.0,bottom=acum[i],color=cols[i],width=1.0,edgecolor=cols[i]) for i in range(8)]
    ##axis([0,len(S[0]),0,1.0])##10])
    axis([mini,maxi,0,1.0])##10])

def visprobs2(S):
    allss8='HGIE-TSB'
    cols=['r','m','w','g','k','0.5','c','b']
    reord=[0,1,2,5,6,4,7,3]
    for n in range(len(S)):
        i=reord.index(allss8.index(S[n]))
        bar(n,10.0,color=cols[i],edgecolor=cols[i])
    axis([0,len(S),0,10])

def evaluatess83(probs,seq,s8,s3,post0,printstrs=True):
    print(''.join(seq))
    ss8to3ind={'H':0,'G':0,'I':0,'E':1,'-':2,'T':2,'S':2,'B':2}
    ss3s='HSC'
    numres=len(s8)
    allss8='HGIE-TSB'
    preds8=[allss8[probs[:,n].argmax()] for n in range(numres)]
    post8 =[post0[:,n].max() for n in range(len(post0[0]))]
    preds3=[ss3s[ss8to3ind[sx]] for sx in preds8]
    if printstrs:
        print(''.join(s8))
        print(''.join(preds8))
        print(''.join(s3))
        print(''.join(preds3))
    trueprobs=average([probs[allss8.index(sx)] for sx in s8])
    Q8=sum(array(preds8)==array(s8))*1.0/numres
    Q3=sum(array(preds3)==array(s3))*1.0/numres
    print('evaluation (probs): %6.4f %6.4f %6.4f'%(Q3,Q8,trueprobs),average(post8))
    return preds8,preds3

def guesss8s(params,resis,pcsobs,priors,ssigs,s8obs=None,ANS=None,dovis=False):
    ss3s='HSC'
    allss8='HGIE-TSB'
    ss8to3ind={'H':0,'G':0,'I':0,'E':1,'-':2,'T':2,'S':2,'B':2}
    ru=array(resis-1,dtype=int)
    inds3=array([0,0,0,1,2,2,2,2])
    sig=array([[[ssigs[pcnum,i] for n in range(len(ru))] for i in range(8)] for pcnum in (0,1)])
    #first derive the predicted shPCs using sum approx
    if ANS==None:preds=[array([params[pcnum]['S8'][i]+params[pcnum]['NS'][ss8to3ind[allss8[i]]] for i in range(8)]) for pcnum in (0,1)]
    else:        preds=array([[params[pcnum]['S8'][i]+         ANS[pcnum][ss8to3ind[allss8[i]]] for i in range(8)]  for pcnum in (0,1)])
    #keep those with observed shPCs
    preds=[prp[:,ru] for prp in preds]
    #derive the likelihood
    dev=array([preds[pc]-pcsobs[pc] for pc in (0,1)])##/3.0
    dev/=sig
    probs=exp(-0.5*(array(dev)**2))/sig#skip the normconstant but remember prop to inv sig
    probs0=probs[0]*probs[1]
    ##print 'testliks',list(probs0[:,6])
    #prior probability from RaptorX
    priors0=priors[:,ru]
    #posterior probability using Bayes
    if debug:print(priors0.shape,probs0.shape)
    post0=priors0*probs0
    #best (quick) guess is the maxpost selection
    maxprobs=[post0[:,n].max() for n in range(len(post0[0]))]
    maxlik=[probs0[:,n].max() for n in range(len(probs0[0]))]
    maxposs=[post0[:,n].argmax() for n in range(len(post0[0]))]
    ##pc1pred=[preds[0][maxposs[n],n] for n in range(len(probs0[0]))]
    if False:
        plot(ru,zeros(len(ru)),'k--')
        plot(ru,pc1pred,'g')##;show();1/0
    ##plot(arange(len(maxlik)),maxlik,'g')
    ##print 'avepost:',average(maxprobs),len(maxprobs)
    if debug:print('avepost:',average(maxprobs),average(log(maxprobs)),len(maxprobs))
    if debug:print('avelik:',average(maxlik),len(maxlik))
    #normalize post
    post=post0/sum(post0,axis=0)
    maxprobsnorm=[post[:,n].max() for n in range(len(post[0]))]
    if debug:print('avepostnorm:',average(maxprobsnorm),exp(average(log(maxprobsnorm))),len(maxprobs))
    ##print 'test_post',list(post[:,7])
    newpri=priors.copy()
    newpri[:,ru]=post
    ##plot(arange(len(maxprobs)),maxprobs,'r')
    if dovis:
        ##imshow(vstack((ANS[0],ANS[1])),interpolation='none',cmap=cm.RdBu,vmax=9,vmin=-9)
        ##show();1/0
        s8obsr=array(s8obs)[ru]
        obsinds=[allss8.index(j) for j in s8obsr]
        subplot(411)
        imshow(probs0,interpolation='none',cmap=cm.hot_r)
        subplot(412)
        imshow(priors0,interpolation='none',cmap=cm.hot_r)
        subplot(413)
        imshow(post,interpolation='none',cmap=cm.hot_r)
        scatter(arange(len(probs0[0])),array(obsinds),alpha=0.5)
        axis([0,len(probs0[0]),0,8])
        subplot(414)
        visprobs(newpri)
        show(block=False);1/0
    return newpri,post0

def getmaxss(pri):
    ss3s='HSC'
    allss8='HGIE-TSB'
    ss8to3ind={'H':0,'G':0,'I':0,'E':1,'-':2,'T':2,'S':2,'B':2}
    ss8ind=[pri[:,n].argmax() for n in range(len(pri[0]))]
    ss8=[allss8[i] for i in ss8ind]
    ss3=[ss3s[ss8to3ind[s8]] for s8 in ss8]
    if debug:print('ss8max:',''.join(ss8))
    if debug:print('ss3max:',''.join(ss3))
    ##ss8+=['-','-','-','-']
    ##ss3+=['C','C','C','C']
    ##ss8indsmax=[allss8.index(ss8m) for ss8m in ss8]
    return ss8,ss3

def selector(probs):
    prob=rand()
    cum=0
    for j,probj in enumerate(probs):
        cum+=probj
        if prob<cum:
            break
    return j

def fastselector(probs,makecum=True):
    allss8='HGIE-TSB'
    if makecum:probs=cumsum(probs)
    ##print probs
    gt = probs>rand()
    try:ind=list(gt).index(True)-1
    except ValueError:
        if debug:print('warning ValueError',probs,gt)
        return -1
    ##print ind,allss8[ind]
    return ind


class SSparameters(Environment):

    allss8='HGIE-TSB'
    ss8to3ind={'H':0,'G':0,'I':0,'E':1,'-':2,'T':2,'S':2,'B':2}
    ss8to3ind={'H':0,'G':0,'I':0,'E':1,'-':2,'T':2,'S':2,'B':2}
    ##ssigs=array((1.9706,3.6273,2.9360,2.9454,3.36407,3.2628)).reshape((2,3)) #H0 S0 C0 H1 S1 C1
    ssigs=array((2.110,3.071,0.0034,2.858,3.947,0.0219,3.897,3.337,0.1231,3.663,3.490,-0.3100,3.116,3.344,-0.2312,2.980,3.670,-0.1521,2.932,3.532,-0.1583,3.876,3.886,-0.3073)).reshape(8,3).transpose()[:2,:]
    ssigs*=1.1


    def __init__(self,bmrid):
        self.bmrid=bmrid
        return
        secbuf=initfil2('rungsshits.txt')
        secdct={}
        for lin in secbuf:secdct[lin[1]]=lin[2]
        seqbuf=initfil2('refseqshits.txt')
        seqdct={}
        for lin in seqbuf:seqdct[lin[1]]=lin[2]
        self.secdct=secdct
        self.seqdct=seqdct

    def init_priors_basic(self):
        aas='GPCTNSVWFHDYIMLKRQAE'
        ##fmat=initfil2('fracmat8.pck')
        ##fmat=eval(initfil('fracmat8.json')[0][:-1])
        fmat=[[0.14211076280041798, 0.034482758620689655, 0.00052246603970741907, 0.14263322884012539, 0.20585161964472309, 0.27795193312434691, 0.18652037617554859, 0.0099268547544409617], [0.15732217573221757, 0.057740585774058578, 0.0, 0.099581589958158995, 0.40083682008368199, 0.1790794979079498, 0.092887029288702933, 0.012552301255230125], [0.21404682274247491, 0.046822742474916385, 0.0, 0.32441471571906355, 0.23076923076923078, 0.096989966555183951, 0.073578595317725759, 0.013377926421404682], [0.23194444444444445, 0.036805555555555557, 0.00069444444444444447, 0.29375000000000001, 0.2298611111111111, 0.10208333333333333, 0.089583333333333334, 0.015277777777777777], [0.22014260249554368, 0.049910873440285206, 0.0, 0.1497326203208556, 0.25311942959001782, 0.19607843137254902, 0.11853832442067737, 0.012477718360071301], [0.24803664921465968, 0.06413612565445026, 0.0, 0.21269633507853403, 0.2349476439790576, 0.12172774869109948, 0.10471204188481675, 0.0137434554973822], [0.27904391328515843, 0.019455252918287938, 0.0, 0.44024458032240132, 0.14508060033351863, 0.054474708171206226, 0.047804335742078929, 0.013896609227348526], [0.36533333333333334, 0.066666666666666666, 0.0, 0.26933333333333331, 0.13600000000000001, 0.087999999999999995, 0.053333333333333337, 0.021333333333333333], [0.33893805309734515, 0.04247787610619469, 0.0, 0.30442477876106194, 0.16371681415929204, 0.070796460176991149, 0.068141592920353988, 0.011504424778761062], [0.30161579892280072, 0.052064631956912029, 0.0, 0.20825852782764812, 0.20287253141831238, 0.13824057450628366, 0.07899461400359066, 0.017953321364452424], [0.27330374128091312, 0.062143310082435003, 0.00063411540900443881, 0.11921369689283449, 0.25618262523779328, 0.15916296766011415, 0.11921369689283449, 0.010145846544071021], [0.33054393305439328, 0.039748953974895397, 0.0010460251046025104, 0.30439330543933052, 0.14644351464435146, 0.092050209205020925, 0.064853556485355651, 0.020920502092050208], [0.3210130047912389, 0.02190280629705681, 0.0, 0.3867214236824093, 0.1567419575633128, 0.045174537987679675, 0.052703627652292952, 0.015742642026009581], [0.42247191011235957, 0.024719101123595506, 0.0, 0.26292134831460673, 0.16629213483146069, 0.053932584269662923, 0.060674157303370786, 0.008988764044943821], [0.41263782866836302, 0.037319762510602206, 0.0, 0.26463104325699743, 0.15097540288379982, 0.066157760814249358, 0.056827820186598814, 0.011450381679389313], [0.38017651052274271, 0.04684317718940937, 0.0, 0.17107942973523421, 0.15953835709436523, 0.14460285132382891, 0.086218601493550581, 0.011541072640868975], [0.38118022328548645, 0.043859649122807015, 0.0, 0.21850079744816586, 0.16267942583732056, 0.098883572567783087, 0.081339712918660281, 0.013556618819776715], [0.449438202247191, 0.048314606741573035, 0.0, 0.15842696629213482, 0.16179775280898875, 0.094382022471910118, 0.07528089887640449, 0.012359550561797753], [0.47163912460920054, 0.04644930772666369, 0.0, 0.1866904868244752, 0.13443501563197857, 0.0933452434122376, 0.06163465832961143, 0.0058061634658329612], [0.44922118380062304, 0.058566978193146414, 0.00062305295950155766, 0.15015576323987539, 0.14080996884735203, 0.11775700934579439, 0.077258566978193152, 0.0056074766355140183]]
        pri=[]
        numres=len
        for i,aa in enumerate(self.seq):
            fracs=[fmat[aas.index(aa)][j] for j in range(8)]
            pri.append(array(fracs))
        return array(pri).transpose()

    def initparameters(self,usesimple=False,ss8pref=''):
        if usesimple:self.priors=self.init_priors_basic()
        else:
            try:self.priors=read_priors(ss8pref+self.bmrid+'.ss8') #TODO generalize path...
            except IOError:
                print('warning: ss8 prediction from sequence not found - using simple')
                self.priors=self.init_priors_basic()
        #priors from DeepCNF (RaptorXproperty, single sequence)
        for i,ires in enumerate(self.resis):
            if self.disordered[i]:
                if debug:print('isdisordered:',self.bmrid,ires,self.zscores[i],self.priors[-4,ires-1],self.priors[-2,ires-1])
                self.priors[:,ires-1]=[0,0,0,0.05,0.8,0,0.2,0]#none or bend (-/S)
        self.params=init_corvals()
        updateparamswithseq(self.params,self.seq)

    def set_observed(self):
        bmrid=self.bmrid
        seq=self.seqdct[bmrid]
        sec=self.secdct[bmrid]
        self.seq,self.s8obs,self.s3obs=getpcdata(bmrid,'','',seq,sec,pref='7hitsnew',return3=True)
        #TODO implement simpler init of obs? and separate init of pc1sobs (2) to other method
        self.ss8inds=[self.allss8.index(ss8) for ss8 in self.s8obs]
        print('observed s8',''.join(self.s8obs))
        print('observed s3',''.join(self.s3obs))
        ##self.resis,pc1sobs,pc2sobs=getobsfromzfile(bmrid,'7hitsnew')
        ##self.resis,pc1sobs,pc2sobs,zscores=getobsfromzfile(bmrid,'7hits14')
        self.resis,pc1sobs,pc2sobs,zscores=getobsfromzfile(bmrid,'7hitsnew')
        self.mini=self.resis[0]
        self.maxi=self.resis[-1]
        print('mini and maxi:',self.mini,self.maxi)
        self.ru=array(self.resis-1,dtype=int)
        self.pcsobsref=(pc1sobs,pc2sobs)
        self.zscores=array(zscores)
        self.disordered=self.zscores<8.0

    def set_input(self,seq,resis,pc1sobs,pc2sobs,zsco):
        bmrid=self.bmrid
        ##self.ss8inds=[self.allss8.index(ss8) for ss8 in self.s8obs]
        self.seq=[s for s in seq]
        self.resis=array(resis)
        self.mini=self.resis[0]
        self.maxi=self.resis[-1]
        print('mini and maxi:',self.mini,self.maxi)
        self.ru=array(self.resis-1,dtype=int)
        self.pcsobsref=(pc1sobs,pc2sobs)
        ##print zsco
        self.zscores=array(zsco)
        self.disordered=self.zscores<8.0
        self.s8obs=None #no observed - this is de novo prediction
        self.s3obs=None

    def make_guess(self):
        self.ss8priors,post0=guesss8s(self.params,self.resis,self.pcsobsref,self.priors,self.ssigs,self.s8obs)

    def evaluate_priors(self):
        probs=self.ss8priors
        trueprobs=average([probs[self.allss8.index(sx)] for sx in self.s8obs])
        print('trueprobs (priors):',trueprobs)
        return trueprobs

class SSopt(GenericIndividual):

    def __init__(self,ssp,s8,s3=None):
        self.ssp=ssp
        self.s8=s8
        if s3==None:
            ss3s='HSC'
            ss8to3ind={'H':0,'G':0,'I':0,'E':1,'-':2,'T':2,'S':2,'B':2}
            s3=[ss3s[ss8to3ind[s8i]] for s8i in s8]
        self.s3=s3
        self.ss8inds=[self.ssp.allss8.index(ss8) for ss8 in (self.s8+['-','-','-','-'])]

    def get_clone(self,need_segments=False):
        s8=self.s8[:]
        s3=self.s3[:]
        new=SSopt(self.ssp,s8,s3)
        ##new.init_segments()
        ##new.segments=Segments(s8,s3)
        if need_segments:new.segments=self.segments.get_clone()
        new.S9s=[s9.copy() for s9 in self.S9s]
        self.backpcs=[None,None]#must be updated #TJEK OK?
        #new.ss8inds=self.ss8inds[:]
        new.post0ref=self.post0ref.copy()
        return new

    def backcalcPCs(self,pcnum):
        subss8={'H':'HGI','S':'E','C':'-TSB'}
        indss3={'H':[0,1,2],'S':[3],'C':[4,5,6,7]}
        indss8={'G':1,'I':2,'T':5,'S':6,'B':7}
        allss8='HGIE-TSB'
        numres=len(self.ssp.seq)##-4
        pari=self.ssp.params[pcnum]
        S8=pari['S8']
        self.ss8inds=[self.ssp.allss8.index(ss8) for ss8 in (self.s8+['-','-','-','-'])]
        ss8inds=self.ss8inds
        s8vals=[S8[ss8inds[n],n] for n in range(numres)]
        S9=zeros((9,numres))
        S9[4]=s8vals
        for n in range(numres):
            gssn=self.s3[n]
            N=pari[gssn][1]
            bck=[N[0,k,ss8inds[n-1-k]] for k in range(4-1,-1,-1)]
            fwd=[N[1,k,ss8inds[n+1+k]] for k in range(4)]
            S9[:4,n]=bck
            S9[5:,n]=fwd
        subtot=sum(S9,axis=0)
        return subtot,S9

    def backcalcmut(self,n0,ss8m):##,isnew8=True):
        M=len(ss8m)
        if M>1:
            if debug:print('NOTE: block-mutation',ss8m,M,n0)
        subss8={'H':'HGI','S':'E','C':'-TSB'}
        indss3={'H':[0,1,2],'S':[3],'C':[4,5,6,7]}
        indss8={'G':1,'I':2,'T':5,'S':6,'B':7}
        allss8='HGIE-TSB'
        conv8to3={'G':'H', 'H':'H', 'I':'H', 'E':'S', 'B':'C','T':'C', 'S':'C', '-':'C','U':'U'}
        ss8inds=[allss8.index(ss8) for ss8 in (self.s8+['-','-','-','-'])]#generate fresh local
        ##s3=self.s3
        s3new=self.s3[:]
        for k in range(M):
            ss8ind=allss8.index(ss8m[k])
            if debug:print(M,k,n0,n0+k,len(ss8inds),ss8ind)
            ss8inds[n0+k]=ss8ind#modify only the local ss8inds
            s3new[n0+k]=conv8to3[ss8m[k]]
        numres=len(self.ssp.seq)
        newS9s=[s9i.copy() for s9i in self.S9s]
        for n in range(n0,n0+M):
                ##isnew8=conv8to3[ss8m[n-n0]]!=s3[n]
            for pcnum in (0,1):
                pari=self.ssp.params[pcnum]
                s8m=pari['S8'][ss8ind,n]
                ##S9=self.S9s[pcnum]
                S9=newS9s[pcnum]
                S9[4,n]=s8m
                if True:##isnew8: #in case of block-mutation we need this always...
                ##gssn=s3[n]
                    gssn=s3new[n]
                    N=pari[gssn][1]
                    bck=[N[0,k,ss8inds[n-1-k]] for k in range(4-1,-1,-1)]
                    fwd=[N[1,k,ss8inds[n+1+k]] for k in range(4)]
                    S9[:4,n]=bck
                    S9[5:,n]=fwd
                #now because ss8m is a new dssp8 class
                for k in range(4):
                    if n+1+k<numres:
                    ##S9[3-k,n+1+k]=pari[s3[n+1+k]][1][0,k,ss8ind]
                        S9[3-k,n+1+k]=pari[s3new[n+1+k]][1][0,k,ss8ind]
                    if n-1-k>=0:
                        ##S9[5+k,n-1-k]=pari[s3[n-1-k]][1][1,k,ss8ind]
                        S9[5+k,n-1-k]=pari[s3new[n-1-k]][1][1,k,ss8ind]
                ##newS9s.append(S9)
                ##subtot=sum(S9,axis=0)
        return newS9s,ss8inds

    def get_diff_mutation(self,n,ss8m):
        newS9s,newss8inds=self.backcalcmut(n,ss8m)##,isnew8)
        N=len(self.ssp.seq)
        M=len(ss8m)
        lr=(max(0,n-4),min(n+4+M,N))#only derive for local range
        backpcs=[sum(newS9s[pcnum][:,lr[0]:lr[1]],axis=0) for pcnum in (0,1)]
        locsegm=[ss8i for ss8i in ss8m]
        news8loc=self.s8[lr[0]:n]+locsegm+self.s8[n+M:lr[1]]
        locpost,oldloc=self.calcpostlik_local(lr,n,newss8inds,news8loc,backpcs)##,verb=True)
        if debug:print('locpost:',locpost,locpost-oldloc)
        self.newS9s=newS9s
        return locpost,locpost-oldloc

    def backcalcbothPCs(self):
        self.backpcs=[]
        self.S9s=[]
        for pcnum in (0,1):
            pcp,S9p=self.backcalcPCs(pcnum)
            self.backpcs.append(pcp)
            self.S9s.append(S9p)

    def calcpostlik_local(self,lr,nmut,ss8inds,s8,backpcs,verb=False):
        allss8='HGIE-TSB'
        numres=len(self.ssp.seq)
        if verb:print(''.join(s8))
        if verb:print([ss8inds[n-1] for n in range(lr[0],lr[1])])
        if verb:print([self.ss8inds[n-1] for n in range(lr[0],lr[1])])
        ru=self.ssp.ru
        tru=(ru<lr[1])&(ru>=lr[0])
        lru=ru[tru]
        if len(lru)<1: return -999,0#dont use
        minru=list(ru).index(min(lru))
        newru=lru-nmut+4
        newru-=max(0,4-nmut)#correct for N-term...OK?
        if verb:print(lru,minru,newru)
        ##print backpcs
        predsnew=[pcp[newru] for pcp in backpcs]
        if verb:print(predsnew)
        ##predsold=[self.backpcs[pc][ru][minru:minru+len(lru)] for pc in (0,1)]
        ##if verb:print predsold
        pcsobs=[self.ssp.pcsobsref[pc][minru:minru+len(lru)] for pc in (0,1)]
        if verb:print(pcsobs)
        #NOTE: s8 is local "9mer"
        sig=array([[self.ssp.ssigs[pcnum,allss8.index(s8[n])] for n in newru] for pcnum in (0,1)])
        if verb:print(sig)
        dev=array([predsnew[pc]-pcsobs[pc] for pc in (0,1)])
        if verb:print(dev)
        dev/=sig
        if verb:print('devloc:',dev)
        probsref=exp(-0.5*(array(dev)**2))/sig
        probs0ref=probsref[0]*probsref[1]
        if verb:print(probs0ref)
        #NOTE: ss8inds has full length
        priors=array([self.ssp.priors[ss8inds[int(n)-1],n-1] for n in lru+1])
        if verb:print('priorsloc:',priors)
        post0ref=probs0ref*priors
        self.post0refnewdata=post0ref,(minru,minru+len(lru))
        if verb:print(post0ref)
        post0reffirst=self.post0ref[minru:minru+len(lru)]
        if verb:print(post0reffirst)
        return sum(log(post0ref)),sum(log(post0reffirst))

    def calcpostlik(self):
        allss8='HGIE-TSB'
        ru=self.ssp.ru
        predsnew=[pcp[ru] for pcp in self.backpcs]
        ss8inds=self.ss8inds
        ##sig=array([[self.ssp.ssigs[pcnum,'HSC'.index(self.s3[int(n)-1])] for n in self.ssp.resis] for pcnum in (0,1)])
        sig=array([[self.ssp.ssigs[pcnum,allss8.index(self.s8[int(n)-1])] for n in self.ssp.resis] for pcnum in (0,1)])
        dev=array([predsnew[pc]-self.ssp.pcsobsref[pc] for pc in (0,1)])
        dev/=sig
        ##print 'dev:',dev[:,180:189]
        probsref=exp(-0.5*(array(dev)**2))/sig
        probs0ref=probsref[0]*probsref[1]
        ##post0ref=probs0ref*array([self.ssp.priors[ss8inds[int(n)-1],n-1] for n in self.ssp.resis])
        priors=array([self.ssp.priors[ss8inds[int(n)-1],n-1] for n in self.ssp.resis])
        ##print 'priors:',priors[175:184]
        ##post0ref=probs0ref*sqrt(priors) would this help although not strictly "correct"?
        post0ref=probs0ref*priors
        self.post0ref=post0ref
        self.score=sum(log(post0ref))
        self.energy=-self.score
        ave=self.score/len(post0ref)
        if debug:print('sumpostlik',self.score,ave)
        return ave

    def evaluate(self,flag='normal'):
        ps8=self.s8##[:-4]
        ps3=self.s3##[:-4]
        os8=self.ssp.s8obs##[:-4]
        os3=self.ssp.s3obs##[:-4]
        numres=len(os3)
        if debug:print(len(ps8),len(os8),numres)
        if flag=='byres':
            tr8= array(ps8)==array(os8)
            tr3= array(ps3)==array(os3)
            return tr8,tr3
        Q8=sum(array(ps8)==array(os8))*1.0/numres
        Q3=sum(array(ps3)==array(os3))*1.0/numres
        if debug:print('evaluation: %6s %6.4f %6.4f'%(flag,Q3,Q8))
        return Q8,Q3

    def init_segments(self):
        self.segments=Segments(self.s8,self.s3)

    def choose_mutation(self,verb=False):
        ##probs=some numbers
        probs=(0.3,0.2,0.2,0.05,0.05,0.12,0.08)#tentative assignments
        ind=selector(probs)
        ##print 'check selector',ind
        info='coil'
        flags=['coil','incr','decr','split','del','H2G','C2G']
        #each case is a rational designed mutation (yet randomly selected)
        if ind==0:
            if verb:print('point-mutating s8 in coil->coil')
            #randomly choose target position and secondary structure
            i,ss8=self.segments.choose_coil_point()
        elif ind==1:
            if verb:print('incrementing secondary element by one')
            i,ss8,info=self.segments.choose_incr_point()#info is direction
        elif ind==2:
            if verb:print('decrementing secondary element')
            i,ss8,info=self.segments.choose_decr_point()
        elif ind==3:
            if verb:print('split by mutating secondary element at point: ss -> coil (large ss)')
            i,ss8,info=self.segments.choose_split_point()
        #below multi-point mutations (range)
        elif ind==4:
            if verb:print('deleting secondary element ss -> coil')
            i,ss8,info=self.segments.choose_delete_elem()#ss8 is len>1 segment of ss8s, info=sl
        elif ind==5:
            if verb:print('overwrite (terminal) segment of helix to 3_10')
            i,ss8,info=self.segments.choose_overwriteH2G()#info=direc
        elif ind==6:
            if verb:print('overwrite 3-long segment of coil to 3_10')
            i,ss8,info=self.segments.choose_overwriteC2G()
        if i==None:return self.choose_mutation(verb)
        else:
            if verb:
                print('chose mutation',flags[ind],ind,i,ss8,info,self.s8[i])
                print(''.join(self.s8))
                print(''.join(self.s3))
                if ind<4:
                    print(' '*i+ss8+' '*(len(self.s8)-i-1)+'|')
                elif flags[ind]=='del':
                    sl=len(ss8)
                    print(' '*i+ss8+' '*(len(self.s8)-i-sl)+'|')
                elif flags[ind]=='H2G':
                    sl,direc=info
                    if direc in ['L','a']:#from left or all
                        print(' '*i+ss8+' '*(len(self.s8)-i-sl)+'|')
                    else:
                        print(' '*(i-sl)+ss8+' '*(len(self.s8)-i)+'|')
                elif flags[ind]=='C2G':
                    sl=3
                    print(' '*i+ss8+' '*(len(self.s8)-i-sl)+'|')
            return ind,i,ss8,info

    def _anal_segments(self,other):
        self.segments.comparedis(other.segments)

    def initialize_random(self,envi=None):
        pri=self.ssp.ss8priors
        ss3s='HSC'
        allss8='HGIE-TSB'
        ss8to3ind={'H':0,'G':0,'I':0,'E':1,'-':2,'T':2,'S':2,'B':2}
        ss8ind=[fastselector(hstack(([0],pri[:,n]))) for n in range(len(pri[0]))]
        ss8=[allss8[i] for i in ss8ind]
        ss3=[ss3s[ss8to3ind[s8]] for s8 in ss8]
        if debug:print('ss8rand:',''.join(ss8))
        if debug:print('ss3rand:',''.join(ss3))
        new=SSopt(self.ssp,ss8,ss3)
        new.backcalcbothPCs()
        new.calcpostlik()
        new.init_segments() #or consider the energy is OK before initializing segments?
        ch3,ch8=new.segments.remedy_disallowed()
        ##q8,q3=new.evaluate()
        ##print 'ener',new.energy,q8,q3
        return new

    def init_from_genestr(self,s8):#TODO: update
        ssp=None;s3=None
        return SSopt(ssp,s8,s3)

    def calc_distance(self,other):
        pass

    def getid(self):
        return ''.join(self.s8)

    def __str__(self):
        return self.getid()

    def crossover(self,other):
        M=len(self.s8)
        both=self,other
        ##inds=numpy.random.random_integers(0,1,M)
        inds=choose_random_consecutive(M,p=0.2)
        newss8=[both[inds[i]].s8[i] for i in range(M)]
        newopt=SSopt(self.ssp,newss8)
        #might need to remedy newopt before returning?
        return newopt

    def multicrossover(self,popul,rat,size):
        M=len(self.s8)
        nums=[popul.selectNormal(rat,size) for _ in range(M)]
        newss8=[popul[nums[i]].s8[i] for i in range(M)]
        newopt=SSopt(self.ssp,newss8)
        #might need to remedy newopt before returning?
        return newopt
        pass

    def mutate(self):
        prob=rand()
        print('not implemented...')
        1/0

    def calculate_fitness(self,dostats=False,dovis=False):
        self.backcalcbothPCs()
        self.calcpostlik()
        ##print 'fullstats:',self.ener
        ##print 'fullstats:',rmsd,RSS,num,aic,numpars,len(params.fitdata[-1])

    def get_class_stats(self,popul,statlen=None):
        allss8='HGIE-TSB'
        s8=self.s8
        M=len(s8)
        if statlen==None:statlen=len(popul)
        A=[[ssopt.s8[i] for ssopt in popul[:statlen]] for i in range(M)]
        C=array([[A[i].count(s) for s in allss8] for i in range(M)])*1.0/statlen
        entrs=[shannon(C[i]) for i in range(M)]
        spread=exp(-average(entrs))
        ##visprobs(C.transpose())
        probs=C.transpose()
        trueprobs=-9.0
        if debug:
            trueprobs=average([probs[allss8.index(sx)] for sx in self.ssp.s8obs])
            if debug:print('trueprobs (stats):',trueprobs,spread)
        return trueprobs,spread,C


class Segments8(dict):

    def __init__(self,s8,allss='HGSTB-E'):
        dict.__init__(self)
        s3=s8
        self.s8=s8
        self.s3=s3
        p3=None
        previ=0
        sl=1
        self.segm=[]
        self._ar=zeros(len(s3),dtype=int)
        for i,s3i in enumerate(s3):
            if s3i==p3:sl+=1
            elif p3!=None:
                if not p3 in self:self[p3]={}
                self[p3][previ]=sl
                self._ar[previ:previ+sl]=len(self.segm)
                self.segm.append([p3,previ])
                #reinitialize segment length and previ
                sl=1
                previ=i
            p3=s3i
        if True: #handle end
            if not p3 in self:self[p3]={}
            self[p3][previ]=sl
            self._ar[previ:previ+sl]=len(self.segm)
            self.segm.append([s3i,previ])


class Segments(dict):

    def __init__(self,s8=None,s3=None):
        dict.__init__(self)
        if s8!=None:
            self.s8=s8
            self.s3=s3
            self['H']={}
            self['S']={}
            self['C']={}
            p3=None
            previ=0
            sl=1
            self.segm=[]
            self._ar=zeros(len(s3),dtype=int)
            for i,s3i in enumerate(s3):
                if s3i==p3:sl+=1
                elif p3!=None:
                    self[p3][previ]=sl
                    self._ar[previ:previ+sl]=len(self.segm)
                    self.segm.append([p3,previ])
                    #reinitialize segment length and previ
                    sl=1
                    previ=i
                p3=s3i
            if True: #handle end
                self[p3][previ]=sl
                self._ar[previ:previ+sl]=len(self.segm)
                self.segm.append([p3,previ])
            if debug:print(self.segm)
            ##print list(self._ar)
            if debug:print(self)

    def get_clone(self):
        new=Segments()
        for ss in 'HSC':
            new[ss]=self[ss].copy()
        new.s8=self.s8[:]
        new.s3=self.s3[:]
        new.segm=[lst[:] for lst in self.segm]
        new._ar=self._ar.copy()
        return new

    def modifys8(self,probs,i,changes8):
        coils='-TSB'
        prob=rand()
        cum=0
        for j,probj in enumerate(probs):
            cum+=probj
            if prob<cum:
                self.s8[i]=coils[j]
                changes8.append((i,coils[j]))
                break

    def remedy_disallowed(self,validate=False,stoch={('H',1):(0.6,0.4),('H',2):(0.1,0.9),('S',1):(0.6,0.4),('G',3):(0.0,1.0)},
subs={('H',1):(0.3,0.45,0.2,0.05),('H',2):(0.2,0.65,0.1,0.05),('S',1):(0.4,0.15,0.2,0.25)}):
        changes3=[]
        changes8=[]
        if debug:print(self)
        if debug:print(''.join(self.s8))
        if debug:print(''.join(self.s3))
        while True:
            if debug:print(''.join(self.s3))
            dis=self.return_disallowed()
            if dis==None:
                if debug:print('sequence allowed...')
                break
            ##print dis
            ss,i,sl=dis
            if ss in 'HS':
                pdel,pext=stoch[(ss,sl)]
                prob=rand()
                if prob<pdel:
                    if debug:print('remedying by delete',ss,i,sl)
                    self.delete_segment(i,ss,'C')
                    for k in range(sl):
                        changes3.append((i+k,'C'))
                        self.modifys8(subs[(ss,sl)],i+k,changes8)
                else:
                    if i==0:ssp=None
                    else:ssp=self.s3[i-1]
                    try:sss=self.s3[i+sl]
                    except IndexError:
                        sss=None
                        ##print 'note: extending from end',dis
                    if ssp=='C' and sss!='C':
                        delta=-1
                    elif sss=='C' and ssp!='C':
                        delta=1
                    elif sss==None:delta=-1
                    elif i==0:delta=1
                    elif ssp==None:delta=1
                    else:
                        delta=1-2*int(rand()*2) #random direction: 1 or -1
                    if debug:print('remedying by increment',ss,i,delta,ssp,sss)
                    self.increment_segment(i,ss,delta)
                    s8id={'H':'H','S':'E'}[ss]
                    if delta<0:
                        self.s8[i+delta]=s8id
                        changes8.append((i+delta,s8id))
                    else:
                        self.s8[i+delta+sl-1]=s8id
                        changes8.append((i+delta+sl-1,s8id))
            elif ss=='G':
                if debug:print('remedying by introducing G-helix',i)
                for k in range(3):
                    self.s8[i+k]='G'
                    changes8.append((i+k,'G'))
            elif ss=='g':
                if debug:print('remedying too short G-helix probably within H-helix replacing with H',i)
                for k in range(sl):
                    self.s8[i+k]='H'
                    changes8.append((i+k,'H'))
            if validate:self._validate_defs()
        if debug:print(''.join(self.s8))
        if validate:self._validate_defs()
        return changes3,changes8

    def _validate_defs(self):
        s30=''.join(self.s3)
        ##print s30
        s3d=self.get_s3_from_dict()
        s3s=self.get_s3_from_segm()
        s3a=self.get_s3_from_ar()
        conv8to3={'G':'H', 'H':'H', 'I':'H', 'E':'S', 'B':'C','T':'C', 'S':'C', '-':'C','U':'U'}
        s3from8=''.join([conv8to3[x] for x in self.s8])
        ##iden=s30==s3d==s3s==s3a
        iden=s30==s3d==s3s==s3a==s3from8
        if not iden:
            print('warning: not identical')
            print(s30);print(s3d);print(s3s);print(s3a);print(s3from8)

    def delete_segment(self,i,ss,target):
        #assert ss in 'HS' and target=='C'
        si=self._ar[i]
        s0c,i0c=self.segm[si]#center segment
        sl=self[s0c][i0c]
        for k in range(sl):self.s3[i+k]=target
        if debug:
            print('delete:',ss,i,sl,si,target,s0c,i0c)
            print('delete:',self.segm[si-1:si+2])
        s0p=None;s0s='none'
        if si>0:
            s0p,i0p=self.segm[si-1]#preceding  segment
            slp=self[s0p][i0p]
        if len(self.segm)>si+1:
            s0s,i0s=self.segm[si+1]#subsequent segment
            try:sls=self[s0s][i0s]
            except KeyError:
                print('this is crashing!!...')
                print(''.join(self.s8))
                print(''.join(self.s3))
            sls=self[s0s][i0s]
        ##print ss,i,sl,s0p,i0p,slp,s0s,i0s,sls,self.segm[si-1:si+2]
        if s0p==s0s:
            if debug:print('both are coil probably',s0p,s0s)
            if s0p!=target:
                if debug:print('Warning: sandwiched between non-targets (calling modify and incr)',s0p,target)
                if debug:print(''.join(self.s8))
                if debug:print(''.join(self.s3))
                self.modify_segment(i,ss,target)
                for k in range(sl-1):self.increment_segment(i,target,1)
            else:
                if debug:print('preceding segment equals target',s0p,target,s0s)
                self[ss].pop(i)
                self.segm.pop(si)
                self.segm.pop(si)#2nd pop -> two deleted
                self[s0s].pop(i0s)
                self[s0p][i0p]+=(sl+sls)
                self._ar[i:i+sl]-=1
                self._ar[i+sl:]-=2
                if debug:print('result delete:',self.segm)
        elif s0p==target:##'C':
            self[ss].pop(i)
            self.segm.pop(si)
            if debug:print('preceding coil segment extended right',i0p,sl)
            self[s0p][i0p]+=sl
            self._ar[i:]-=1
        elif s0s==target:##'C':
            self[ss].pop(i)
            self.segm.pop(si)
            if debug:print('subsequent segment extended left and given new start index',i,sls,sl,s0s,i0s)
            self[s0s].pop(i0s)#i0s==i+sl
            self[s0s][i]=sls+sl
            self.segm[si][1]-=sl # after first pop si is now for subsequent segment!
            #was: self._ar[i+1:]-=1
            self._ar[i+sl:]-=1
        else:
            if debug:print('nothing special',s0p,s0s,target,sl)#below OK???
            self[ss].pop(i)
            self[target][i]=sl
            self.segm[si][0]=target


    def decrement_segment_end(self,i,ss,si):
        self.s3[-1]='C'
        self[ss][i]-=1
        end=len(self._ar)-1
        self['C'][end]=1
        self.segm.append(['C',end])
        self._ar[-1]+=1

    def decrement_segment_start(self,i,ss):
        self.s3[0]='C'
        sl=self[ss].pop(0)
        self[ss][i+1]=sl-1
        self['C'][0]=1
        self.segm.insert(0,['C',0])
        self.segm[1][1]=1#added newly
        self._ar[1:]+=1

    def decrement_segment(self,i,ss,delta):
        si=self._ar[i]
        s0c,i0c=self.segm[si]#center segment
        if delta<0:
            if si>0:
                s0p,i0p=self.segm[si-1]#preceding  segment
                self.increment_segment(i0p,s0p,-delta)
            else:
                if debug:print('changing start...',i,ss,si,delta)
                self.decrement_segment_start(i,s0c)
        elif delta>0:
            if len(self.segm)>si+1:
                s0s,i0s=self.segm[si+1]#subsequent segment
                self.increment_segment(i0s,s0s,-delta)
            else:
                if debug:print('changing end...',i,ss,si,delta)
                self.decrement_segment_end(i,s0c,si)

    def increment_segment(self,i,ss,delta):
        ##sl=self[ss][i]
        si=self._ar[i]
        s0c,i0c=self.segm[si]#center segment
        sl=self[s0c][i0c]
        if debug:print('increment:',ss,i,sl,si)
        if debug:print('increment:',self.segm[si-1:si+2])
        #NOTE: if abs(delta)>1:increment can exceed one more segment and this is not implemented
        if delta>0:
            s0s,i0s=self.segm[si+1]#subsequent segment
            sls=self[s0s][i0s]
            if debug:print('incrementing to right',i,delta,ss,self.segm[si+1])
            if sls<=delta:
                if debug:print('increment exceeds right segment',sls,delta,self.segm[si+1])
                self.delete_segment(i0s,s0s,s0c)
            else:
                self.s3[i0s:i0s+delta]=ss#change to target
                self[ss][i0c]+=delta #extend center segment length
                self[s0s].pop(i0s)
                self[s0s][i0s+delta]=sls-delta #decrease subs segm len and move to right
                self.segm[si+1][1]+=delta
                self._ar[i0s:i0s+delta]-=1
        elif delta<0:
            s0p,i0p=self.segm[si-1]#preceding segment
            slp=self[s0p][i0p]
            if debug:print('incrementing to left',i,delta,ss,self.segm[si-1])
            if slp<=abs(delta):
                if debug:print('increment exceeds left segment',slp,delta,self.segm[si-1])
                self.delete_segment(i0p,s0p,s0c)
            else:
                self.s3[i0c+delta:i0c]=ss#change to target
                self[ss].pop(i0c)
                self[ss][i0c+delta]=sl-delta #extend center segment length (delta<0) and move to left
                self[s0p][i0p]=slp+delta #decrease prev segm len
                self.segm[si][1]+=delta
                self._ar[i0c+delta:i0c]+=1

    def modify_segment(self,i,ss,target):##,delta):
        si=self._ar[i]
        s0c,i0c=self.segm[si]#center segment
        sl=self[s0c][i0c]
        self.s3[i]=target#easy!
        if debug:print('modify:',ss,i,sl,si)
        if i0c<i<i0c+sl-1:
            if debug:print('middle of segment modification',i0c,i,i0c+sl,ss,target)
            self[s0c][i0c]=i-i0c
            self[target][i]=1
            self[s0c][i+1]=i0c+sl-i-1
            self.segm.insert(si+1,[target,i])
            self.segm.insert(si+2,[s0c,i+1])
            self._ar[i]+=1
            self._ar[i+1:]+=2
            #note that the sum of segment lengths is preserved == sl
        if i0c==i:
            #assuming s0p!=target
            if debug:print('left-side segment modification',i0c,ss,target,s0c,si,sl)
            ##s0p,i0p=self.segm[si-1]#preceding segment
            ##if s0p==target:print 'WARNING: prev ss equals target',target
            self[s0c].pop(i)
            self[target][i]=1
            self.segm.insert(si+1,[target,i])
            if sl>1:#TJEK OK?!....
                self[s0c][i+1]=sl-1
                self.segm.insert(si+2,[s0c,i+1])
                self._ar[i+1:]+=1
            self.segm.pop(si)
        ##if i==i0c+sl-1:
        elif i==i0c+sl-1:
            if debug:print('right-side segment modification',i,ss,target)
            ##if s0s==target:print 'WARNING: prev ss equals target',target
            self[s0c][i0c]=sl-1
            self[target][i]=1
            self.segm.insert(si+1,[target,i])
            self._ar[i]+=1
            self._ar[i+1:]+=1
            #note that the sum of segment lengths is preserved == sl

    def choose_coil_point(self):
        coils=list(self['C'].items())
        if len(coils)==0:return None,None
        n=randint(0,len(coils)-1)
        i0,sl=coils[n]
        j=randint(0,sl-1)
        i=i0+j
        s8i=self.s8[i]
        coilvals='-TSB'
        s8val=s8i
        probs=(0.4,0.2,0.3,0.1)
        if (i>0 and self.s8[i-1]=='E' or i<len(self.s8)-1 and self.s8[i+1]=='E'):
            probs=(0.4,0.3,0.3)#bridge should not extend strand?...
        while s8val==s8i:
            ind=selector(probs)
            s8val=coilvals[ind]
        return i,s8val

    def choose_incr_point(self):
        hs=list(self['H'].items())
        es=list(self['S'].items())
        if len(hs)==0 and len(es)==0:return None,None,None
        if len(hs)==0 and len(es)>0:ssm='S'
        elif len(hs)>0 and len(es)==0:ssm='H'
        else:ssm=randchoice('HS')
        elems=list(self[ssm].items())
        n=randint(0,len(elems)-1)
        i0,sl=elems[n]
        if i0==0:direc='R'
        elif int(self._ar[i0])==len(self.segm)-1:direc='L'
        else:direc=randchoice('LR')
        if direc=='R':
            i=i0+sl
            refi=i0+sl-1
        else:
            i=i0-1
            refi=i0
        d3to8={'H':'H','S':'E'}
        ##return i,d3to8[ssm],direc
        return i,self.s8[refi],(i0,ssm,direc)

    def choose_delete_elem(self):
        hs=list(self['H'].items())
        es=list(self['S'].items())
        if len(hs)==0 and len(es)==0:return None,None,None
        if len(hs)==0 and len(es)>0:ssm='S'
        elif len(hs)>0 and len(es)==0:ssm='H'
        else:ssm=randchoice('HS')
        elems=list(self[ssm].items())
        minelem=min(elems,key=lambda x:x[1])
        minsl={'S':2,'H':4}#temporarily allow 3-long alpha-helix
        if minelem[1]>minsl[ssm]+2:return None,None,None #unlikely to benefit from delete...
        i0,sl=minelem
        coils='-TSB'
        subs={'H':(0.5,0.27,0.2,0.03),'S':(0.5,0.15,0.2,0.15)}
        target=''
        for _ in range(sl):
            ind=selector(subs[ssm])
            target+=coils[ind]
        return i0,target,ssm

    def choose_decr_point(self,allowsmall=False):
        hs=list(self['H'].items())
        es=list(self['S'].items())
        if len(hs)==0 and len(es)==0:return None,None,None
        if len(hs)==0 and len(es)>0:ssm='S'
        elif len(hs)>0 and len(es)==0:ssm='H'
        else:ssm=randchoice('HS')
        elems=list(self[ssm].items())
        maxelem=max(elems,key=lambda x:x[1])
        minsl={'S':2,'H':4}#temporarily allow 3-long alpha-helix
        if maxelem[1]<minsl[ssm] and not allowsmall:return None,None,None
        sl=0
        while sl<minsl[ssm]:
            n=randint(0,len(elems)-1)
            i0,sl=elems[n]
            if allowsmall:break
        direc=randchoice('LR')
        if direc=='R':
            i=i0+sl-1
            bi=i+1
        else:
            i=i0
            bi=i-1
        d3to8={'H':'H','S':'E'}
        if bi<0 or bi==len(self.s3):bases3='C'
        else:bases3=self.s3[bi]
        if bases3=='C':
            coils='-TSB'
            subs={'H':(0.5,0.27,0.2,0.03),'S':(0.65,0.15,0.2,0.0)}
            ind=selector(subs[ssm])
            targets8=coils[ind]
        else:
            targets8=d3to8[bases3]
        if debug:print('bases3',i,bi,bases3,targets8)
        return i,targets8,(i0,ssm,direc)

    def choose_split_point(self):
        hs=list(self['H'].items())
        es=list(self['S'].items())
        minsl={'S':2,'H':3}
        if len(hs)==0 and len(es)==0:return None,None,None
        if len(hs)==0 and len(es)>0:ssm='S'
        elif len(hs)>0 and len(es)==0:ssm='H'
        else:
            smaxls=max([elem[1]-minsl['S']*2 for elem in list(self['S'].items())])
            hmaxls=max([elem[1]-minsl['H']*2 for elem in list(self['H'].items())])
            if smaxls<1 and hmaxls<1:return None,None,None
            elif smaxls>0 and hmaxls<1:
                ssm='S'
            elif hmaxls>0 and smaxls<1:
                ssm='H'
            else:
                ssm=randchoice('HS')
        elems=list(self[ssm].items())
        maxls=max([elem[1]-minsl[ssm]*2 for elem in elems])
        if maxls<1:return None,None,None
        sl=0
        while sl<minsl[ssm]*2+1:
            n=randint(0,len(elems)-1)
            i0,sl=elems[n]
            ##if allowsmall:break
        j=randint(minsl[ssm],sl-minsl[ssm]-1)
        i=i0+j
        coils='-TSB'
        subs={'H':(0.27,0.5,0.2,0.03),'S':(0.65,0.15,0.2,0.0)}
        ind=selector(subs[ssm])
        return i,coils[ind],ssm

    def choose_overwriteH2G(self):
        hs=list(self['H'].items())
        if len(hs)==0:return None,None,None
        elems=list(self['H'].items())
        minls=min([elem[1] for elem in elems])
        if minls>4:
            n=randint(0,len(elems)-1)
            i0,sl=elems[n]
            direc=randchoice('LR')
            if direc=='L':
                i=i0
                gsl=[3,min(sl,4),min(sl,5)][selector((0.6,0.3,0.1))]
                if not 'H' in self.s8[i:i+sl]:return None,None,None
            else:
                ##i=i0+sl-1
                gsl=[3,min(sl,4),min(sl,5)][selector((0.6,0.3,0.1))]
                ##if not 'H' in self.s8[i-sl+1:i+1]:return None,None,None
                if not 'H' in self.s8[i0+sl-gsl:i0+sl]:return None,None,None
                i=i0+sl-gsl
        else:
            direc='a'
            gsl=999
            while gsl>4:
                n=randint(0,len(elems)-1)
                i,gsl=elems[n]
            if not 'H' in self.s8[i:i+gsl]:return None,None,None
        return i,'G'*gsl,(gsl,direc)

    def choose_overwriteC2G(self):
        cs=list(self['C'].items())
        if len(cs)==0:return None,None,None
        elems=list(self['C'].items())
        minls=min([elem[1] for elem in elems])
        if minls<3:return None,None,None
        sl=0
        while sl<3:
            n=randint(0,len(elems)-1)
            i0,sl=elems[n]
        j=randint(0,sl-3)
        i=i0+j
        #NOTE: what if new GGG edges old helix?... -> extend
        return i,'G'*3,sl

    def get_s8_mutation(self,flag,ind,i,ss8):
        flags=['coil','incr','decr','split','del','H2G','C2G']
        s8new=self.s8[:]
        if flag in ['coil','incr','decr','split']:
            s8new[i]=ss8
        else:
            for k,s8k in enumerate(ss8):s8new[i+k]=s8k
        return s8new

    def execute_mutation(self,flag,ind,i,ss8,info):
        flags=['coil','incr','decr','split','del','H2G','C2G']
        if flag=='coil':
            self.s8[i]=ss8
        elif flag=='incr':
            #see choose_incr_point
            self.s8[i]=ss8
            i0,ssm,direc=info
            if direc=='R':delta=1
            else:delta=-1
            self.increment_segment(i0,ssm,delta)
        elif flag=='decr':
            #see choose_decr_point
            self.s8[i]=ss8
            i0,ssm,direc=info
            if direc=='R':delta=1
            else:delta=-1
            self.decrement_segment(i0,ssm,delta)
        elif flag=='split':
            #see choose_split_point
            self.s8[i]=ss8
            ssm=info
            self.modify_segment(i,ssm,'C')
        elif flag=='del':
            #see choose_delete_elem
            ssm=info
            for k,s8k in enumerate(ss8):self.s8[i+k]=s8k
            self.delete_segment(i,ssm,'C')
        if flag=='H2G':
            #see choose_overwriteH2G
            for k,s8k in enumerate(ss8):self.s8[i+k]=s8k
        if flag=='C2G':
            #see choose_overwriteC2G
            for k,s8k in enumerate(ss8):self.s8[i+k]=s8k#always 3-long
            self.modify_segment(i,'C','H')
            for k in (1,2): self.increment_segment(i,'H',1)
        if False:self._validate_defs()#TAKEBACK for debug!!

    def get_s3_from_dict(self):
        ds8=array(['u' for _ in range(len(self.s8))],dtype='|S1')
        for ss in self:
            for i in self[ss]:
                sl=self[ss][i]
                ds8[i:i+sl]=ss
        return ''.join(ds8)

    def get_s3_from_segm(self):
        segm=self.segm
        ds8=array(['u' for _ in range(len(self.s8))],dtype='|S1')
        s0s,i0s=segm[0] #just in case segm is length one
        for si in range(len(segm)-1):
            s0,i0=segm[si]
            s0s,i0s=segm[si+1]
            ds8[i0:i0s]=s0
        ds8[i0s:]=s0s#fix end
        return ''.join(ds8)

    def get_s3_from_ar(self):#but segm is also used once
        ds8=array(['u' for _ in range(len(self.s8))],dtype='|S1')
        sip=0;ip=0
        for i,si in enumerate(self._ar):
            if si!=sip:
                ds8[ip:i]=self.segm[sip][0]
                sip=si;ip=i
        ds8[ip:]=self.segm[-1][0]
        return ''.join(ds8)

    def return_disallowed(self):
        for i in self['H']:
            if self['H'][i]<3:return 'H',i,self['H'][i]#too short helix
        for i in self['S']:
            if self['S'][i]<2:return 'S',i,1#too short strand - but might be OK to work with...
        for i in self['H']:
            if self['H'][i]<4:
                for k in range(3):
                    if self.s8[i+k]!='G': return 'G',i,3
            ##else:
        for i in self['H']:
            sl=self['H'][i]
            segstr=self.s8[i:i+sl]
            ##print i,sl,segstr
            ##for m in re.finditer(r"G+", segstr):
                    ##if m.end()-m.start()<3:return 'g',i+m.start(),m.end()-m.start()
            if 'G' in segstr:
                    #might be a too short G-segment within Helix
                gi=segstr.index('G')
                if gi+1>=sl:         return 'g',i+gi,1
                if segstr[gi+1]!='G':return 'g',i+gi,1
                if gi+2>=sl:         return 'g',i+gi,2
                if segstr[gi+2]!='G':return 'g',i+gi,2
        return None

    def get_disallowed(self):
        sshort=[]
        for i in self['S']:
            if self['S'][i]<2:sshort.append(i)
        hshort=[]
        gonly=[]
        for i in self['H']:
            if self['H'][i]<3:hshort.append(i)
            elif self['H'][i]<4:gonly.append(i)
        return sshort,hshort,gonly

    def comparedis(self,other):
        lab=['beta','helix','gonly']
        for k in range(3):
            ss=self.disallowed[k]
            for i in ss:
                ss8o=other.s8[i]
                if debug:print('other short',lab[k],ss8o)

def getCSIpreds(ssp,bmrid):
    buf=initfil2('csi3output/bmr%s.out'%bmrid)[1:]
    sub3={'C':'C','H':'H','B':'S'}
    sub8={'C':'-','H':'H','E':'E','I':'E','T':'T'}
    s3=[sub3[lin[2]] for lin in buf]
    s8=[sub8[lin[3][0]] for lin in buf]
    if debug:print('CSI predictions for',bmrid)
    if debug:print(''.join(s3))
    if debug:print(''.join(s8))
    return SSopt(ssp,s8,s3)

def get_score(pr,p0):
    if pr>=1.0:
        score=1+p0/0.4
        if score>1.1:lab='9'
        else:lab='8'
    else:
        score=pr
        if pr>0.96:lab='7'
        elif pr>0.90:lab='6'
        elif pr<0.60:lab='1'
        else:
            lab=str(max(0,int(pr*10)-3))
            ##lab=str(max(0,int(pr*10)-2))
    return score,lab


class SOPopulation(Population):

    def derive_stats(self,cnt):
        eners=array([obj.energy for obj in self])
        ##genestd=self.getspjread()
        trueprobs,genestd,fracs=self[0].get_class_stats(self)
        self.trueprobs=trueprobs
        print('average energy: %9.3f %9.3f %8.4f %8.5f %7.4f %4d %3d'%(average(eners),min(eners),std(eners),trueprobs,genestd,cnt,len(eners)), end=' ')
        print(self[0].getid())

    def summarize_as_probs(self,dovis=True):
        allss8='HGIE-TSB'
        allss3='HSC'
        conv8to3={'G':'H', 'H':'H', 'I':'H', 'E':'S', 'B':'C','T':'C', 'S':'C', '-':'C','U':'U'}
        indss3={'H':[0,1,2],'S':[3],'C':[4,5,6,7]}
        obj=self[0]
        segm8=Segments8(obj.s8)
        visSS8max(segm8,obj.ssp.mini,obj.ssp.maxi)
        trueprobs,genestd,fracs=obj.get_class_stats(self)
        probs=fracs##.transpose()
        ##ANS=avenscorr(obj.ssp.params,fracs.transpose(),len(obj.ssp.seq))#-4)
        ##ss8priors,post0=guesss8s(obj.ssp.params,obj.ssp.resis,obj.ssp.pcsobsref,fracs.transpose(),obj.ssp.ssigs)
        ##post=post0/sum(post0,axis=0)
        ru=list(obj.ssp.ru)
        allconfdigits='';allconfdigits3='';matches='';outdata=[];alls8maxs='';alls3maxs=''
        pid=obj.ssp.bmrid
        outfiles=[open(fname+'_'+pid+'.txt','w') for fname in ['probs8','probs3','max8','max3','short8','short3']]
        testdata=[]
        seq=''.join(obj.ssp.seq)
        if dovis:
            visprobs3(fracs.transpose(),mini=obj.ssp.mini,maxi=obj.ssp.maxi)
            ##xticks(range(obj.ssp.mini,obj.ssp.maxi+1),obj.ssp.seq) #labels will overlap :(
            ##visprobs(post)
            ##show();1/0
        ##tr8,tr3=obj.evaluate('byres')
        dotest=obj.ssp.dotest
        if dotest:
            os8=obj.ssp.s8obs##[:-4]
            os3=obj.ssp.s3obs
        ##pot=post.transpose()
        for i in range(len(probs)):
            for n in range(4):
                ##outfiles[n].write('%3d'%(i+1))
                outfiles[n].write(' %3s %3d'%(obj.ssp.seq[i],i+1))
            pri=probs[i]
            outfiles[0].write(' %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f %6.4f\n'%tuple(pri))
            pri3=[sum([pri[j] for j in indss3[k]]) for k in 'HSC']
            outfiles[1].write(' %6.4f %6.4f %6.4f\n'%tuple(pri3))
            if i in ru:
                ##pti=pot[ru.index(i)]
                p0i=obj.post0ref[ru.index(i)]
            else:
                ##pti=[-9]*8
                p0i=0.000
            mip=pri.argmax()
            mip3=array(pri3).argmax()
            s8maxave=allss8[mip]
            s3maxave=allss3[mip3]
            s8max=obj.s8[i]
            s3max=obj.s3[i]
            alls8maxs+=s8max
            alls3maxs+=s3max
            ##s3max=conv8to3[s8max]
            entr=shannon(pri)
            score,confdigit=get_score(pri[mip],p0i)
            score3,confdigit3=get_score(pri3[mip3],p0i)
            allconfdigits+=confdigit
            allconfdigits3+=confdigit3
            vals=(i+1,s8max,pri[mip],exp(entr),p0i,score,confdigit)
            vals3=(i+1,s3max,pri3[mip3],exp(entr),p0i,score3,confdigit3)
            outfiles[2].write(' %s %6.4f %6.4f\n'%(s8max,pri[mip],p0i))
            outfiles[3].write(' %s %6.4f %6.4f\n'%(s3max,pri3[mip3],p0i))
            if dotest:
                iden8=os8[i]==s8max
                iden3=os3[i]==s3max
                if iden8:matches+='|'
                elif iden3:matches+=':'
                else: matches+=' '
                prn='%3d %s %6.4f %6.4f %6.4f %6.4f %6.4f %1s'%vals
                print('result:',obj.ssp.bmrid,prn,os8[i],iden8, end=' ')
                if not iden8:print(pri[allss8.index(os8[i])])
                else:print()
                testdata.append((iden8,score,iden3,score3,confdigit,confdigit3))
        if dotest:
            print('summarizing performance',pid,'--------------------')
            print(pid,'stats_confids:',allconfdigits3)
            print(pid,'stats_confids:',allconfdigits)
            print(pid,'stats_predict:',alls3maxs)
            print(pid,'stats_predict:',alls8maxs)
            print(pid,'stats_matches:',matches)
            print(pid,'stats_observs:',''.join(os8))
            print(pid,'stats_observs:',''.join(os3))
        dnums='1234567890'
        dtens,dones=divmod(len(alls8maxs),10)
        dstr=dtens*dnums+dnums[:dones]
        outfiles[4].write(dstr+'\n')
        outfiles[4].write(seq+'\n')
        outfiles[4].write(allconfdigits+'\n')
        outfiles[4].write(alls8maxs+'\n')
        outfiles[5].write(dstr+'\n')
        outfiles[5].write(seq+'\n')
        outfiles[5].write(allconfdigits3+'\n')
        outfiles[5].write(alls3maxs+'\n')
        for n in range(6):
            outfiles[n].close()
        return testdata

    def breed(self,limitfac=100.0,expandfac=1.0,temperature=0.3,probs=(0.6,0.3,0.1),
              growthmode='replace',selrats=(0.5,2.0),sortnum=10):
        children=SOPopulation()
        cnt=0;numrep=0
        size=len(self)#or maybe place inside loop?
        dct={}
        flags=['coil','incr','decr','split','del','H2G','C2G']
        self.iddct=dct
        for obj in self:dct[obj.getid()]=obj
        print('breeding population',size,limitfac,temperature,growthmode)
        while cnt<size*limitfac and len(children)<size*expandfac:
            #find mates (only one in case of mutation)
            i=self.selectNormal(selrats[0],size)
            obji=self[i]
            ##print 'breeding object',i##,onum
            #find breeding operation - and breed mates
            rn=uniform(0.0,1.0)
            psum=0.0;onum=None
            for j in range(len(probs)):
                psum+=probs[j]
                if rn<psum:break
            prevener=obji.energy
            if j==0:
                #---mutation---
                ##child=obji.mutate()#consider multiple mutations?
                ind,I,ss8,info=obji.choose_mutation()##verb=False)
                locpost,locdiff=obji.get_diff_mutation(I,ss8)
                enerdiff=-locdiff;childener='mut'
                if debug:print('mutation:',ind,I,ss8,info,flags[ind])
                ##testscore=locdiff+obji.score
                ##printr'testing sum for sumpostlik:',testscore,locdiff,flags[I],ss8
                ##success=obji.evaluate_local_observed(i,ss8)
                childid=''.join(obji.segments.get_s8_mutation(flags[ind],ind,I,ss8))
                repi=i
            elif j==1:
                #---crossover---(reproduce)
                onum=i
                while onum==i:onum=self.selectNormal(selrats[1],size)
                objo=self[onum]
                prevenero=objo.energy
                child=obji.crossover(objo)
                child.init_segments()
                if debug:print('crossover(bi):',child)
                ch3,ch8=child.segments.remedy_disallowed()
                if prevener>=prevenero:repi=i
                else:repi=onum
                childid=child.getid()
            elif j==2:
                #---multicrossover---(non-biological reproduction)
                onum=-1;repi=-1;objo=self[-1]
                child=objo.multicrossover(self,selrats[1],size)
                child.init_segments()
                if debug:print('multicrossover:',child)
                ch3,ch8=child.segments.remedy_disallowed()
                childid=child.getid()
            #consider acceptance of child
            if childid in dct:
                pass##dct[childid]+=1
                ##print 'note child allready used',childid,dct[childid],cnt
                ##print 'note child allready used',childid,cnt
            else:
                if j>0:
                    child.calculate_fitness()
                    childener=child.energy
                    enerdiff=childener-prevener
                    if debug:print('crossover',j,enerdiff)
                ptest=999
                if enerdiff>0:
                    ptest=exp(-(enerdiff)/temperature)
                    if repi==0:ptest=-999#to ensure that very best individual survives!
                if ptest>uniform(0.0,1.0):
                    ##print 'breedinfo: using',j,i,onum,enerdiff,childener,prevener,ptest
                    if j==0:
                        child=obji.get_clone(need_segments=True) #remember to update backpcs
                        child.segments.execute_mutation(flags[ind],ind,I,ss8,info)
                        ##child.calculate_fitness()#sets energy
                        child.S9s=obji.newS9s #child is clone
                        post0refnew,ranges=obji.post0refnewdata
                        child.post0ref[ranges[0]:ranges[1]]=post0refnew
                        child.energy=prevener+enerdiff
                    if debug:
                        q8,q3=child.evaluate()
                        print('breedinfo: using',j,i,'repi'+str(repi),onum,enerdiff,childener,prevener,ptest,q8*1000,q3*1000)
                        print('newss:',child,childener)
                    dct[childid]=child
                    numrep+=1
                    if True:
                        if growthmode=='replace':
                            self[repi]=child
                        elif growthmode=='append':
                            if j==0:self[repi]=child
                            else:self.append(child) #doesnt improve result
                        if numrep%sortnum==0:
                            self.sort('energy')
                            self.derive_stats(cnt)
                ##else:print 'breedinfo: rejecting',j,i,onum,childener,prevener,ptest
            cnt+=1

    def multi_breed(self,pops,limitfac=100):
        print('merging populations',len(pops))
        ##for popul in pops:popul.breed() must be breed before
        merged=pops[0]
        for i in range(1,len(pops)):merged.mergewith(pops[i])
        merged.sort('energy')
        merged.derive_stats(-1)
        merged.cull(30)
        merged.breed(limitfac=limitfac)
        return merged


def predict8ss(bmrid,seq,resis,pc1s,pc2s,zsco,dotest=False,dovis=False):
    ssp=SSparameters(bmrid)
    ssp.dotest=dotest
    if dotest:ssp.set_observed()
    else:ssp.set_input(seq,resis,pc1s,pc2s,zsco)
    ssp.initparameters(usesimple=False)
    ssp.make_guess()
    if dotest:trueprobs_priors=ssp.evaluate_priors()
    ss8max,ss3max=getmaxss(ssp.ss8priors)
    ssopt=SSopt(ssp,ss8max,ss3max)
    ssopt.backcalcbothPCs()
    ssopt.init_segments()
    ch3,ch8=ssopt.segments.remedy_disallowed()
    optlik=ssopt.calcpostlik()
    if dotest:q8max,q3max=ssopt.evaluate('max')
    comb=[]
    ##comb=SOPopulation();popul.envi=ssp
    T_0=time.time()
    ##for i in range(3):
    for i in [0]:
        popul=SOPopulation();popul.envi=ssp
        popul.fill_from_random(25,ssopt)
        popul.append(ssopt)
        popul.breed(limitfac=75,growthmode='append')
        popul.cull(len(popul)-100)
        ##comb.append(popul)
    ##popul=comb
    ##merged=popul.multi_breed(comb)
    ##q8breed,q3breed=merged[0].evaluate('breed')
    ##trueprobs_breed=merged.trueprobs
    print('final s8:',bmrid,''.join(popul[0].s8))
    testdata=popul.summarize_as_probs(dovis)
    if dotest:
        q8breed,q3breed=popul[0].evaluate('breed')
        trueprobs_breed=popul.trueprobs
        print('TOTAL TIME: (ms)',1000*(time.time()-T_0))
        sscsi=getCSIpreds(ssp,bmrid)
        q8csi,q3csi=sscsi.evaluate('CSI')
        print('summary %5s %6.4f %6.4f %7.4f %6.4f %6.4f  %6.4f %6.4f %7.4f'%(bmrid,trueprobs_priors,trueprobs_breed,trueprobs_breed-trueprobs_priors,q3breed,q8breed,q3csi,q8csi,q3breed-q3csi))
        ##print roc_auc_score([tup[0] for tup in testdata],[tup[1] for tup in testdata])
        return trueprobs_breed-trueprobs_priors,q8breed,q3breed-q3csi,testdata


def test14():
    ids=[lin[0] for lin in initfil2('ids14hits')]
    result=[]
    testdata=[]
    for bmrid in ids[:-1]:#last ID has no CSI preds
        tpdiff,q8opt,q3diff,data=predict8ss(bmrid)
        testdata+=data
        result.append((tpdiff,q8opt,q3diff))
    labs8=[tup[0] for tup in testdata]
    labs3=[tup[2] for tup in testdata]
    scos8=[tup[1] for tup in testdata]
    scos3=[tup[3] for tup in testdata]
    conf8=array([eval(tup[4]) for tup in testdata],dtype=int)
    conf3=array([eval(tup[5]) for tup in testdata],dtype=int)
    auc8 = roc_auc_score(labs8,scos8)
    auc3 = roc_auc_score(labs3,scos3)
    for i in range(1,10):
        labsi=array(labs8)[conf8==i]
        truei=sum(labsi)*1.0/len(labsi)
        print(i,truei,len(labsi)*1.0/len(labs8))
    print(average(result,axis=0),auc8,auc3)

##test14()
##from sklearn.metrics import roc_auc_score
##predict8ss('18341',dovis=True)



#constants for PePKalc
R = 8.314472
e = 79.0
a = 5.0
b = 7.5
cutoff = 2
ncycles = 5

def smallmatrixlimits(ires, cutoff, len):
    ileft = max(1, ires - cutoff)
    iright = min(ileft + 2 * cutoff, len)
    if iright == len:
        ileft = max(1, iright - 2 * cutoff)
    return (ileft, iright)

def smallmatrixpos(ires, cutoff, len):
    resi = cutoff + 1
    if ires < cutoff + 1:
        resi = ires
    if ires > len - cutoff:
        resi = min(len, 2 * cutoff + 1) - (len - ires)
    return resi

def fun(pH, pK, nH):
    return (10 ** ( nH*(pK - pH) ) ) / (1. + (10 **( nH*(pK - pH) ) ) )

def W(r,Ion=0.1):
    k = np.sqrt(Ion) / 3.08 #Ion=0.1 is default
    x = k * r / np.sqrt(6)
    return 332.286 * np.sqrt(6 / np.pi) * (1 - np.sqrt(np.pi) * x * np.exp(x ** 2) * erfc(x)) / (e * r)

def w2logp(x,T=293.15):
    return x * 4181.2 / (R * T * np.log(10))

pK0 = {"n":8.23, "D":3.86, "E":4.34, "H":6.45, "C":8.49, "K":10.34, "R":13.9, "Y":9.76, "c":3.55}

def calc_pkas_from_seq(seq=None, T=293.15, Ion=0.1):
    #pH range
    pHs = np.arange(1.99, 10.01, 0.15)
    #titratable groups
    ##pK0 = {"n":7.5, "D":4.0, "E":4.4, "H":6.6, "C":8.6, "K":10.4, "R":12.0, "Y":9.6, "c":3.5} #was these values!
    pK0 = {"n":8.23, "D":3.86, "E":4.34, "H":6.45, "C":8.49, "K":10.34, "R":13.9, "Y":9.76, "c":3.55}

    pos = np.array([i for i in range(len(seq)) if seq[i] in list(pK0.keys())])
    N = pos.shape[0]
    I = np.diag(np.ones(N))
    sites = ''.join([seq[i] for i in pos])
    neg = np.array([i for i in range(len(sites)) if sites[i] in 'DEYc'])
    l = np.array([abs(pos - pos[i]) for i in range(N)])
    d = a + np.sqrt(l) * b

    tmp = W(d,Ion)
    tmp[I == 1] = 0

    ww = w2logp(tmp,T) / 2

    chargesempty = np.zeros(pos.shape[0])
    if len(neg): chargesempty[neg] = -1

    pK0s = [pK0[c] for c in sites]
    nH0s = [0.9 for c in sites]

    titration = np.zeros((N,len(pHs)))
    smallN = min(2 * cutoff+1, len(pos))
    smallI = np.diag(np.ones(smallN))

    alltuples =  [[int(c) for c in np.binary_repr(i, smallN)]
                  for i in range(2 ** (smallN))]
    gmatrix = [np.zeros((smallN, smallN)) for p in range(len(pHs))]

    #perform iterative fitting.........................
    for icycle in range(ncycles):
        ##print (icycle)

        if icycle == 0:
            fractionhold = np.array([[fun(pHs[p], pK0s[i], nH0s[i]) for i in range(N)] for p in range(len(pHs))])
        else:
            fractionhold = titration.transpose()

        for ires in range(1, N+1):

            (ileft,iright) = smallmatrixlimits(ires, cutoff, N)

            resi = smallmatrixpos(ires, cutoff, N)
#    print ires, resi, (ileft, iright)

            for p in range(len(pHs)):

                fraction = fractionhold[p].copy()
                fraction[ileft - 1 : iright] = 0
                charges = chargesempty + fraction
                ww0 = np.diag(np.dot(ww, charges) * 2)
                gmatrixfull =  ww + ww0 + pHs[p] * I - np.diag(pK0s)
                gmatrix[p] = gmatrixfull[ileft - 1 : iright, ileft - 1 : iright]

            E_all = np.array([sum([10 ** -(gmatrix[p] * np.outer(c,c)).sum() for c in alltuples]) for p in range(len(pHs))])
            E_sel = np.array([sum([10 ** -(gmatrix[p] * np.outer(c,c)).sum() for c in alltuples if c[resi-1] == 1]) for p in range(len(pHs))])
            titration[ires-1] = E_sel/E_all
        sol=np.array([curve_fit(fun, pHs, titration[p], [pK0s[p], nH0s[p]])[0] for p in range(len(pK0s))])
        (pKs, nHs) = sol.transpose()
        ##print (sol)

    dct={}
    for p,i in enumerate(pos):
        ##print (p,i,seq[i],pKs[p],nHs[p])
        dct[i-1]=(pKs[p],nHs[p],seq[i])

    return dct


##--------------- POTENCI core code and data tables from here -----------------

#AAstandard='ACDEFGHIKLMNPQRSTVY'
AAstandard='ACDEFGHIKLMNPQRSTVWY'

tablecent='''aa C CA CB N H HA HB
A 177.44069  52.53002  19.21113 125.40155   8.20964   4.25629   1.31544
C 174.33917  58.48976  28.06269 120.71212   8.29429   4.44261   2.85425
D 176.02114  54.23920  41.18408 121.75726   8.28460   4.54836   2.60054
E 176.19215  56.50755  30.30204 122.31578   8.35949   4.22124   1.92383
F 175.42280  57.64849  39.55984 121.30500   8.10906   4.57507   3.00036
G 173.83294  45.23929  None     110.09074   8.32746   3.91016   None
H 175.00142  56.20256  30.60335 120.69141   8.27133   4.55872   3.03080
I 175.88231  61.04925  38.68742 122.37586   8.06407   4.10574   1.78617
K 176.22644  56.29413  33.02478 122.71282   8.24902   4.25873   1.71982
L 177.06101  55.17464  42.29215 123.48611   8.14330   4.28545   1.54067
M 175.90708  55.50643  32.83806 121.54592   8.24848   4.41483   1.97585
N 174.94152  53.22822  38.87465 119.92746   8.37189   4.64308   2.72756
P 176.67709  63.05232  32.03750 137.40612   None      4.36183   2.03318
Q 175.63494  55.79861  29.44174 121.49225   8.30042   4.28006   1.97653
R 175.92194  56.06785  30.81298 122.40365   8.26453   4.28372   1.73437
S 174.31005  58.36048  63.82367 117.11419   8.25730   4.40101   3.80956
T 174.27772  61.86928  69.80612 115.48126   8.11378   4.28923   4.15465
V 175.80621  62.20156  32.77934 121.71912   8.06572   4.05841   1.99302
W 175.92744  57.23836  29.56502 122.10991   7.97816   4.61061   3.18540
Y 175.49651  57.82427  38.76184 121.43652   8.05749   4.51123   2.91782'''

def initcorcents():
    datc=tablecent.split('\n')
    aas=datc[0].split()[1:]
    dct={}
    for i in range(20):
        vals=datc[1+i].split()
        aai=vals[0]
        dct[aai]={}
        for j in range(7):
            atnj=aas[j]
            dct[aai][atnj]=eval(vals[1+j])
    return dct


tablenei='''C A  0.06131 -0.04544  0.14646  0.01305
 C C  0.04502  0.12592 -0.03407 -0.02654
 C D  0.08180 -0.08589  0.22948  0.10934
 C E  0.05388  0.22264  0.06962  0.01929
 C F -0.06286 -0.22396 -0.34442  0.00950
 C G  0.12772  0.72041  0.16048  0.01324
 C H -0.00628 -0.03355  0.13309 -0.03906
 C I -0.11709  0.06591 -0.06361 -0.03628
 C K  0.03368  0.15830  0.04518 -0.01576
 C L -0.03877  0.11608  0.02535  0.01976
 C M  0.04611  0.25233 -0.00747 -0.01624
 C N  0.07068 -0.06118  0.10077  0.05547
 C P -0.36018 -1.90872  0.16158 -0.05286
 C Q  0.10861  0.19878  0.01596 -0.01757
 C R  0.01933  0.13237  0.03606 -0.02468
 C S  0.09888  0.28691  0.07601  0.01379
 C T  0.05658  0.41659 -0.01103 -0.00114
 C V -0.11591  0.09565 -0.03355 -0.03368
 C W -0.01954 -0.19134 -0.37965  0.01582
 C Y -0.08380 -0.24519 -0.32700 -0.00577
CA A  0.03588  0.03480 -0.00468 -0.00920
CA C  0.02749  0.15742  0.14376  0.03681
CA D -0.00751  0.12494  0.17354  0.14157
CA E  0.00985  0.13936  0.03289 -0.00702
CA F  0.01122  0.03732 -0.19586 -0.00377
CA G -0.00885  0.23403 -0.03184 -0.01144
CA H -0.02102  0.04621  0.03122 -0.02826
CA I -0.00656  0.05965 -0.10588 -0.04372
CA K  0.01817  0.11216 -0.00341 -0.02950
CA L  0.04507  0.07829 -0.03526  0.00858
CA M  0.07553  0.18840  0.04987 -0.01749
CA N -0.00649  0.11842  0.18729  0.06401
CA P -0.27536 -2.02189  0.01327 -0.08732
CA Q  0.06365  0.15281  0.04575 -0.01356
CA R  0.04338  0.11783  0.00345 -0.02873
CA S  0.02867  0.07846  0.09443  0.02061
CA T -0.01625  0.10626  0.03880 -0.00126
CA V -0.04935  0.04248 -0.10195 -0.03778
CA W  0.00434  0.16188 -0.08742  0.03983
CA Y  0.02782  0.02846 -0.24750  0.00759
CB A -0.00953  0.05704 -0.04838  0.00755
CB C -0.00164  0.00760 -0.03293 -0.05613
CB D  0.02064  0.09849 -0.08746 -0.06691
CB E  0.01283  0.05404 -0.01342  0.02238
CB F  0.01028  0.03363  0.18112  0.01493
CB G -0.02758  0.04383  0.06071 -0.02639
CB H -0.01760 -0.02367  0.00343  0.00415
CB I  0.02783  0.01052  0.00641  0.05090
CB K  0.00350  0.02852 -0.00408  0.01218
CB L  0.01223 -0.02940 -0.07268  0.00884
CB M -0.02925 -0.03912 -0.06587  0.03490
CB N -0.02242  0.03403 -0.09759 -0.08018
CB P  0.08431 -0.35696 -0.04680  0.05192
CB Q -0.01649 -0.01016 -0.03663  0.01723
CB R -0.01887  0.00618 -0.00385  0.02884
CB S -0.00921  0.07096 -0.06338 -0.03707
CB T  0.02601  0.04904 -0.01728  0.00781
CB V  0.03068  0.06325  0.01928  0.05011
CB W -0.07651 -0.11334  0.13806 -0.03339
CB Y  0.00082  0.01466  0.18107 -0.01181
 N A  0.09963 -0.00873 -2.31666 -0.14051
 N C  0.11905 -0.01296  1.15573  0.01820
 N D  0.11783 -0.11817 -1.16322 -0.37601
 N E  0.10825 -0.00605 -0.41856  0.01187
 N F -0.12280 -0.27542  0.34635  0.09102
 N G  0.10365 -0.05667 -1.50346 -0.00146
 N H -0.04145 -0.26494  0.26356  0.18198
 N I -0.09249  0.12136  2.75071  0.40643
 N K -0.02472  0.07224 -0.07057  0.12261
 N L  0.01542 -0.12800 -0.85172 -0.15460
 N M -0.11266 -0.27311 -0.33192  0.09384
 N N -0.00295 -0.20562 -1.00652 -0.30971
 N P  0.03252  1.35296 -1.17173  0.06026
 N Q  0.00900 -0.09950 -0.07389  0.08415
 N R -0.07819  0.00802 -0.04821  0.08524
 N S  0.12057  0.02242  0.48924 -0.25423
 N T  0.04631  0.09935  1.02269  0.20228
 N V -0.03610  0.21959  2.42228  0.39686
 N W -0.15643 -0.19285  0.05515 -0.53172
 N Y -0.10497 -0.25228  0.46023  0.01399
 H A  0.01337 -0.00605 -0.04371 -0.02485
 H C  0.01324  0.05107  0.12857  0.00610
 H D  0.02859  0.02436 -0.06510  0.02085
 H E  0.02737  0.01790  0.03740  0.01969
 H F -0.02633 -0.08287 -0.11364 -0.03603
 H G  0.02753  0.05640 -0.10477  0.06876
 H H -0.00124 -0.02861  0.04126  0.10004
 H I -0.02258 -0.00929  0.07962  0.01880
 H K -0.00512 -0.00744  0.04443  0.03434
 H L -0.01088 -0.01230 -0.03640 -0.03719
 H M -0.01961 -0.00749 -0.00097  0.02041
 H N  0.01134  0.02121 -0.01837 -0.00629
 H P -0.01246  0.02956  0.13007 -0.00810
 H Q  0.00783  0.00751  0.05643  0.02413
 H R -0.00734  0.00546  0.07003  0.04051
 H S  0.02133  0.03964  0.04978 -0.03749
 H T  0.00976  0.06072  0.03531  0.01657
 H V -0.01267  0.00994  0.09630  0.03420
 H W -0.02348 -0.09617 -0.24207 -0.18741
 H Y -0.01881 -0.07345 -0.14345 -0.06721
HA A  0.00350 -0.02371 -0.00654  0.00652
HA C  0.00660  0.01073  0.01921  0.00919
HA D  0.01717 -0.00854 -0.00802 -0.00597
HA E  0.01090 -0.01091  0.00472  0.00790
HA F -0.02271 -0.06316 -0.03057 -0.02350
HA G  0.02155 -0.00151  0.02477  0.01526
HA H -0.01132 -0.05617 -0.01514  0.01264
HA I  0.00459  0.00571  0.02984  0.00416
HA K  0.00492 -0.01788  0.00555  0.01259
HA L -0.00599 -0.01558  0.00358  0.00167
HA M  0.00100 -0.02037  0.00678  0.00930
HA N  0.00651 -0.01499 -0.00361  0.00203
HA P  0.01542  0.28350 -0.01496  0.00796
HA Q  0.00711 -0.02142  0.00734  0.00971
HA R -0.00472 -0.01414  0.00966  0.01180
HA S  0.01572  0.02791  0.03762  0.00133
HA T  0.01714  0.06590  0.03085  0.00143
HA V  0.00777  0.01505  0.02525  0.00659
HA W -0.06818 -0.08412 -0.09386 -0.06072
HA Y -0.02701 -0.05585 -0.03243 -0.02987
HB A  0.01473  0.01843  0.01428  0.00451
HB C  0.01180  0.03340  0.03081  0.00169
HB D  0.01786  0.01626  0.02221  0.01030
HB E  0.01796  0.01820  0.00835 -0.00045
HB F -0.04867 -0.09154 -0.04858 -0.00164
HB G  0.01718  0.03852  0.01043  0.00051
HB H -0.00817 -0.04557 -0.00820  0.00855
HB I  0.00446  0.00111  0.00049 -0.00283
HB K  0.01570  0.01156  0.00771  0.00646
HB L  0.00700  0.01236  0.00880  0.00150
HB M  0.01607  0.02294  0.01385 -0.00038
HB N  0.01893  0.01561  0.02760  0.01215
HB P -0.01199 -0.02752  0.00891 -0.00033
HB Q  0.01636  0.01861  0.01177 -0.00099
HB R  0.01324  0.01526  0.01082  0.00378
HB S  0.01859  0.03487  0.02890 -0.00477
HB T  0.01624  0.04073  0.01936 -0.00348
HB V  0.00380  0.00271 -0.00144 -0.00315
HB W -0.09045 -0.06895 -0.10934 -0.01948
HB Y -0.05069 -0.06698 -0.05666 -0.01193'''

tabletermcorrs='''C n -0.15238
C c -0.90166
CB n 0.12064
CB c 0.06854
CA n -0.04616
CA c -0.06680
N n 0.347176
N c 0.619141
H n 0.156786
H c 0.023189
HB n 0.0052692
HB c 0.0310875
HA n 0.048624
HA c 0.042019'''

def initcorneis():
    datc=tablenei.split('\n')
    dct={}
    for i in range(20*7):
        vals=datc[i].split()
        atn=vals[0]
        aai=vals[1]
        if not aai in dct:dct[aai]={}
        dct[aai][atn]=[eval(vals[2+j]) for j in range(4)]
    datc=tabletermcorrs.split('\n')
    for i in range(len(datc)):
        vals=datc[i].split()
        atn=vals[0]
        term=vals[1]
        if not term in dct:dct[term]={}
        if term=='n':  dct['n'][atn]=[None,None,None,eval(vals[-1])]
        elif term=='c':dct['c'][atn]=[eval(vals[-1]),None,None,None]
    return dct


tabletempk='''aa  CA   CB   C     N    H    HA
A  -2.2  4.7 -7.1  -5.3 -9.0  0.7
C  -0.9  1.3 -2.6  -8.2 -7.0  0.0
D   2.8  6.5 -4.8  -3.9 -6.2 -0.1
E   0.9  4.6 -4.9  -3.7 -6.5  0.3
F  -4.7  2.4 -6.9 -11.2 -7.5  0.4
G   3.3  0.0 -3.2  -6.2 -9.1  0.0
H   7.8 15.5  3.1   3.3 -7.8  0.4
I  -2.0  4.6 -8.7 -12.7 -7.8  0.4
K  -0.8  2.4 -7.1  -7.6 -7.5  0.4
L   1.7  4.9 -8.2  -2.9 -7.5  0.1
M   4.1  9.4 -8.2  -6.2 -7.1 -0.5
N   2.8  5.1 -6.1  -3.3 -7.0 -2.9
P   1.1 -0.2 -4.0   0.0  0.0  0.0
Q   2.3  3.6 -5.7  -6.5 -7.2  0.3
R  -1.4  3.5 -6.9  -5.3 -7.1  0.4
S  -1.7  4.4 -4.7  -3.8 -7.6  0.1
T   0.0  2.2 -5.2  -6.7 -7.3  0.0
V  -2.8  2.5 -8.1 -14.2 -7.6  0.5
W  -2.7  3.1 -7.9 -10.1 -7.8  0.4
Y  -5.0  2.9 -7.7 -12.0 -7.7  0.5'''

def gettempkoeff():
    datc=tabletempk.split('\n')
    buf=[lin.split() for lin in datc]
    headers=buf[0][1:]
    dct={}
    for atn in headers:
        dct[atn]={}
    for lin in buf[1:]:
        aa=lin[0]
        for j,atn in enumerate(headers):
            dct[atn][aa]=eval(lin[1+j])
    return dct

tablecombdevs='''C -1 G r xrGxx  0.2742  1.4856
 C -1 G - x-Gxx  0.0522  0.2827
 C -1 P P xPPxx -0.0822  0.4450
 C -1 P r xrPxx  0.2640  1.4303
 C -1 r P xPrxx -0.1027  0.5566
 C -1 + P xP+xx  0.0714  0.3866
 C -1 - - x--xx -0.0501  0.2712
 C -1 p r xrpxx  0.0582  0.3151
 C  1 G r xxGrx  0.0730  0.3955
 C  1 P a xxPax -0.0981  0.5317
 C  1 P + xxP+x -0.0577  0.3128
 C  1 P p xxPpx -0.0619  0.3356
 C  1 r r xxrrx -0.1858  1.0064
 C  1 r a xxrax -0.1888  1.0226
 C  1 r + xxr+x -0.1805  0.9779
 C  1 r - xxr-x -0.1756  0.9512
 C  1 r p xxrpx -0.1208  0.6544
 C  1 + P xx+Px -0.0533  0.2886
 C  1 - P xx-Px  0.1867  1.0115
 C  1 p P xxpPx  0.2321  1.2574
 C -2 G r rxGxx -0.1457  0.7892
 C -2 r p pxrxx  0.0555  0.3008
 C  2 P P xxPxP  0.1007  0.5455
 C  2 P - xxPx-  0.0634  0.3433
 C  2 r P xxrxP -0.1447  0.7841
 C  2 a r xxaxr -0.1488  0.8061
 C  2 a - xxax- -0.0093  0.0506
 C  2 + G xx+xG -0.0394  0.2132
 C  2 + P xx+xP  0.1016  0.5502
 C  2 + a xx+xa  0.0299  0.1622
 C  2 + + xx+x+  0.0427  0.2312
 C  2 - a xx-xa  0.0611  0.3308
 C  2 p P xxpxP -0.0753  0.4078
CA -1 G P xPGxx -0.0641  0.3233
CA -1 G r xrGxx  0.2107  1.0630
CA -1 P P xPPxx -0.2042  1.0303
CA -1 P p xpPxx  0.0444  0.2240
CA -1 r G xGrxx  0.2030  1.0241
CA -1 r + x+rxx -0.0811  0.4093
CA -1 - P xP-xx  0.0744  0.3755
CA -1 - - x--xx -0.0263  0.1326
CA -1 p p xppxx -0.0094  0.0475
CA  1 G P xxGPx  1.3044  6.5813
CA  1 G - xxG-x -0.0632  0.3188
CA  1 P G xxPGx  0.2642  1.3329
CA  1 P P xxPPx  0.3025  1.5262
CA  1 P r xxPrx  0.1455  0.7343
CA  1 P - xxP-x  0.1188  0.5994
CA  1 P p xxPpx  0.1201  0.6062
CA  1 r P xxrPx -0.1958  0.9878
CA  1 r - xxr-x -0.0931  0.4696
CA  1 a P xxaPx -0.1428  0.7204
CA  1 a - xxa-x -0.0262  0.1324
CA  1 a p xxapx  0.0392  0.1977
CA  1 + P xx+Px -0.1059  0.5344
CA  1 + a xx+ax -0.0377  0.1901
CA  1 + + xx++x -0.0595  0.3001
CA  1 - P xx-Px -0.1156  0.5831
CA  1 - + xx-+x  0.0316  0.1593
CA  1 - p xx-px  0.0612  0.3090
CA  1 p r xxprx -0.0511  0.2576
CA -2 P - -xPxx -0.1028  0.5185
CA -2 r r rxrxx  0.1933  0.9752
CA -2 - G Gx-xx  0.0559  0.2818
CA -2 - p px-xx  0.0391  0.1973
CA -2 p a axpxx -0.0293  0.1479
CA -2 p + +xpxx -0.0173  0.0873
CA  2 G - xxGx-  0.0357  0.1802
CA  2 + G xx+xG -0.0315  0.1591
CA  2 - P xx-xP  0.0426  0.2150
CA  2 - r xx-xr  0.0784  0.3954
CA  2 - a xx-xa  0.1084  0.5467
CA  2 - - xx-x-  0.0836  0.4216
CA  2 p P xxpxP  0.0685  0.3456
CA  2 p - xxpx- -0.0481  0.2428
CB -1 P r xrPxx -0.2678  1.7345
CB -1 P p xpPxx  0.0355  0.2300
CB -1 r P xPrxx -0.1137  0.7367
CB -1 a p xpaxx  0.0249  0.1613
CB -1 + - x-+xx -0.0762  0.4935
CB -1 - P xP-xx -0.0889  0.5757
CB -1 - r xr-xx -0.0533  0.3451
CB -1 - - x--xx  0.0496  0.3215
CB -1 - p xp-xx -0.0148  0.0960
CB -1 p P xPpxx  0.0119  0.0768
CB -1 p r xrpxx -0.0673  0.4358
CB  1 P G xxPGx -0.0522  0.3379
CB  1 P P xxPPx -0.8458  5.4779
CB  1 P r xxPrx -0.1573  1.0187
CB  1 r r xxrrx  0.1634  1.0581
CB  1 a G xxaGx -0.0393  0.2544
CB  1 a r xxarx  0.0274  0.1777
CB  1 a - xxa-x  0.0394  0.2553
CB  1 a p xxapx  0.0149  0.0968
CB  1 + G xx+Gx -0.0784  0.5076
CB  1 + P xx+Px -0.1170  0.7580
CB  1 - P xx-Px -0.0913  0.5912
CB  1 - - xx--x  0.0284  0.1838
CB  1 p P xxpPx  0.0880  0.5697
CB  1 p p xxppx -0.0113  0.0733
CB -2 P - -xPxx  0.0389  0.2521
CB -2 P p pxPxx  0.0365  0.2362
CB -2 r + +xrxx  0.0809  0.5242
CB -2 a - -xaxx -0.0452  0.2927
CB -2 + - -x+xx -0.0651  0.4218
CB -2 - G Gx-xx -0.0883  0.5717
CB -2 p G Gxpxx  0.0378  0.2445
CB -2 p p pxpxx  0.0207  0.1341
CB  2 r G xxrxG -0.0362  0.2344
CB  2 r - xxrx- -0.0219  0.1419
CB  2 a - xxax- -0.0298  0.1929
CB  2 + p xx+xp  0.0189  0.1223
CB  2 - - xx-x- -0.0525  0.3400
 N -1 G P xPGxx  0.2411  0.5105
 N -1 G + x+Gxx -0.1773  0.3754
 N -1 G - x-Gxx  0.1905  0.4035
 N -1 P P xPPxx -0.9177  1.9434
 N -1 P p xpPxx  0.2609  0.5525
 N -1 r G xGrxx  0.2417  0.5119
 N -1 r a xarxx -0.0139  0.0295
 N -1 r + x+rxx -0.4122  0.8729
 N -1 r p xprxx  0.1440  0.3049
 N -1 a G xGaxx -0.5177  1.0963
 N -1 a r xraxx  0.0890  0.1885
 N -1 a a xaaxx  0.1393  0.2950
 N -1 a p xpaxx -0.0825  0.1747
 N -1 + G xG+xx -0.4908  1.0394
 N -1 + a xa+xx  0.1709  0.3619
 N -1 + + x++xx  0.1868  0.3955
 N -1 + - x-+xx -0.0951  0.2014
 N -1 - P xP-xx -0.3027  0.6410
 N -1 - r xr-xx -0.1670  0.3537
 N -1 - + x+-xx -0.3501  0.7414
 N -1 - - x--xx  0.1266  0.2681
 N -1 p G xGpxx -0.1707  0.3614
 N -1 p - x-pxx  0.0011  0.0023
 N  1 G G xxGGx  0.2555  0.5412
 N  1 G P xxGPx -0.9725  2.0595
 N  1 G r xxGrx  0.0165  0.0349
 N  1 G p xxGpx  0.0703  0.1489
 N  1 r a xxrax -0.0237  0.0503
 N  1 a r xxarx -0.1816  0.3845
 N  1 a - xxa-x -0.1050  0.2224
 N  1 a p xxapx -0.1196  0.2533
 N  1 - r xx-rx -0.1762  0.3731
 N  1 - a xx-ax  0.0006  0.0013
 N  1 p P xxpPx  0.2797  0.5923
 N  1 p a xxpax  0.0938  0.1986
 N  1 p + xxp+x  0.1359  0.2878
 N -2 G r rxGxx -0.5140  1.0885
 N -2 G - -xGxx -0.0639  0.1354
 N -2 P P PxPxx -0.4215  0.8927
 N -2 r P Pxrxx -0.3696  0.7828
 N -2 r p pxrxx -0.1937  0.4101
 N -2 a - -xaxx -0.0351  0.0743
 N -2 a p pxaxx -0.1031  0.2183
 N -2 - G Gx-xx -0.2152  0.4558
 N -2 - P Px-xx -0.1375  0.2912
 N -2 - p px-xx -0.1081  0.2290
 N -2 p P Pxpxx -0.1489  0.3154
 N -2 p - -xpxx  0.0952  0.2015
 N  2 G - xxGx-  0.1160  0.2457
 N  2 r p xxrxp -0.1288  0.2728
 N  2 a P xxaxP  0.1632  0.3456
 N  2 + + xx+x+ -0.0106  0.0226
 N  2 + - xx+x-  0.0389  0.0824
 N  2 - a xx-xa -0.0815  0.1726
 N  2 p G xxpxG -0.0779  0.1649
 N  2 p p xxpxp -0.0683  0.1447
 H -1 G P xPGxx -0.0317  0.4730
 H -1 G r xrGxx  0.0549  0.8186
 H -1 G + x+Gxx -0.0192  0.2867
 H -1 G - x-Gxx  0.0138  0.2055
 H -1 r P xPrxx -0.0964  1.4367
 H -1 r - x-rxx -0.0245  0.3648
 H -1 a G xGaxx -0.0290  0.4320
 H -1 a a xaaxx  0.0063  0.0944
 H -1 + G xG+xx -0.0615  0.9168
 H -1 + r xr+xx -0.0480  0.7153
 H -1 + - x-+xx -0.0203  0.3030
 H -1 - + x+-xx -0.0232  0.3455
 H -1 p G xGpxx -0.0028  0.0411
 H -1 p P xPpxx -0.0121  0.1805
 H  1 G P xxGPx -0.1418  2.1144
 H  1 G r xxGrx  0.0236  0.3520
 H  1 G a xxGax  0.0173  0.2580
 H  1 a - xxa-x  0.0091  0.1349
 H  1 + P xx+Px -0.0422  0.6290
 H  1 + p xx+px  0.0191  0.2842
 H  1 - P xx-Px -0.0474  0.7065
 H  1 - a xx-ax  0.0102  0.1515
 H -2 G G GxGxx  0.0169  0.2517
 H -2 G r rxGxx -0.3503  5.2220
 H -2 a P Pxaxx  0.0216  0.3227
 H -2 a - -xaxx -0.0276  0.4118
 H -2 + - -x+xx -0.0260  0.3874
 H -2 - G Gx-xx  0.0273  0.4073
 H -2 - a ax-xx -0.0161  0.2400
 H -2 - - -x-xx -0.0285  0.4255
 H -2 p P Pxpxx -0.0101  0.1503
 H -2 p a axpxx -0.0157  0.2343
 H -2 p + +xpxx -0.0122  0.1815
 H -2 p p pxpxx  0.0107  0.1601
 H  2 G G xxGxG -0.0190  0.2826
 H  2 r G xxrxG  0.0472  0.7036
 H  2 r P xxrxP  0.0337  0.5027
 H  2 a + xxax+ -0.0159  0.2376
 H  2 + G xx+xG  0.0113  0.1685
 H  2 + r xx+xr -0.0307  0.4575
 H  2 - P xx-xP -0.0088  0.1318
HA -1 P P xPPxx  0.0307  1.1685
HA -1 P r xrPxx  0.0621  2.3592
HA -1 r G xGrxx -0.0371  1.4092
HA -1 r + x+rxx  0.0125  0.4733
HA -1 r p xprxx -0.0199  0.7569
HA -1 a G xGaxx  0.0073  0.2779
HA -1 a a xaaxx  0.0044  0.1683
HA -1 - G xG-xx  0.0116  0.4409
HA -1 - r xr-xx  0.0228  0.8679
HA -1 - p xp-xx  0.0074  0.2828
HA  1 G G xxGGx  0.0175  0.6636
HA  1 G - xxG-x  0.0107  0.4081
HA  1 P a xxPax  0.0089  0.3369
HA  1 - r xx-rx  0.0113  0.4291
HA -2 G G GxGxx -0.0154  0.5847
HA -2 P - -xPxx  0.0136  0.5179
HA -2 r G Gxrxx -0.0159  0.6045
HA -2 + + +x+xx -0.0137  0.5190
HA -2 p - -xpxx -0.0068  0.2592
HA -2 p p pxpxx  0.0046  0.1763
HB -1 P r xrPxx  0.0460  2.1365
HB -1 a - x-axx  0.0076  0.3551
HB -1 + - x-+xx  0.0110  0.5122
HB -1 - r xr-xx  0.0233  1.0819
HB  1 a P xxaPx  0.0287  1.3310
HB  1 + P xx+Px  0.0324  1.5056
HB  1 + r xx+rx -0.0231  1.0709
HB  1 p r xxprx  0.0077  0.3586
HB  1 p + xxp+x -0.0074  0.3426
HB -2 a P Pxaxx -0.0026  0.1192
HB -2 a r rxaxx -0.0098  0.4559
HB -2 - - -x-xx  0.0016  0.0751
HB  2 P r xxPxr -0.0595  2.7608
HB  2 P + xxPx+ -0.0145  0.6744
HB  2 P - xxPx-  0.0107  0.4976
HB  2 a + xxax+ -0.0015  0.0691
HB  2 p r xxpxr  0.0262  1.2178'''

tablephshifts='''
D (pKa 3.86)
D H  8.55 8.38 -0.17 0.02 -0.03
D HA 4.78 4.61 -0.17 0.01 -0.01
D HB 2.93 2.70 -0.23
D CA 52.9 54.3 1.4 0.0 0.1
D CB 38.0 41.1 3.0
D CG 177.1 180.3 3.2
D C  175.8 176.9 1.1 -0.2 0.4
D N  118.7 120.2 1.5  0.3 0.1
D Np na na 0.1
E (pKa 4.34)
E H  8.45 8.57  0.12 0.00 0.02
E HA 4.39 4.29 -0.10 0.01 0.00
E HB 2.08 2.02 -0.06
E HG 2.49 2.27 -0.22
E CA 56.0 56.9 1.0 0.0 0.0
E CB 28.5 30.0 1.5
E CG 32.7 36.1 3.5
E CD 179.7 183.8 4.1
E C  176.5 177.0 0.6  0.1 0.1
E N  119.9 120.9 1.0  0.2 0.1
E Np na na 0.1
H (pKa 6.45)
H H  8.55 8.35 -0.2  -0.01  0.0
H HA 4.75 4.59 -0.2  -0.01 -0.06
H HB 3.25 3.08 -0.17
H HD2 7.30 6.97 -0.33
H HE1 8.60 7.68 -0.92
H CA 55.1 56.7 1.6 -0.1 0.1
H CB 28.9 31.3 2.4
H CG 131.0 135.3 4.2
H CD2 120.3 120.0 -0.3
H CE1 136.6 139.2 2.6
H C 174.8 176.2 1.5  0.0 0.6
H N 117.9 119.7 1.8  0.3 0.5
H Np na na 0.5
H ND1 175.8 231.3 56
H NE2 173.1 181.1 8
C (pKa 8.49)
C H 8.49 8.49 0.0
C HA 4.56 4.28 -0.28 -0.01 -0.01
C HB 2.97 2.88 -0.09
C CA 58.5 60.6 2.1 0.0 0.1
C CB 28.0 29.7 1.7
C C 175.0 176.9 1.9 -0.4 0.5
C N 118.7 122.2 3.6  0.4 0.6
C Np na na 0.6
Y (pKa 9.76)
Y H  8.16 8.16 0.0
Y HA 4.55 4.49 -0.06
Y HB 3.02 2.94 -0.08
Y HD 7.14 6.97 -0.17
Y HE 6.85 6.57 -0.28
Y CA 58.0 58.2 0.3
Y CB 38.6 38.7 0.1
Y CG 130.5 123.8 -6.7
Y CD 133.3 133.2 -0.1
Y CE 118.4 121.7 3.3
Y CZ 157.0 167.4 10.4
Y C 176.3 176.7 0.4
Y N 120.1 120.7 0.6
K (pKa 10.34)
K H  8.4  8.4  0.0
K HA 4.34 4.30 -0.04
K HB 1.82 1.78 -0.04
K HG 1.44 1.36 -0.08
K HD 1.68 1.44 -0.24
K HE 3.00 2.60 -0.40
K CA 56.4 56.9 0.4
K CB 32.8 33.2 0.3
K CG 24.7 25.0 0.4
K CD 28.9 33.9 5.0
K CE 42.1 43.1 1.0
K C 177.0 177.5 0.5
K N 121.0 121.7 0.7
K Np na na 0.1
R (pKa 13.9)
R H  7.81 7.81 0.0
R HA 3.26 3.19 -0.07
R HB 1.60 1.55 0.05
R HG 1.60 1.55 0.05
R HD 3.19 3.00 -0.19
R CA 58.4 58.6 0.2
R CB 34.4 35.2 0.9
R CG 27.2 28.1 1.0
R CD 43.8 44.3 0.5
R CZ 159.6 163.5 4.0
R C 185.8 186.1 0.2
R N 122.4 122.8 0.4
R NE 85.6 91.5 5.9
R NG 71.2 93.2 22'''

def initcorrcomb():
    datc=tablecombdevs.split('\n')
    buf=[lin.split() for lin in datc]
    dct={}
    for lin in buf:
        atn=lin[0]
        if not atn in dct:dct[atn]={}
        neipos=int(lin[1])
        centgroup=lin[2]
        neigroup= lin[3]
        key=(neipos,centgroup,neigroup)#(k,l,m)
        segment=lin[4]
        dct[atn][segment]=key,eval(lin[-2])
    return dct

TEMPCORRS=gettempkoeff()
##dct[atn][aa]=eval(lin[1+j])
CENTSHIFTS=initcorcents()
##dct[aai][atnj]=eval(vals[1+j])
NEICORRS =initcorneis()
##dct[aai][atn]=[eval(vals[2+j]) for j in range(4)]
COMBCORRS=initcorrcomb()
##dct[atn][segment]=key,eval(lin[-1])

def predPentShift(pent,atn):
    aac=pent[2]
    sh=CENTSHIFTS[aac][atn]
    allneipos=[2,1,-1,-2]
    for i in range(4):
        aai=pent[2+allneipos[i]]
        if aai in NEICORRS:
            corr=NEICORRS[aai][atn][i]
            sh+=corr
    groups=['G','P','FYW','LIVMCA','KR','DE']##,'NQSTHncX']
    labels='GPra+-p' #(Gly,Pro,Arom,Aliph,pos,neg,polar)
    grstr=''
    for i in range(5):
        aai=pent[i]
        found=False
        for j,gr in enumerate(groups):
            if aai in gr:
                grstr+=labels[j]
                found=True
                break
        if not found:grstr+='p'#polar
    centgr=grstr[2]
    for segm in COMBCORRS[atn]:
        key,combval=COMBCORRS[atn][segm]
        neipos,centgroup,neigroup=key#(k,l,m)
        if centgroup==centgr and grstr[2+neipos]==neigroup:
            if (centgr,neigroup)!=('p','p') or pent[2] in 'ST':
            #pp comb only used when center is Ser or Thr!
                sh+=combval
    return sh

def gettempcorr(aai,atn,tempdct,temp):
    return tempdct[atn][aai]/1000*(temp-298)

def get_phshifts():
    datc=tablephshifts.split('\n')
    buf=[lin.split() for lin in datc]
    dct={}
    na=None
    for lin in buf:
        if len(lin)>3:
            resn=lin[0]
            atn=lin[1]
            sh0=eval(lin[2])
            sh1=eval(lin[3])
            shd=eval(lin[4])
            if not resn in dct:dct[resn]={}
            dct[resn][atn]=shd
            if len(lin)>6:#neighbor data
                for n in range(2):
                    shdn=eval(lin[5+n])
                    nresn=resn+'ps'[n]
                    if not nresn in dct:dct[nresn]={}
                    dct[nresn][atn]=shdn
    return dct

def initfilcsv(filename):
    file=open(filename,'r')
    buffer=file.readlines()
    file.close()
    for i in range(len(buffer)):
        buffer[i]=buffer[i][:-1].split(',')
    return buffer

def write_csv_pkaoutput(pkadct,seq,temperature,ion):
    seq=seq[:min(150,len(seq))]
    name='outpepKalc_%s_T%6.2f_I%4.2f.csv'%(seq,temperature,ion)
    out=open(name,'w')
    out.write('Site,pKa value,pKa shift,Hill coefficient\n')
    for i in pkadct:
        pKa,nH,resi=pkadct[i]
        reskey=resi+str(i+1)
        diff=pKa-pK0[resi]
        out.write('%s,%5.3f,%5.3f,%5.3f\n'%(reskey,pKa,diff,nH))
    out.close()

def read_csv_pkaoutput(seq,temperature,ion,name=None):
    seq=seq[:min(150,len(seq))]
    if VERB:print('reading csv',name)
    if name==None:name='outpepKalc_%s_T%6.2f_I%4.2f.csv'%(seq,temperature,ion)
    try:out=open(name,'r')
    except IOError:return None
    buf=initfilcsv(name)
    for lnum,data in enumerate(buf):
        if len(data)>0 and data[0]=='Site':break
    pkadct={}
    for data in buf[lnum+1:]:
        reskey,pKa,diff,nH=data
        i=int(reskey[1:])-1
        resi=reskey[0]
        pKaval=eval(pKa)
        nHval=eval(nH)
        pkadct[i]=pKaval,nHval,resi
    return pkadct

def getphcorrs(seq,temperature,pH,ion,pkacsvfilename=None):
    bbatns=['C','CA','CB','HA','H','N','HB']
    dct=get_phshifts()
    Ion=max(0.0001,ion)
    pkadct=read_csv_pkaoutput(seq,temperature,ion,pkacsvfilename)
    if pkadct==None:
        pkadct=calc_pkas_from_seq('n'+seq+'c',temperature,Ion)
        write_csv_pkaoutput(pkadct,seq,temperature,ion)
    outdct={}
    for i in pkadct:
        if VERB:print('pkares: %6.3f %6.3f %1s'%pkadct[i],i)
        pKa,nH,resi=pkadct[i]
        frac =fun(pH,pKa,nH)
        frac7=fun(7.0,pK0[resi],nH)
        if resi in 'nc':jump=0.0#so far
        else:
            for atn in bbatns:
                if not atn in outdct:outdct[atn]={}
                if VERB:print('data:',atn,pKa,nH,resi,i,atn,pH)
                dctresi=dct[resi]
                try:
                    delta=dctresi[atn]
                    jump =frac *delta
                    jump7=frac7*delta
                    key=(resi,atn)
                except KeyError:
                    ##if not (resi in 'RKCY' and atn=='H') and not (resi == 'R' and atn=='N'):
                    print('warning no key:',resi,i,atn)
                    delta=999;jump=999;jump7=999
                if delta<99:
                    jumpdelta=jump-jump7
                    if not i in outdct[atn]:outdct[atn][i]=[resi,jumpdelta]
                    else:
                        outdct[atn][i][0]=resi
                        outdct[atn][i][1]+=jumpdelta
                    if VERB:print('%3s %5.2f %6.4f %s %3d %5s %8.5f %8.5f %4.2f'%(atn,pKa,nH,resi,i,atn,jump,jump7,pH))
                    if resi+'p' in dct and atn in dct[resi+'p']:
                        for n in range(2):
                            ni=i+2*n-1
                            ##if ni is somewhere in seq...
                            nresi=resi+'ps'[n]
                            ndelta=dct[nresi][atn]
                            jump =frac *ndelta
                            jump7=frac7*ndelta
                            jumpdelta=jump-jump7
                            if not ni in outdct[atn]:outdct[atn][ni]=[None,jumpdelta]
                            else:outdct[atn][ni][1]+=jumpdelta
    return outdct

def getpredshifts(seq,temperature,pH,ion,usephcor=True,pkacsvfile=None,identifier=''):
    tempdct=gettempkoeff()
    bbatns =['C','CA','CB','HA','H','N','HB']
    if usephcor:
        phcorrs=getphcorrs(seq,temperature,pH,ion,pkacsvfile)
    else:phcorrs={}
    shiftdct={}
    for i in range(1,len(seq)-1):
        if seq[i] in AAstandard:#else: do nothing
            res=str(i+1)
            trip=seq[i-1]+seq[i]+seq[i+1]
            phcorr=None
            shiftdct[(i+1,seq[i])]={}
            for at in bbatns:
                if not (trip[1],at) in [('G','CB'),('G','HB'),('P','H')]:
                    if i==1:
                        pent='n'+     trip+seq[i+2]
                    elif i==len(seq)-2:
                        pent=seq[i-2]+trip+'c'
                    else:
                        pent=seq[i-2]+trip+seq[i+2]
                    shp=predPentShift(pent,at)
                    if shp!=None:
                        if not (at in ('CA','CB') and seq[i]=='C'):
                            if at!='HB':shp+=gettempcorr(trip[1],at,tempdct,temperature)
                            if at in phcorrs and i in phcorrs[at]:
                                phdata=phcorrs[at][i]
                                resi=phdata[0]
                                ##assert resi==seq[i]
                                if seq[i] in 'CDEHRKY' and resi!=seq[i]:
                                    print('WARNING: residue mismatch',resi,seq[i],i,phdata,at)
                                phcorr=phdata[1]
                                if abs(phcorr)<9.9:
                                    shp-=phcorr
                            shiftdct[(i+1,seq[i])][at]=shp
                            if VERB:print('predictedshift: %5s %3d %1s %2s %8.4f'%(identifier,i,seq[i],at,shp),phcorr)
    return shiftdct

def writeOutput(name,dct):
    try:out=open(name,'w')
    except IOError:
        print('warning file name too long!',len(name),name)
        subnames=name.split('_')
        name='_'.join([subnames[0]]+[subnames[1][:120]]+subnames[2:])
        out=open(name,'w')
    bbatns =['N','C','CA','CB','H','HA','HB']
    out.write('#NUM AA   N ')
    out.write(' %7s %7s %7s %7s %7s %7s\n'%tuple(bbatns[1:]))
    reskeys=list(dct.keys());reskeys.sort()
    for resnum,resn in reskeys:
        shdct=dct[(resnum,resn)]
        if len(shdct)>0:
            out.write('%-4d %1s '%(resnum,resn))
            for at in bbatns:
                shp=0.0
                if at in shdct:shp=shdct[at]
                out.write(' %7.3f'%shp)
        out.write('\n')
    out.close()

def potenci(seq,pH=7.0,temp=298,ion=0.1,pkacsvfile=None,doreturn=True):
    ##README##......
    #requires: python with numpy and scipy
    #usage: potenci1_0.py seqstring pH temp ionicstrength [pkacsvfile] > logfile
    #optional filename in csv format contained predicted pKa values and Hill parameters,
    #the format of the pkacsvfile must be the same as the output for pepKalc,
    #only lines after "Site" is read. If this is not found no pH corrections are applied.
    #Output: Table textfile in SHIFTY format (space separated)
    #average of methylene protons are provided for Gly HA2/HA3 and HB2/HB3.
    #NOTE:pH corrections is applied if pH is not 7.0
    #NOTE:pKa predictions are stored locally and reloaded if the seq, temp and ion is the same.
    #NOTE:at least 5 residues are required. Chemical shift predictions are not given for terminal residues.
    #NOTE:change the value of VERB in the top of this script to have verbose logfile
    ##name='outPOTENCI_%s_T%6.2f_I%4.2f_pH%4.2f.txt'%(seq,temp,ion,pH)
    name='outPOTENCI_%s_T%6.2f_I%4.2f_pH%4.2f.txt'%(seq[:min(150,len(seq))],temp,ion,pH)
    usephcor = pH<6.99 or pH>7.01
    if len(seq)<5:
        print('FAILED: at least 5 residues are required (exiting)')
        raise SystemExit
    #------------- now ready to generate predicted shifts ---------------------
    print('predicting random coil chemical shift with POTENCI using:',seq,pH,temp,ion,pkacsvfile)
    shiftdct=getpredshifts(seq,temp,pH,ion,usephcor,pkacsvfile)
    #------------- write output nicely is SHIFTY format -----------------------$
    writeOutput(name,shiftdct)
    print('chemical shift succesfully predicted, see output:',name)
    if doreturn: return shiftdct

histdct_flattened=(2.0737054913103337e-10, 0.029518200092680934, 0.97048179969994852, 8.9102609389174977e-10, 0.049071251975264775, 0.95092874713370923, 3.6911845844839106e-09, 0.079951554923860677, 0.92004844138495467, 1.4645276032946968e-08, 0.12682756718735982, 0.87317241816736413, 5.5170502882584017e-08, 0.19418179262213037, 0.80581815220736663, 1.9535866625876679e-07, 0.28408625538027543, 0.71591354926105832, 6.4415744419331008e-07, 0.39341966288684982, 0.60657969295570613, 0.52492556339882823, 0.24358165501654738, 0.2314927815846245, 5.5564750876404044e-06, 0.62885124891949329, 0.37114319460541911, 2.1057352549240146e-05, 0.61171750797158275, 0.38826143467586793, 3.0971176979542517e-05, 0.51981670536451852, 0.48015232345850201, 7.915310450907783e-05, 0.61884065214048178, 0.38108019475500915, 0.00045690835118482965, 0.79503735616235505, 0.20450573548646017, 0.00037479162478264302, 0.35106708082817562, 0.64855812754704179, 0.00095386218989570288, 0.57450903465177372, 0.4245371031583306, 0.0020603975788089112, 0.61761448046266132, 0.38032512195852974, 0.10697471251615311, 0.740936476567855, 0.15208881091599186, 0.19327399498223335, 0.66933460014069035, 0.13739140487707624, 0.012958657581034067, 0.8553594104147666, 0.13168193200419931, 0.091851181267882026, 0.77756153682517193, 0.13058728190694613, 0.22921634513601896, 0.70560705274133872, 0.065176602122642202, 0.17138260006224124, 0.74739765730864161, 0.081219742629117173, 0.39611931387854205, 0.53348400777148219, 0.070396678349975719, 0.32077386008589764, 0.67887372861950723, 0.00035241129459517807, 0.34547036052878238, 0.53173852579655434, 0.12279111367466328, 0.15654016376325999, 0.84329817825782072, 0.00016165797891921677, 0.609236196608406, 0.39071653468646333, 4.7268705130734661e-05, 0.56507190622112824, 0.43487160797697183, 5.6485801899947119e-05, 0.72211884215624933, 0.27786639061478047, 1.4767228970310703e-05, 0.89076020079356311, 0.1092234770391385, 1.6322167298468004e-05, 0.9651593658187213, 0.034836824638462209, 3.8095428165094679e-06, 0.98971313476752076, 0.010286035965388558, 8.2926709062859595e-07, 0.96981453223812519, 0.03018366029636706, 1.8074655077167692e-06, 0.9800419677234179, 0.019957137967335396, 8.9430924670088857e-07, 0.9866363147631777, 0.013363233763595815, 4.5147322651919685e-07, 1.9109838135778465e-10, 0.023630638204507205, 0.97636936160439436, 8.2442113579148138e-10, 0.039442231792554197, 0.96055776738302479, 3.4371676755121813e-09, 0.064675160889006281, 0.93532483567382607, 1.3771494331934358e-08, 0.10360311557528777, 0.89639687065321794, 5.2622165192033297e-08, 0.16089625102505495, 0.83910369635277982, 1.8996806314544746e-07, 0.23997930062335224, 0.76002050940858468, 6.4159584961185574e-07, 0.34040915035607228, 0.65959020804807811, 1.6142671821825171e-06, 0.3656723330296458, 0.63432605270317199, 7.9306224762809292e-06, 0.42167471692381381, 0.57831735245370997, 1.4331997234628106e-05, 0.62168294461968965, 0.37830272338307569, 8.5079831053122454e-05, 0.35116882723558307, 0.64874609293336394, 0.00023739564627928063, 0.60858211393349881, 0.39118049042022185, 0.00027350017133546272, 0.35110265425567283, 0.64862384557299169, 0.0013094397503175168, 0.80436154464227105, 0.19432901560741142, 0.0011593081625392108, 0.6181721553663625, 0.38066853647109822, 0.0017483116290761852, 0.60143525528397734, 0.39681643308694647, 0.062346515643269242, 0.67173435620272981, 0.26591912815400082, 0.12117764676552746, 0.79268160196400617, 0.086140751270466262, 0.025364944414347012, 0.96071846892327084, 0.013916586662382227, 0.1253815227369563, 0.86842714038053614, 0.0061913368825075822, 0.035564561379828476, 0.71161999636365836, 0.25281544225651315, 0.05127083074821575, 0.94697591712442863, 0.0017532521273556747, 0.33683647246616599, 0.66246322641254274, 0.00070030112129126204, 0.20613528440390783, 0.7931944731511591, 0.00067024244493308304, 0.25475130826701098, 0.74500186152316994, 0.00024683020981902096, 0.38096153535572541, 0.618941435995089, 9.7028649185720704e-05, 0.4380554386001887, 0.56186912046014503, 7.5440939666278716e-05, 0.72201381857408975, 0.27782597825880734, 0.00016020316710293287, 0.46415121975875845, 0.53580664263808608, 4.2137603155417023e-05, 0.83863471128469635, 0.16135044999873116, 1.483871657248392e-05, 0.9127086014213116, 0.087279403938147634, 1.1994640540753855e-05, 0.95968276815616971, 0.040313147387399932, 4.0844564303048067e-06, 0.97959790349402753, 0.020400561247868244, 1.5352581042162526e-06, 0.98243937381474755, 0.017559637299381859, 9.8888587070698638e-07, 0.98837030712191354, 0.01162919912319507, 4.9375489140841599e-07, 1.7586070645157005e-10, 0.018919495073917988, 0.98108050475022135, 7.6114140518621012e-10, 0.031681081386595179, 0.96831891785226343, 1.5738979951325724e-09, 0.025765327484998785, 0.97423467094110328, 1.2883779943905633e-08, 0.084325190757747803, 0.91567479635847215, 4.9822664459746072e-08, 0.13253373783046729, 0.86746621234686827, 1.938707366951566e-07, 0.21307266355241578, 0.78692714257684759, 6.3126935162206797e-07, 0.29139135982217446, 0.70860800890847397, 3.1778932524635995e-06, 0.35119759109025267, 0.64879923101649484, 7.3222033521025827e-06, 0.62630845676289149, 0.37368422103375648, 3.5011493538620542e-05, 0.51981460507542765, 0.48015038343103372, 7.1272798885618945e-05, 0.15284352413112626, 0.84708520306998814, 0.00015475183905515138, 0.72141337200465983, 0.27843187615628495, 0.00027694019364964242, 0.43099593807618158, 0.56872712173016882, 0.0005940761539064874, 0.47400377256513898, 0.52540215128095458, 0.002552483169753832, 0.70714312419390568, 0.29030439263634056, 0.048136277614296952, 0.81499045482398769, 0.13687326756171533, 0.090692589975098353, 0.65142724668963636, 0.25788016333526537, 0.03745858302666627, 0.74951793816703616, 0.21302347880629754, 0.029535710506623215, 0.88648086977008478, 0.083983419723291999, 0.10213292270407413, 0.89080113308337361, 0.0070659442125522078, 0.08366492548264258, 0.8370359658293498, 0.079299108688007519, 0.24465858755181566, 0.7531436066998346, 0.0021978057483498241, 0.33657682568722619, 0.66195257374585037, 0.0014706005669234679, 0.40230659369205496, 0.59710432564384208, 0.00058908066410307588, 0.29238446867227558, 0.70719027286905833, 0.00042525845866613841, 0.40491597418577552, 0.59490669737192015, 0.00017732844230438293, 0.56505048739799879, 0.4348551243437338, 9.4388258267336206e-05, 0.56506660125667107, 0.4348675253489056, 6.5873394423309603e-05, 0.7958164435359204, 0.2041498156516921, 3.3740812387630269e-05, 0.68409674991869873, 0.31588289954646637, 2.0350534834945435e-05, 0.94542022483429133, 0.054570363018285849, 9.4121474229599436e-06, 0.92863027799932507, 0.071360647917449158, 9.0740832258402936e-06, 0.93479652168789862, 0.065197320514038481, 6.1577980629425805e-06, 0.98484176376230692, 0.015157164952703448, 1.071284989674963e-06, 0.98799996363359788, 0.011999396959327391, 6.3940707466488445e-07, 1.6165617676271101e-10, 0.015153116260222027, 0.98484688357812189, 7.0147936153724939e-10, 0.025440079913643904, 0.97455991938487674, 2.9521305956832856e-09, 0.042107899156463249, 0.95789209789140617, 1.2002430192798381e-08, 0.068446641981493875, 0.93155334601607587, 3.9989238031081283e-08, 0.23965735406034891, 0.76034260595041314, 1.8473809999672171e-07, 0.17690531070607751, 0.82309450455582256, 1.1311414665106574e-06, 0.45493338944441802, 0.54506547941411554, 3.5240316153704533e-06, 0.60512861536107743, 0.39486786060730722, 9.7525092748002545e-06, 0.72682822772674927, 0.27316201976397597, 2.0861086226669762e-05, 0.6859466903146072, 0.31403244859916624, 5.332729240920751e-05, 0.18829335186004104, 0.81165332084754971, 0.00025945729180097395, 0.47416247745093659, 0.52557806525726247, 0.00035725454767968995, 0.43592108982262995, 0.56372165562969045, 0.0010897843172447664, 0.38177825445219243, 0.6171319612305628, 0.0018591181203997816, 0.53394779913297052, 0.46419308274662957, 0.0045928219568831148, 0.57925391139005111, 0.41615326665306585, 0.031283424727716821, 0.74633416562103239, 0.22238240965125072, 0.10385850320845873, 0.85922689359944548, 0.036914603192095684, 0.11120289139689665, 0.77022201413565816, 0.11857509446744517, 0.043321716017784687, 0.83349499849331521, 0.12318328548890009, 0.21041134479899304, 0.69754328950803046, 0.092045365692976513, 0.2123196322567944, 0.7625253259234076, 0.0251550418197981, 0.3312304844007723, 0.64398429234572929, 0.024785223253498315, 0.3273376571679506, 0.67177221993330294, 0.00089012289874644697, 0.48962085422104135, 0.50979569087113141, 0.00058345490782740013, 0.46406754194472771, 0.53571004668683031, 0.00022241136844202664, 0.47346135887494539, 0.5263113326065374, 0.00022730851851715877, 0.56504995961065041, 0.43485471816581145, 9.5322223538082067e-05, 0.92115472651613373, 0.078767563857399928, 7.7709626466389205e-05, 0.88629770933571506, 0.11368043186533899, 2.185879894596154e-05, 0.83862783079609726, 0.16134912621625858, 2.3042987644162106e-05, 0.96631295876816758, 0.033681673271623441, 5.3679602088754854e-06, 0.838644851080249, 0.16135240086071348, 2.7480590375089156e-06, 0.98440741136075338, 0.015591207496872617, 1.3811423740147136e-06, 0.98108244712858661, 0.018916289515771071, 1.2633556422733213e-06, 1.4846190684672449e-10, 0.01214339852203244, 0.98785660132950559, 6.4556439373447552e-10, 0.02042954543601691, 0.97957045391841868, 2.7259985755764897e-09, 0.033928854284672787, 0.96607114298932861, 1.1142560576130246e-08, 0.055447698327182209, 0.94455229053025735, 1.0107812694009762e-07, 0.35119867166374696, 0.64880122725812617, 1.654000159869412e-07, 0.13820873971878719, 0.86179109488119687, 2.3223672356741317e-06, 0.35119789154988373, 0.64879978608288058, 2.4408824174268045e-06, 0.36573819315220912, 0.63425936596537358, 7.2097582121844249e-06, 0.063374404788280117, 0.93661838545350773, 3.0386781128102376e-05, 0.071776381334351963, 0.92819323188451985, 6.5650760385645707e-05, 0.08959463451860368, 0.91033971472101072, 0.00044744139811345109, 0.47407331930863594, 0.52547923929325069, 0.00067487507718573005, 0.38193683059140787, 0.61738829433140652, 0.045779702813143329, 0.56370292717454962, 0.39051737001230707, 0.026856114715831315, 0.74405154428792653, 0.22909234099624223, 0.035269922704626547, 0.81429749900443538, 0.15043257829093798, 0.048924812447079517, 0.76558794795279728, 0.18548723960012309, 0.079046798759930509, 0.87600002175553215, 0.04495317948453733, 0.096444017823476252, 0.8349974619163345, 0.068558520260189354, 0.19376178818706802, 0.76688445204086342, 0.039353759772068501, 0.18454410738301449, 0.81036436229132403, 0.005091530325661486, 0.28381399090869897, 0.68256051372628801, 0.033625495365013074, 0.32660290681419762, 0.64137363863754115, 0.032023454548261152, 0.36082178603061182, 0.61944782985149038, 0.01973038411789782, 0.55761760296151508, 0.44175649223864227, 0.00062590479984271999, 0.55656155484308267, 0.44309188757699419, 0.00034655757992309489, 0.47465596158444351, 0.5251025551443339, 0.00024148327122261258, 0.81529190442053157, 0.18454043976402412, 0.00016765581544424501, 0.89404820563457432, 0.10585342570845434, 9.8368656971371839e-05, 0.94785806600754141, 0.052104185674751766, 3.7748317706797921e-05, 0.83863502030838277, 0.16135050945383145, 1.4470237785757608e-05, 0.94231374952028113, 0.057674745437563832, 1.1505042155123695e-05, 0.9230730445097739, 0.076915559070109427, 1.139642011672311e-05, 0.98243351081584129, 0.017564541661950692, 1.9475222079740559e-06, 0.98569633242627486, 0.014302471968853316, 1.1956048718005995e-06, 1.36240635668259e-10, 0.0097385449777252827, 0.99026145488603401, 5.9340775954517885e-10, 0.01641098147654356, 0.9835890179300486, 2.5125697989399905e-09, 0.02732901032883624, 0.9726709871585939, 3.9446330598836948e-08, 0.17154075963781867, 0.82845920091585068, 1.6504487039990168e-07, 0.35119864919870936, 0.64880118575642032, 2.1344063721831815e-07, 0.1558616494389477, 0.84413813712041508, 2.2998920896228269e-06, 0.21300195540160005, 0.78699574470631029, 4.5359774978689756e-06, 0.097684860082922875, 0.90231060393957918, 1.499302138667569e-05, 0.40355941577024274, 0.59642559120837046, 3.0550408219921344e-05, 0.26516747696249077, 0.73480197262928926, 7.9715726522888093e-05, 0.19987691221010465, 0.8000433720633725, 0.00023722907701973362, 0.43101305814738139, 0.56874971277559883, 0.00066614456557445014, 0.51948652140013785, 0.4798473340342877, 0.046027174247046672, 0.49590637009413346, 0.45806645565881976, 0.057860713654857072, 0.66793220408137521, 0.27420708226376761, 0.028272367394338957, 0.75065193623726156, 0.22107569636839949, 0.036174255405063901, 0.72381951305071224, 0.24000623154422374, 0.074301679440815213, 0.7596978145870138, 0.16600050597217098, 0.10088294103963727, 0.84696143117085221, 0.052155627789510592, 0.15153295257912125, 0.79177271768957602, 0.056694329731302603, 0.16258775171205039, 0.78487693995163177, 0.052535308336317817, 0.30110694619777884, 0.69518335856616831, 0.0037096952360529539, 0.39164241310540737, 0.59625305434697995, 0.012104532547612675, 0.41870766798824777, 0.58001704689659284, 0.0012752851151593718, 0.48371653941491172, 0.51543918103731157, 0.00084427954777679742, 0.52190589673625576, 0.47763978531906004, 0.00045431794468420123, 0.49624968038443801, 0.50342281692885249, 0.00032750268670954889, 0.59544595576665271, 0.40433564200905803, 0.00021840222428923535, 0.89028496661588385, 0.1096241807748886, 9.0852609227485534e-05, 0.88760593168518243, 0.11234214495144711, 5.192336337035488e-05, 0.76460113373795835, 0.23537062864316166, 2.8237618879884617e-05, 0.9285295070485976, 0.071458360491606879, 1.2132459795584331e-05, 0.96713858224879545, 0.03285533272768458, 6.0850235199357034e-06, 0.9073905786752221, 0.092596587895467833, 1.283342930992485e-05, 0.96023262996968806, 0.039763215133852226, 4.1548964598639039e-06, 1.249460449550858e-10, 0.0078166157623807755, 0.99218338411267315, 5.4493784644288464e-10, 0.013189767582097526, 0.98681023187296457, 4.1046417517442006e-09, 0.039074179331734717, 0.96092581656362352, 5.7494043326152375e-08, 0.21882271798998215, 0.78117722451597449, 2.5511722740456355e-07, 0.35119861756541404, 0.64880112731735862, 4.599285302560988e-07, 0.29394179850740626, 0.70605774156406342, 2.2129124459681669e-06, 0.26517499137431694, 0.73482279571323705, 3.8534353451592905e-06, 0.10737338509950629, 0.89262276146514852, 1.7683866271391761e-05, 0.43110770745363519, 0.56887460868009343, 3.5597241834713196e-05, 0.19988573117960604, 0.80007867157855916, 6.5297850503057936e-05, 0.28245446610122588, 0.71748023604827116, 0.00025963522600652424, 0.43596365935187936, 0.56377670542211411, 0.00055629085636108022, 0.45216340899019891, 0.54728030015344009, 0.0011350170661250966, 0.5137607624461642, 0.48510422048771068, 0.012020945557803323, 0.62907855606863516, 0.35890049837356147, 0.0069552027468725254, 0.68284458437285678, 0.31020021288027061, 0.055921114734906352, 0.76235421097882172, 0.18172467428627198, 0.070118303391193959, 0.82022372185086045, 0.10965797475794549, 0.10214531120142367, 0.7953445321949375, 0.1025101566036388, 0.15660989240593035, 0.78964544141622484, 0.053744666177844874, 0.21502193493428201, 0.75718693435163997, 0.027791130714078106, 0.31085898742543339, 0.65152769006198941, 0.037613322512577166, 0.36271872557927254, 0.62807257947832196, 0.0092086949424054591, 0.46811728543474374, 0.53037785806420867, 0.0015048565010475092, 0.50987561748906873, 0.46555137209677477, 0.024573010414156545, 0.63361890611508076, 0.36571833095040768, 0.00066276293451154661, 0.66071512117548392, 0.33898487843992936, 0.00030000038458678053, 0.88366574495923411, 0.11610730419318148, 0.00022695084758433308, 0.86392095832233629, 0.13599444881463338, 8.4592863030316664e-05, 0.88628043827939951, 0.11367821660389803, 4.1345116702401145e-05, 0.93970992205548809, 0.060265658278344798, 2.4419666167040562e-05, 0.96209674471090179, 0.037891461227038382, 1.1794062059785199e-05, 0.94788907403898592, 0.052105890200234789, 5.0357607793574558e-06, 0.98065622512876816, 0.019340428830497556, 3.3460407343359303e-06, 0.94694421969391585, 0.053048860846764551, 6.9194593196676287e-06, 1.1452663474520966e-10, 0.0062799794920764271, 0.99372002039339691, 2.853257157209107e-09, 0.060532214515358576, 0.93946778263138431, 1.6214598025741835e-08, 0.13529329344145699, 0.86470669034394498, 2.1189337446152076e-08, 0.21300244077085834, 0.78699753803980421, 7.3955721368779058e-08, 0.10027259913410227, 0.89972732691017632, 2.7127367296178246e-07, 0.051350744882100251, 0.94864898384422691, 1.1373150305372755e-06, 0.13970426155079299, 0.86029460113417644, 5.6386873784185915e-06, 0.10737319341021356, 0.89262116790240809, 9.1443181671856631e-06, 0.1958725816555755, 0.80411827402625724, 3.0780835544700696e-05, 0.23623548224942459, 0.76373373691503066, 0.018866399425582821, 0.20327052027286135, 0.77786308030155582, 0.00016186564366182682, 0.39934577771479773, 0.60049235664154044, 0.00055400522477567474, 0.50935418305662183, 0.49009181171860233, 0.0011543244279179205, 0.60305481615717316, 0.39579085941490899, 0.0093830174487906804, 0.65711480876058237, 0.33350217379062697, 0.02712460037708728, 0.68364712401760941, 0.28922827560530329, 0.071627369982289954, 0.76713459519396177, 0.16123803482374829, 0.039927699342942116, 0.83843027544955162, 0.12164202520750628, 0.14656321780515202, 0.74588950576415913, 0.10754727643068876, 0.16376035719753274, 0.78848118510568288, 0.047758457696784468, 0.19493473739530479, 0.77867060244504371, 0.026394660159651598, 0.36120498883352231, 0.61929368977117705, 0.019501321395300596, 0.33948133935494107, 0.63170375299979131, 0.028814907645267729, 0.51829821941476095, 0.47954661106164709, 0.0021551695235920544, 0.58059215907068418, 0.40958113371002164, 0.0098267072192940765, 0.71672312276462669, 0.28251674384286046, 0.00076013339251280619, 0.77942164030452332, 0.22019157835612072, 0.00038678133935605036, 0.86461414507544643, 0.13515840341285848, 0.00022745151169498992, 0.87144894223037694, 0.12842333294968455, 0.0001277248199384536, 0.92979811341202045, 0.070152932060478179, 4.895452750144501e-05, 0.95126278805944253, 0.048711574494744239, 2.563744581323103e-05, 0.97227436758017605, 0.02771292781793892, 1.2704601884907007e-05, 0.98237127145535186, 0.01762364926357245, 5.0792810756628159e-06, 0.9883308747746975, 0.011666609041297193, 2.51618400519803e-06, 0.98235119700233953, 0.017645933714761562, 2.8692828988985315e-06, 6.150922647499844e-10, 0.02960697961527442, 0.97039301976963332, 3.901427491963202e-09, 0.072655969185578692, 0.92734402691299378, 2.1823351141247776e-08, 0.15984300523259043, 0.84015697294405844, 1.6425441738108356e-08, 0.11919570971067156, 0.88080427386388671, 9.7614611940378502e-08, 0.26517555229964312, 0.73482435008574487, 5.701319637312147e-07, 0.28035220426049173, 0.71964722560754446, 9.3319247507560906e-07, 0.082751612748402772, 0.91724745405912222, 3.5530676313383773e-06, 0.097684956098771203, 0.90231149083359752, 1.0912076402876782e-05, 0.16873535134981291, 0.8312537365737841, 2.3104211625557428e-05, 0.19200984631769741, 0.8079670494706771, 8.8396020164666851e-05, 0.25937649579303113, 0.74053510818680424, 0.00022977833115246573, 0.31406919157580399, 0.68570103009304362, 0.00051050879418069637, 0.45177723595921199, 0.54771225524660727, 0.013015917668960585, 0.50585204409539097, 0.48113203823564832, 0.026157531993968221, 0.63914270022932174, 0.33469976777671007, 0.016468280264379884, 0.71817991354020883, 0.26535180619541132, 0.061697392653401247, 0.76286893962150992, 0.17543366772508873, 0.062288225164186743, 0.84915493858483237, 0.088556836250980861, 0.080077719163564112, 0.86570864472610753, 0.054213636110328381, 0.125712880508489, 0.82960477806789368, 0.04468234142361735, 0.23580485020524711, 0.72863832476703816, 0.035556825027714609, 0.27782924455626395, 0.70394011219599584, 0.01823064324774025, 0.36138756245183318, 0.62576757838464525, 0.012844859163521632, 0.55509185834700769, 0.44218026106753838, 0.0027278805854539867, 0.59550747330712761, 0.39558043292726031, 0.0089120937656120107, 0.68655511497381561, 0.31247299230750236, 0.00097189271868207243, 0.7954393293525992, 0.20405307501303099, 0.00050759563436990134, 0.90561026643893916, 0.094181793366656483, 0.00020794019440424204, 0.93326029567241164, 0.06663937315513993, 0.00010033117244839944, 0.97155646884745128, 0.028393540482592489, 4.9990669956191124e-05, 0.98709918457349344, 0.01287555978671461, 2.5255639792054125e-05, 0.96891974492996114, 0.031069474141213794, 1.0780928825086651e-05, 0.96761573797445677, 0.032376688412043095, 7.5736135001059529e-06, 0.90094551641916587, 0.099050763302711287, 3.7202781226453157e-06, 0.99133691074756192, 0.0086613359312496859, 1.7533211885125555e-06, 9.6097254311358254e-11, 0.0040664325175955333, 0.99593356738630712, 4.2020893703699151e-10, 0.0068795779582577097, 0.99312042162153336, 3.9879837830057039e-09, 0.063374861452971831, 0.93662513455904439, 3.0080683037737539e-08, 0.077439687097355894, 0.92256028282196101, 7.7186008207421418e-08, 0.039974282905150094, 0.96002563990884171, 3.6885786560369713e-07, 0.076875499296983479, 0.92312413184515085, 7.7055439693921474e-07, 0.069475346224996848, 0.9305238832206062, 2.3788787821454687e-06, 0.12468665514378201, 0.87531096597743596, 6.8106732164348888e-06, 0.1427741686108622, 0.85721902071592138, 2.5733347849939136e-05, 0.16308427171890702, 0.83688999493324312, 6.6605014300140638e-05, 0.31161863783095967, 0.68831475715474022, 0.00018680201424775851, 0.38941372835540933, 0.61039946963034297, 0.00061803537808386767, 0.55393249902621355, 0.44544946559570259, 0.0054109434599216352, 0.5330160712634614, 0.46157298527661689, 0.0097375594561176539, 0.68569116673948893, 0.30457127380439342, 0.0039141582307427852, 0.72897239469063568, 0.2671134470786215, 0.028926609312672959, 0.77915329683199297, 0.19192009385533398, 0.053433332039870884, 0.8452765375847382, 0.10129013037539092, 0.064694683146133941, 0.85436453433854931, 0.080940782515316792, 0.13413179047744975, 0.81527466221209133, 0.050593547310458876, 0.17498194500100919, 0.79836342861812759, 0.026654626380863269, 0.30176405042849586, 0.68253987551331341, 0.015696074058190668, 0.44444174379002854, 0.53878282121133103, 0.016775434998640436, 0.56975274670981035, 0.41169688556828721, 0.018550367721902401, 0.62105948045207948, 0.37692692092350022, 0.0020135986244202821, 0.73838910877870134, 0.26044982141749318, 0.0011610698038053676, 0.84383025163554393, 0.15567813415622619, 0.00049161420822986111, 0.89605580056509737, 0.10369808792428638, 0.00024611151061605928, 0.94064348769367923, 0.059228702074037368, 0.00012781023228344892, 0.97198351665198623, 0.02796355948371226, 5.2923864301402124e-05, 0.98155001689620114, 0.018424084485191394, 2.589861860750302e-05, 0.98846266666253302, 0.01152586885723272, 1.1464480234292309e-05, 0.98167521430374161, 0.018316614933378158, 8.1707628801724633e-06, 0.99179140859534576, 0.008205852149880663, 2.7392547735057506e-06, 0.99230972099150416, 0.0076883440461310909, 1.9349623647716529e-06, 9.9365586388011134e-10, 0.0370197924262224, 0.96298020658012173, 3.263280530733794e-09, 0.047037725201323412, 0.95296227153539603, 9.9735532843536177e-09, 0.056541359702757379, 0.94345863032368926, 1.3430512891640197e-08, 0.059870119660389826, 0.94012986690909728, 5.3626335247782195e-08, 0.049400900691735312, 0.95059904568192943, 1.8251676122974967e-07, 0.12256942989678073, 0.87743038758645808, 5.2922450677873055e-07, 0.076875486968713325, 0.92312398380677985, 1.8404048442577517e-06, 0.12432874015114775, 0.875669419444008, 6.2614999735686165e-06, 0.14538888263629424, 0.85460485586373214, 2.1023550747395797e-05, 0.18484238552335236, 0.81513659092590041, 0.0063906682531892755, 0.22131768840776816, 0.77229164333904254, 0.00017232974892336268, 0.31131130515430244, 0.68851636509677416, 0.0084904521815259079, 0.49659432357304756, 0.49491522424542644, 0.013467487739868876, 0.507855321126509, 0.47867719113362212, 0.011177896815878621, 0.67098380378005851, 0.31783829940406289, 0.018719412343690768, 0.71070604571793838, 0.27057454193837094, 0.029818801988092305, 0.81987452935681904, 0.15030666865508854, 0.043634440046455995, 0.85188345323689274, 0.10448210671665126, 0.071265570563405545, 0.86336657885860391, 0.065367850577990577, 0.090578007986616166, 0.8572150282070562, 0.052206963806327632, 0.17442474222818516, 0.76673152015876533, 0.058843737613049507, 0.33994821113117157, 0.64376032368387026, 0.016291465184958123, 0.41266805186909161, 0.56313808378591601, 0.024193864344992419, 0.56348149705322992, 0.43025977856840303, 0.00625872437836712, 0.68925181451467832, 0.3082279318432869, 0.0025202536420348394, 0.80676473084094369, 0.19209395330517381, 0.0011413158538825963, 0.88637676130418119, 0.1130178461429087, 0.00060539255291009798, 0.927608488602367, 0.072146921450505927, 0.00024458994712709065, 0.93409735164382557, 0.065778820831101786, 0.00012382752507264516, 0.95955613130039441, 0.040384600727647969, 5.9267971957485057e-05, 0.97011376253539017, 0.029863451160091054, 2.2786304518811963e-05, 0.97785636843210832, 0.022133673016754722, 9.9585511369828196e-06, 0.98883089378959566, 0.011162923574077121, 6.1826363272136429e-06, 0.99132115144217314, 0.0086752529754306317, 3.5955823961140894e-06, 0.99391937637817918, 0.0060787241602671032, 1.8994615537603742e-06, 2.1883111168533595e-10, 0.097685303159883413, 0.90231469662128561, 1.9619342309380787e-09, 0.024935516727982106, 0.97506448131008361, 3.5286318780874051e-09, 0.076875527381861097, 0.92312446908950707, 1.1174111479027537e-08, 0.021193277834474996, 0.97880671099141348, 3.9014624280688761e-08, 0.027700502337816992, 0.97229945864755873, 1.9855753294600787e-07, 0.056732691047394423, 0.94326711039507272, 5.5649301216555306e-07, 0.094581880780753844, 0.90541756272623397, 2.1048608818736715e-06, 0.10587348637527356, 0.89412440876384458, 6.3394180477664409e-06, 0.1480302505364014, 0.85196341004555076, 1.7495901445102562e-05, 0.17312172990195959, 0.82686077419659532, 0.0049196783937341055, 0.2536698512655457, 0.74141047034072016, 0.0045293250465165205, 0.34508495218051799, 0.65038572277296547, 0.00048661010877909847, 0.45371542150162869, 0.54579796838959216, 0.0071844113231145897, 0.46167355915152009, 0.53114202952536527, 0.005889581720519464, 0.60056175055146765, 0.39354866772801289, 0.010782119472985954, 0.70945947440517587, 0.27975840612183822, 0.01642973426724444, 0.82006011621068664, 0.16351014952206883, 0.041788042636438386, 0.85815102554979483, 0.10006093181376677, 0.06441789360108971, 0.85876918013974235, 0.076812926259168024, 0.1083871738371005, 0.82396050886044858, 0.067652317302450873, 0.24327610456501764, 0.71505255245120514, 0.041671342983777108, 0.33455571864246691, 0.62408368863533703, 0.041360592722195916, 0.4376036981926188, 0.55108443115460148, 0.0113118706527797, 0.61343631730047987, 0.36718281992332857, 0.019380862776191631, 0.74969640877153532, 0.24368332139839324, 0.0066202698300714558, 0.85119990263626566, 0.14753869354684521, 0.0012614038168891181, 0.91305101156710244, 0.086394045069231262, 0.00055494336366611167, 0.94159826524719181, 0.058182865450185708, 0.00021886930262248174, 0.96696107098195949, 0.032927434102496211, 0.00011149491554430661, 0.95834583136945961, 0.041604247394788012, 4.9921235752383312e-05, 0.96462998331574712, 0.035350763692445421, 1.9252991807457744e-05, 0.98934203780505781, 0.010648728623461537, 9.2335714806298587e-06, 0.98241227853886326, 0.017582582526883196, 5.1389342535582088e-06, 0.9931869095510869, 0.0068095909833367435, 3.4994655764008678e-06, 0.99244970892018214, 0.0075473668794043521, 2.9242004134331896e-06, 3.339859439043867e-10, 0.0096885070803255629, 0.9903114925856884, 6.6121992840305402e-10, 0.039974285964173864, 0.96002571337460618, 5.7939805196932679e-09, 0.056732701983391663, 0.94326729222262784, 1.293760096272363e-08, 0.022056853662269983, 0.97794313340012906, 3.0749706047563064e-08, 0.0392496563128246, 0.96075031293746938, 1.2920621726186205e-07, 0.04977673026423924, 0.95022314052954349, 4.0424534540435191e-07, 0.056144245701243024, 0.94385535005341159, 1.3477013411494762e-06, 0.091401519396331718, 0.90859713290232713, 4.0981074768474016e-06, 0.089326336031237741, 0.91066956586128545, 1.8237107152639052e-05, 0.1740783281776366, 0.82590343471521077, 0.0038803579363370817, 0.18514876347033832, 0.81097087859332462, 0.00013533082420921915, 0.31868429584681496, 0.68118037332897585, 0.0065781577655604339, 0.39487189693243979, 0.5985499453019999, 0.012532913921255872, 0.50637085192594344, 0.48109623415280062, 0.01536184158953059, 0.53909519798637417, 0.4455429604240953, 0.0051958393538176079, 0.66977335234010082, 0.32503080830608172, 0.015235236726309416, 0.78053866575827613, 0.2042260975154144, 0.038499342715402084, 0.82466179329259126, 0.1368388639920067, 0.08425963752955834, 0.80963694495948102, 0.10610341751096065, 0.12191915369695405, 0.79141298491078516, 0.086667861392260737, 0.22601809958995775, 0.73642314957685306, 0.037558750833189151, 0.32756897296451915, 0.64823811415012966, 0.02419291288535114, 0.44785970630845934, 0.5258832162877094, 0.026257077403831305, 0.61337403998392526, 0.38035221696858235, 0.0062737430474923347, 0.79559588376442836, 0.20095333978995925, 0.0034507764456123725, 0.84284029889699708, 0.15540294105933913, 0.0017567600436638351, 0.93424840284558153, 0.065115603521040649, 0.00063599363337777368, 0.94134185197668685, 0.058422887925821496, 0.00023526009749169207, 0.9666607629679429, 0.033233937014115193, 0.00010530001794187947, 0.98350184818462183, 0.016454121011921057, 4.403080345709061e-05, 0.98772145143229284, 0.012260272830276267, 1.8275737430953548e-05, 0.99106996043374562, 0.0089206302010749125, 9.4093651794501396e-06, 0.99271879949982789, 0.0072760267255096494, 5.1737746624565255e-06, 0.99500086432646317, 0.0049959565442079202, 3.1791293289832205e-06, 0.99413373450184239, 0.0058634524709917264, 2.8130271657988598e-06, 1.4890074595651799e-10, 0.056732702303652287, 0.94326729754744687, 5.5164699221405322e-10, 0.0054754415857801572, 0.99452455786257288, 1.6855214298597994e-09, 0.015671207920404839, 0.98432879039407373, 6.3441770089935905e-09, 0.051350758486430906, 0.94864923516939204, 2.4237545120856208e-08, 0.036720221326562538, 0.96327975443589242, 9.9809191992937716e-08, 0.066937067907946388, 0.93306283228286169, 3.5070831958991804e-07, 0.060125873813705412, 0.93987377547797502, 1.4107925778350402e-06, 0.06489431342917816, 0.93510427577824407, 0.0042461469762375631, 0.11437218166870533, 0.88138167135505718, 1.469222381146675e-05, 0.17250839273092008, 0.82747691504526844, 4.4989382244150631e-05, 0.17401496905303238, 0.82594004156472345, 0.00012918933912872213, 0.27215846728718202, 0.7277123433736894, 0.0031919472999223496, 0.36601536672116297, 0.63079268597891469, 0.0088518902292733757, 0.39965455862973115, 0.59149355114099544, 0.0086857091673266263, 0.53029596667999723, 0.46101832415267618, 0.0081001904119084676, 0.62337957179697701, 0.36852023779111459, 0.01796662965674432, 0.72294789834748074, 0.25908547199577486, 0.03036864014526687, 0.77337723160873328, 0.19625412824599966, 0.045280776900217222, 0.80584766031253818, 0.14887156278724464, 0.1079457271478957, 0.8020894941362412, 0.089964778715863017, 0.23833738414678105, 0.71604810718646128, 0.045614508666757772, 0.32946417908479775, 0.64924454644743579, 0.021291274467766488, 0.53905579612338017, 0.44198968296084262, 0.018954520915777207, 0.59742330889998618, 0.38780499192689893, 0.014771699173114914, 0.79456694214993939, 0.19966950131706829, 0.0057635565329923139, 0.88375940901024241, 0.11098341778069606, 0.0052571732090615081, 0.903451493353706, 0.0959012287837505, 0.00064727786254343048, 0.96367159898140298, 0.036067038447164058, 0.00026136257143289087, 0.98275802786434341, 0.017140331617144153, 0.00010164051851241006, 0.98577611361797401, 0.014180183366550192, 4.3703015475690965e-05, 0.98791129714047454, 0.012067984414869278, 2.0718444656275322e-05, 0.99412999128844415, 0.0058617103010831116, 8.2984104727447807e-06, 0.99377704428800751, 0.0062178635519437699, 5.0921600487546242e-06, 0.99507421822732978, 0.0049219087753953842, 3.8729972747183382e-06, 0.99389431209247481, 0.006102067798638167, 3.6201088870785132e-06, 1.3436663246182434e-10, 0.051350758805309378, 0.94864924106032411, 3.0245333555268103e-10, 0.034830021882150085, 0.9651699778153966, 1.6293431669884804e-09, 0.045584883390177723, 0.95441511498047915, 5.7935011524760405e-09, 0.0094072243189571164, 0.99059276988754164, 2.2920191518573447e-08, 0.034830021094373775, 0.96516995598543476, 7.1552742834805665e-08, 0.021878552531952946, 0.97812137591530424, 2.4066169516794339e-07, 0.041384826584195365, 0.95861493275410947, 9.1208389540814795e-07, 0.098191497692471347, 0.90180759022363333, 3.7366780764952134e-06, 0.097684938162729204, 0.90231132515919432, 1.3322018292023556e-05, 0.11010237579519749, 0.88988430218651049, 4.4816354764194115e-05, 0.18457279033563193, 0.81538239330960383, 0.00012953164247918807, 0.22809125560451687, 0.77177921275300398, 0.00043620745611727978, 0.3562993175278219, 0.64326447501606077, 0.0030147186049377028, 0.37121379078132843, 0.62577149061373394, 0.0031459523393467916, 0.54958558651158618, 0.4472684611490671, 0.0062650069699376719, 0.50384295133666768, 0.48989204169339479, 0.016546717599393645, 0.71056431338426873, 0.27288896901633775, 0.053285192434476346, 0.63106070864449748, 0.3156540989210263, 0.065835201188771772, 0.79376529836335186, 0.14039950044787641, 0.13616974495645434, 0.81543121262958773, 0.048399042413957975, 0.2175380165935713, 0.70686029889198354, 0.075601684514445128, 0.38976360615743039, 0.56761044406685002, 0.042625949775719561, 0.48429319255322578, 0.49849349271620019, 0.017213314730574213, 0.65577844118514184, 0.33645207752045642, 0.0077694812944017625, 0.81328991779179638, 0.18213927858367787, 0.0045708036245257289, 0.90155922851848225, 0.096272735785017216, 0.0021680356965005066, 0.91640021854328324, 0.082813337815603849, 0.00078644364111294686, 0.9700403361305322, 0.029691524984771501, 0.0002681388846962445, 0.98137240893801769, 0.018521136275595661, 0.00010645478638659134, 0.97974481001879721, 0.020214428991367224, 4.07609898355343e-05, 0.98917056485208699, 0.0108132405303822, 1.6194617530872471e-05, 0.98619159540055856, 0.013799264712834254, 9.1398866072316556e-06, 0.99671927679643746, 0.0032764685165851859, 4.2546869772530814e-06, 0.99595685930891742, 0.004039215597667763, 3.9250934147206801e-06, 0.96762031774846635, 0.032376841652539595, 2.840598993960128e-06, 7.2097396335411564e-11, 0.029194492376581511, 0.97080550755132111, 4.0179039697768676e-10, 0.049025365025077261, 0.95097463457313236, 9.5066065405223261e-10, 0.028181215348281424, 0.97181878370105801, 3.7831465448186402e-09, 0.02603511334043445, 0.97396488287641891, 1.2897453100992321e-08, 0.033226557647600172, 0.96677342945494671, 5.5540205241171822e-08, 0.035987832474261745, 0.96401211198553305, 2.4998164072527338e-07, 0.042044199734704649, 0.95795555028365453, 8.1670004618803465e-07, 0.055895756937254425, 0.94410342636269939, 3.5557183280460435e-06, 0.095593906464581158, 0.90440253781709079, 1.185475439547221e-05, 0.098620850863316845, 0.9013672943822878, 0.0032133768311381028, 0.16074310494565341, 0.83604351822320844, 0.0032911711794620145, 0.21529142647254981, 0.78141740234798807, 0.0067920595635109242, 0.29794333851398391, 0.69526460192250528, 0.0034341497501990908, 0.39114545017058466, 0.60542040007921616, 0.0034709908480684542, 0.44876614745630133, 0.54776286169563015, 0.0038885669818436775, 0.59253241363734921, 0.40357901938080715, 0.026798279846251247, 0.6874529842694449, 0.28574873588430377, 0.046865210150335936, 0.74658326805472752, 0.20655152179493647, 0.050973212054560915, 0.73820502975669444, 0.21082175818874463, 0.11582050725305687, 0.7975136432918819, 0.086665849455061283, 0.23845744267710173, 0.73405434168222672, 0.027488215640671592, 0.38642095964740025, 0.58414770015039585, 0.02943134020220398, 0.59032075382646843, 0.39956750147623415, 0.010111744697297306, 0.7188743196947609, 0.27129834517111084, 0.009827335134128222, 0.8880468278643705, 0.10514287521247102, 0.006810296923158439, 0.89523876139976111, 0.10220887125492693, 0.0025523673453119598, 0.93299311307193045, 0.066093774773800032, 0.00091311215426958592, 0.96948075560435842, 0.030215852435740143, 0.00030339195990135022, 0.98743151006175234, 0.012457602960085305, 0.00011088697816232922, 0.98863307660542143, 0.011327620194609483, 3.9303199969077409e-05, 0.99192771052491746, 0.0080567176245565537, 1.5571850525886394e-05, 0.9915449244966672, 0.0084473735206991758, 7.701982633683089e-06, 0.98896457303458574, 0.01103034209933974, 5.0848660745897837e-06, 0.99739916086639624, 0.0025977259776725765, 3.113155931097272e-06, 0.9959521110731242, 0.0040442348735576072, 3.6540533181947174e-06, 4.4199695987302964e-11, 0.00079135070310652029, 0.9992086492526937, 2.2304041455284082e-10, 0.015230278483834668, 0.9847697212931249, 6.8854433767571221e-10, 0.015230278476744913, 0.9847697208347107, 2.8192807958977872e-09, 0.027144862577934682, 0.9728551346027845, 1.0778809988163945e-08, 0.031080299962911805, 0.96891968925827832, 4.8193427306082821e-08, 0.031456581535049252, 0.96854337027152348, 1.807015419342082e-07, 0.031182021533312645, 0.96881779776514543, 7.5681741952125855e-07, 0.071778508130552518, 0.92822073505202796, 2.5644348903010699e-06, 0.084181389562409448, 0.91581604600270017, 1.0818550821281452e-05, 0.10868723168293189, 0.89130194976624688, 0.0035761069920280547, 0.13210190469280431, 0.8643219883151676, 0.00012820012897510902, 0.20853946141899798, 0.791332338452027, 0.00039227128709937755, 0.27635328768831097, 0.72325444102458969, 0.0040385455059335235, 0.33566501172958918, 0.66029644276447741, 0.0036193142363509698, 0.45968037923984117, 0.53670030652380785, 0.019002973720688467, 0.5081988933496111, 0.4727981329297003, 0.016204891781588775, 0.71500761241990485, 0.26878749579850642, 0.042688688205912047, 0.71454471112403395, 0.2427666006700539, 0.1382598686175068, 0.77437668498850887, 0.087363446393984384, 0.12441612787888208, 0.73407528189227178, 0.14150859022884615, 0.31785277970529957, 0.61153787636852763, 0.070609343926172824, 0.45274998924439597, 0.49360944632781095, 0.053640564427793115, 0.55663135865760371, 0.40947694225532671, 0.033891699087069516, 0.79868554174638928, 0.18237089641179172, 0.018943561841819025, 0.84486569202216188, 0.14752370666445122, 0.0076106013133868094, 0.91693074199889102, 0.080284369619351315, 0.0027848883817575515, 0.93265969205335908, 0.066400902707302881, 0.00093940523933805028, 0.95821883063149993, 0.041428769783705847, 0.00035239958479424047, 0.9774688774728677, 0.022424697623625742, 0.00010642490350651342, 0.98300434716428664, 0.016952531015567419, 4.3121820145886123e-05, 0.98810034637639721, 0.01188169543503511, 1.7958188567716007e-05, 0.98737955654446385, 0.012612013242308748, 8.430213227496385e-06, 0.99709656907768007, 0.0028977155863713871, 5.7153359486050302e-06, 0.98712043664391691, 0.012875836995233881, 3.7263608491763499e-06, 0.9970893397129047, 0.0029074249700652114, 3.2353170301639181e-06, 4.3888955063189543e-11, 0.00069907988458812315, 0.99930092007152294, 1.1754043539367822e-10, 0.000724357199774671, 0.99927564268268498, 6.1289453853422841e-10, 0.0080144137737966602, 0.99198558561330874, 2.4333146707723345e-09, 0.02770050335113769, 0.97229949421554762, 8.8905864030767153e-09, 0.034098665837255612, 0.965901325272158, 4.0007630845511952e-08, 0.024013869669660209, 0.975986090322709, 1.7184897608261227e-07, 0.063748025836775649, 0.93625180231424832, 6.9712268733252152e-07, 0.039086123597828377, 0.96091317927948428, 2.5831802294727531e-06, 0.05848385440586986, 0.94151356241390061, 1.0526998699058674e-05, 0.10979251231594027, 0.89019696068536069, 3.4459274098236631e-05, 0.15284915124105034, 0.84711638948485146, 0.0044856204022698971, 0.21748054175923309, 0.77803383783849689, 0.00038571747310749794, 0.25769559343018633, 0.74191868909670622, 0.011963826053637832, 0.40972025970841741, 0.57831591423794482, 0.011437298748728635, 0.43569843754256626, 0.55286426370870512, 0.0089947583370318662, 0.6184467122975541, 0.37255852936541406, 0.035309177334161806, 0.60325080739663639, 0.36144001526920166, 0.040297966404177196, 0.63886293029668306, 0.32083910329913978, 0.10125893136242717, 0.71551602800859582, 0.18322504062897702, 0.223448691256009, 0.58317905835789197, 0.19337225038609901, 0.34548155099428157, 0.58009718165983104, 0.07442126734588736, 0.43013936485315829, 0.53680438414769005, 0.033056250999151639, 0.61905110162159371, 0.33782031038761423, 0.043128587990792062, 0.75968307867829277, 0.21924063889519718, 0.021076282426509937, 0.85766715474075783, 0.13445440720263788, 0.0078784380566042384, 0.90288678811449841, 0.093749511328208177, 0.0033637005572933125, 0.96811646495403314, 0.030678495898637168, 0.0012050391473296292, 0.95089363517350589, 0.048786315463027113, 0.0003200493634669237, 0.97573817535568441, 0.024145168815375446, 0.00011665582894015838, 0.99367518240783481, 0.0062853602086005173, 3.9457383564631756e-05, 0.99114421679596987, 0.0088351856626138828, 2.0597541416095451e-05, 0.98326681111255509, 0.016722843872560747, 1.03450148842026e-05, 0.99220181813099639, 0.0077916831060220303, 6.4987629815080154e-06, 0.98241270058943386, 0.017582590080472613, 4.7093300936084676e-06, 0.99712459543069476, 0.0028714745167780892, 3.9300525271690069e-06, 2.7378520631881889e-11, 0.018323631138197263, 0.98167636883442433, 1.2052212251421604e-10, 0.012152853843749001, 0.98784714603572887, 4.7293100527401347e-10, 0.015447597425960255, 0.98455240210110873, 2.3770398395229041e-09, 0.013518639561767774, 0.9864813580611923, 7.8637346462345538e-09, 0.033483469953700086, 0.96651652218256523, 3.5647561754668079e-08, 0.026723682033058294, 0.9732762823193799, 1.4844428637083042e-07, 0.034387486461628987, 0.96561236509408466, 6.0889521621561119e-07, 0.042638615750026365, 0.95736077535475739, 2.1224683916353647e-06, 0.097169346848809554, 0.90282853068279878, 9.4610359789014307e-06, 0.051350272980832536, 0.94864026598318862, 0.0049279203459382456, 0.14032102283869916, 0.85475105681536268, 0.00012291526472504904, 0.15959566862730168, 0.84028141610797324, 0.00043392494435007972, 0.23511412741233956, 0.76445194764331037, 0.011874908686974274, 0.33813438856531086, 0.64999070274771487, 0.0072754448510199445, 0.40313396290282921, 0.58959059224615096, 0.021887809915287919, 0.58394471380190371, 0.39416747628280835, 0.032295125140880981, 0.49707772923103155, 0.47062714562808733, 0.074250520848829632, 0.66937988124340253, 0.25636959790776775, 0.1099557710066984, 0.68905229273932522, 0.20099193625397641, 0.19159918058635889, 0.71760025897447011, 0.090800560439171021, 0.42917814742742499, 0.55048271740748989, 0.020339135165085273, 0.51832997904470879, 0.4593390027965169, 0.02233101815877454, 0.57265786634794857, 0.40591679127907632, 0.021425342372975154, 0.82240898436026277, 0.15277251440782993, 0.024818501231907313, 0.86864798604493454, 0.12154538284049969, 0.0098066311145658461, 0.93836792759720689, 0.057772409501247034, 0.0038596629015461925, 0.96660059357272565, 0.032110039952553335, 0.0012893664747210358, 0.96312795810933927, 0.036452955712746496, 0.00041908617791427548, 0.97942566613234527, 0.020450651737463313, 0.00012368213019137324, 0.9917480209001196, 0.0082068355725797709, 4.5143527300700856e-05, 0.99655519962274208, 0.0034238180679699425, 2.0982309288017537e-05, 0.99722361082503641, 0.0027652958623038217, 1.1093312659843271e-05, 0.99787731128663626, 0.0021163825452772747, 6.3061680865358122e-06, 0.99775001773541105, 0.0022449764528887466, 5.0058117001726669e-06, 0.9934580702019119, 0.0065309506133623433, 1.0979184725732311e-05, 1.7511407197797245e-11, 0.00022175643672111715, 0.9997782435457675, 6.9504524600977934e-11, 0.009246530576511024, 0.99075346935398434, 4.7326191949812714e-10, 0.020394776296029635, 0.97960522323070853, 1.6481905805489844e-09, 0.006183412077557863, 0.99381658627425162, 7.4661109877518518e-09, 0.031456582816191458, 0.96854340971769759, 3.3062905832505243e-08, 0.042044208854881547, 0.95795575808221256, 1.6292748863877625e-07, 0.024897488666784786, 0.97510234840572663, 5.5029117087644341e-07, 0.039107851461809104, 0.96089159824701997, 2.7196647548860221e-06, 0.062809030530917118, 0.93718824980432802, 1.1264414578094582e-05, 0.086039056972500028, 0.91394967861292198, 3.2859306410116049e-05, 0.10422421809251206, 0.8957429226010778, 0.0075239783960994455, 0.17950087585610025, 0.81297514574780028, 0.00041462532727106041, 0.25490163266672039, 0.7446837420060084, 0.0097942997080261596, 0.29396480311563605, 0.69624089717633775, 0.020116220796997084, 0.37928862346267783, 0.60059515574032507, 0.029684742810971144, 0.54827932642773602, 0.42203593076129275, 0.045373111520344275, 0.67509149981043781, 0.27953538866921779, 0.056440911995126582, 0.62258486931532042, 0.32097421868955284, 0.067054063161592389, 0.77405834410019403, 0.15888759273821346, 0.16059537517490682, 0.74155202126060504, 0.097852603564488147, 0.27688185792734227, 0.59190136025604712, 0.13121678181661051, 0.4881873237408641, 0.45397359461573883, 0.057839081643396968, 0.7289080071501608, 0.2445199924432194, 0.026572000406619858, 0.81789665319636884, 0.1573605185546515, 0.024742828248979696, 0.78582066612439938, 0.20158561113891454, 0.012593722736686163, 0.96249124557469046, 0.032678827686928716, 0.004829926738380951, 0.95445948645458389, 0.04407233773830041, 0.0014681758071157095, 0.97946770234799052, 0.02010093181615474, 0.00043136583585478948, 0.98130479288638905, 0.018532484487115006, 0.00016272262649596838, 0.98162352424793353, 0.018313794767152655, 6.2680984913820494e-05, 0.98575174919864261, 0.014224144867249884, 2.4105934107445664e-05, 0.99652195739581984, 0.0034610116781912952, 1.70309259889367e-05, 0.97276885264424784, 0.027222894546339853, 8.2528094122116463e-06, 0.99695740758510432, 0.0030342932228727597, 8.2991920229771441e-06, 0.99446164937779757, 0.0055269535040442571, 1.1397118157986199e-05, 1.4187068837724371e-11, 0.00016054974935304818, 0.99983945023645981, 5.715327212215367e-11, 0.021193278070079785, 0.97880672187276696, 3.2999678230222699e-10, 0.029728955965103266, 0.97027104370490003, 1.5979272319802827e-09, 0.058484005387143365, 0.94151599301492939, 7.1179770126793832e-09, 0.034830021644765251, 0.96516997123725778, 2.4371933812835587e-08, 0.033594794856526007, 0.96640518077154014, 1.1942460612760051e-07, 0.050868191962605856, 0.94913168861278807, 5.884704560091193e-07, 0.052456570500484724, 0.94754284102905928, 2.8410714601984615e-06, 0.077374795730142401, 0.92262236319839741, 9.3211675545631986e-06, 0.11782901767715663, 0.88216166115528882, 3.9345881457697885e-05, 0.10586954353028988, 0.89409111058825241, 0.0001405174272693304, 0.20967228324452339, 0.79018719932820725, 0.00054998713503999442, 0.2301343614117039, 0.7693156514532562, 0.0012577130436678496, 0.35075699996733722, 0.64798528698899494, 0.028674514115622787, 0.44135027504055413, 0.52997521084382315, 0.0097800513521887865, 0.51474881366893599, 0.47547113497887511, 0.032067924665140454, 0.6052776622641477, 0.36265441307071189, 0.0950402629788107, 0.52662013986132783, 0.37833959715986143, 0.058359927550077247, 0.65123852594302745, 0.29040154650689526, 0.30676510578518651, 0.511511494855586, 0.18172339935922752, 0.39807812005322452, 0.47131611518985894, 0.13060576475691657, 0.69469774016045083, 0.26731493814817442, 0.037987321691374823, 0.61569958793272406, 0.3230686221530723, 0.061231789914203603, 0.72417678120376272, 0.24150383528473066, 0.034319383511506589, 0.91453093874707181, 0.072185692130575421, 0.01328336912235286, 0.94061063280727397, 0.054632533887668429, 0.0047568333050575827, 0.95769458075676495, 0.040201562542849685, 0.0021038567003853945, 0.9627929884309181, 0.036590237600538186, 0.00061677396854360668, 0.96993609453164731, 0.029857981925494666, 0.00020592354285794284, 0.99409111054581212, 0.0058435971952659543, 6.5292258921788846e-05, 0.99566306061244092, 0.0043017670863138048, 3.5172301245249531e-05, 0.98665977709230013, 0.01332140114790183, 1.882175979812223e-05, 0.99726662916713416, 0.0027211872188618036, 1.2183614004143976e-05, 0.93972420864926431, 0.060266574508937097, 9.216841798684859e-06, 0.98591063450261096, 0.014053864888318803, 3.5500609070171877e-05, 1.5722910771986251e-11, 0.00015924225241121373, 0.99984075773186587, 5.4960143058987886e-11, 0.030003593882343266, 0.96999640606269655, 2.6307862914140925e-10, 0.011630614333934525, 0.9883693854029868, 1.2982856773412406e-09, 0.039974285938707624, 0.96002571276300674, 5.4748242528577134e-09, 0.023663936054151687, 0.976336058471024, 3.1316150502647088e-08, 0.027235915413429776, 0.97276405327041982, 1.1321209554098173e-07, 0.042595620639255725, 0.95740426614864882, 5.9795690136218268e-07, 0.017438173155925336, 0.98256122888717334, 2.4649363394370085e-06, 0.053907602548449743, 0.94608993251521079, 7.216653795107126e-06, 0.098960216184005897, 0.90103256716219904, 4.5191500880007834e-05, 0.10229605010773089, 0.89765875839138898, 0.00010975898091841597, 0.14466735403110442, 0.85522288698797722, 0.00038007082176860416, 0.27872926403735859, 0.72089066514087285, 0.0011900061186975064, 0.35078077855185269, 0.64802921532944968, 0.02805540116460423, 0.45341211080212007, 0.51853248803327578, 0.010764024114413793, 0.45329345171126378, 0.53594252417432242, 0.065488732167637911, 0.65519001976821012, 0.27932124806415198, 0.072212199387054393, 0.72245576876949025, 0.20533203184345539, 0.13561030828027243, 0.80012275719790971, 0.06426693452181792, 0.38372846175915604, 0.47988228303541325, 0.13638925520543058, 0.43719277419040659, 0.33645757754889161, 0.22634964826070161, 0.62347075615045644, 0.28788873833801987, 0.088640505511523623, 0.58109227420307807, 0.351371950279949, 0.067535775516973026, 0.79400292795233607, 0.18105297486625949, 0.024944097181404411, 0.9139607174946488, 0.072762585910215269, 0.013276696595135992, 0.95135494406111376, 0.043067632291405651, 0.0055774236474804657, 0.92596556385245343, 0.071261042931099375, 0.0027733932164471053, 0.97306551752294235, 0.026275716114251176, 0.00065876636280652915, 0.98640080969260957, 0.013347995496412926, 0.00025119481097760158, 0.99161869525162583, 0.0082682879375069861, 0.00011301681086729397, 0.98789635835861556, 0.01206780192785129, 3.5839713533250897e-05, 0.99694085974943014, 0.0030367468212366923, 2.2393429333304457e-05, 0.99800256657017805, 0.0019865525553096376, 1.0880874512223259e-05, 0.99821633293335454, 0.0017763860429823425, 7.2810236631001788e-06, 0.99826454295271017, 0.0017301106657655668, 5.3463815241317353e-06, 1.4776740137602711e-11, 0.00013414022858605908, 0.99986585975663733, 4.6300513708786933e-11, 0.01965426030242572, 0.9803457396512737, 2.6234330573059661e-10, 0.00036238377872868313, 0.99963761595892808, 1.613504112766891e-09, 0.00089109455206720872, 0.99910890383442863, 6.1096903584786802e-09, 0.013689582780224219, 0.98631041111008544, 3.806569167025583e-08, 0.017161748835659331, 0.98283821309864894, 1.0076978395624472e-07, 0.019654258322780158, 0.98034564090743592, 4.9559954932050257e-07, 0.044953909537167498, 0.95504559486328322, 2.2987489996242469e-06, 0.013030469946320946, 0.98696723130467956, 7.397591693764927e-06, 0.1464892998856431, 0.85350330252266304, 4.3292944525184965e-05, 0.19050426515518376, 0.80945244190029109, 0.019035109959053019, 0.08789496116983575, 0.89306992887111114, 0.00064689527722181612, 0.23608992967694434, 0.76326317504583385, 0.048395461253001142, 0.29795587884907565, 0.6536486598979232, 0.0046861036728838915, 0.50318430900855238, 0.49212958731856371, 0.01122471857926274, 0.49987869011216157, 0.4888965913085756, 0.12382094198014931, 0.52409996588084928, 0.3520790921390014, 0.1605005119790715, 0.53524899187843811, 0.30425049614249033, 0.20965967811493125, 0.59162113930744409, 0.19871918257762458, 0.29276594099134395, 0.54074079047904344, 0.16649326852961249, 0.49837013587232309, 0.38353883809910699, 0.11809102602856991, 0.69088569763685714, 0.21267847220991304, 0.096435830153229818, 0.63999631213235397, 0.24626620284270148, 0.11373748502494455, 0.72830635497980567, 0.16814838193316983, 0.10354526308702455, 0.92298165842769053, 0.064574005138227406, 0.012444336434082095, 0.95846926195585125, 0.035124991936709524, 0.0064057461074392376, 0.96505439295829154, 0.032290985104160036, 0.0026546219375483543, 0.97242160835875646, 0.026726080921534993, 0.00085231071970847565, 0.98862713876212316, 0.011117265350910083, 0.00025559588696679353, 0.99229982509509329, 0.0075737021569505401, 0.00012647274795616972, 0.97319556615527103, 0.026748499746583349, 5.593409814555021e-05, 0.99710974235865635, 0.002864451988807614, 2.5805652536018087e-05, 0.99759973342109121, 0.0023843118993613281, 1.5954679547526123e-05, 0.9969172245390302, 0.0030674155400210357, 1.5359920948821713e-05, 0.99874827087156437, 0.0012470212936870357, 4.7078347486403233e-06, 9.7450028416373407e-12, 7.9407963503867098e-05, 0.9999205920267511, 5.543497048108002e-11, 0.00017476716041905143, 0.99982523278414592, 1.6522628019573371e-10, 0.00020487056732963453, 0.99979512926744407, 1.1004130796729861e-09, 0.00054552057801935685, 0.99945447832156764, 4.3147419317708209e-09, 0.031764233305951857, 0.9682357623793062, 4.4183598096215622e-08, 0.032724381013353274, 0.96727557480304871, 1.0213216506373892e-07, 0.032724379117022202, 0.96727551875081275, 4.6748150228075886e-07, 0.034830005610293577, 0.96516952690820412, 2.8944680850101307e-06, 0.053907579393366038, 0.94608952613854891, 6.8401858457495187e-06, 0.051350407563475607, 0.94864275225067862, 4.2288229609097081e-05, 0.15284795455060832, 0.84710975721978254, 0.045890069806887993, 0.10594910963041623, 0.84816082056269582, 0.0004039828679425948, 0.27248430824822867, 0.7271117088838287, 0.0014317249600511064, 0.50059847338920349, 0.49796980165074534, 0.0031682920577561806, 0.32875625853129753, 0.66807544941094632, 0.14007213011769412, 0.39525784810192865, 0.46467002178037708, 0.060335162020955097, 0.5107642673509557, 0.42890057062808923, 0.068901196818126897, 0.69698801831644763, 0.23411078486542539, 0.12448441105338233, 0.47900749804456111, 0.39650809090205658, 0.33672714414871358, 0.32392575399099149, 0.33934710186029493, 0.63664263410065269, 0.22270520952530348, 0.14065215637404377, 0.27610128479574603, 0.53120942822384698, 0.19268928698040699, 0.74549517920020447, 0.19124096346480865, 0.063263857334986989, 0.87030326117595458, 0.10304207426413499, 0.026654664559910449, 0.93537072989748393, 0.051417751173010354, 0.013211518929505771, 0.90809120890068074, 0.085373083665776825, 0.0065357074335423357, 0.9565376945801991, 0.04122098491339371, 0.0022413205064071603, 0.95807364609933843, 0.040962242784464434, 0.00096411111619706068, 0.92099342804345152, 0.078753771290981531, 0.00025280066556699032, 0.992442566968611, 0.0074065361038368879, 0.00015089692755214875, 0.99572231550936152, 0.0042148468997504377, 6.2837590888111967e-05, 0.99134726004376938, 0.0085586688949944659, 9.4071061236363082e-05, 0.99802897803884261, 0.0019550608975151362, 1.5961063642100496e-05, 0.99327938162255047, 0.0066798092837178948, 4.0809093731748351e-05, 0.9986311122982684, 0.0013626115141493135, 6.2761875822913219e-06, 6.7388632162049671e-12, 4.9364762207106814e-05, 0.99995063523105399, 4.2433006481895921e-11, 0.051350758810030234, 0.94864924114753679, 1.7257304034797493e-10, 0.00019236307682332141, 0.99980763675060369, 7.5234801343775437e-10, 0.051350758773575561, 0.9486492404740765, 4.9803189007011353e-09, 0.00090208264868298982, 0.9990979123709981, 2.4009290881476715e-08, 0.030858820153509676, 0.9691411558371994, 1.2528099340963286e-07, 0.034830017529144795, 0.96516985718986181, 5.2063787722667725e-07, 0.067315410303138395, 0.93268406905898438, 1.4129672385283775e-06, 0.11416757860757935, 0.88583100842518214, 6.0682881578408014e-06, 0.026351816486843552, 0.97364211522499866, 3.7386115182993796e-05, 0.046899702306341141, 0.95306291157847589, 8.016968117097043e-05, 0.24985439330176415, 0.75006543701706485, 0.00034565980934394023, 0.58441035377936745, 0.41524398641128868, 0.0011304260154092413, 0.31656987858998814, 0.68229969539460267, 0.0035604164419432553, 0.64111987709890883, 0.35531970645914801, 0.0091238402813121691, 0.61324298895716323, 0.37763317076152447, 0.12806014139478231, 0.689873329307228, 0.18206652929798983, 0.046441352413898636, 0.37057007675116349, 0.58298857083493782, 0.29705346121765586, 0.30481103947455324, 0.39813549930779096, 0.32875701438496641, 0.25300690037021911, 0.41823608524481454, 0.58872081446699387, 0.26077382736263455, 0.1505053581703715, 0.8091949032455994, 0.088963618072826628, 0.10184147868157394, 0.8273979804226429, 0.10612569427653497, 0.066476325300822092, 0.79151970053582321, 0.17532851569116747, 0.033151783773009404, 0.90960582233468579, 0.077780021785032058, 0.012614155880282082, 0.92994619328513295, 0.065061260660114972, 0.0049925460547520645, 0.90948288095894547, 0.087490697758068184, 0.0030264212829863866, 0.97536224692630613, 0.023522644634195223, 0.001115108439498745, 0.95494297937251682, 0.043568029563507277, 0.001488991063975965, 0.99252839457658693, 0.0072906289943522121, 0.00018097642906096838, 0.99371392777951295, 0.0061739244113479192, 0.00011214780913929365, 0.996387276765903, 0.0035649814270718389, 4.7741807025164776e-05, 0.99591720423002128, 0.0040425840764449416, 4.0211693533666997e-05, 0.99824821565752853, 0.0017388410567994045, 1.2943285671922303e-05, 0.99858038976050756, 0.0014116878842659047, 7.9223552264642187e-06)

aa31dict={'CYS': 'C', 'GLN': 'Q', 'ILE': 'I', 'SER': 'S', 'VAL': 'V', 'MET': 'M', 'ASN': 'N', 'PRO': 'P', 'LYS': 'K', 'THR': 'T', 'PHE': 'F', 'ALA': 'A', 'HIS': 'H', 'GLY': 'G', 'ASP': 'D', 'LEU': 'L', 'ARG': 'R', 'TRP': 'W', 'GLU': 'E', 'TYR': 'Y'}
aa3s=list(aa31dict.keys());aa3s.sort()#introduce ordering
aa1s=list(aa13dict.keys());aa1s.sort()
aa3s=['ALA','ARG','ASP' ,'ASN' ,'CYS' ,'GLU' ,'GLN' ,'GLY' ,'HIS' ,'ILE' ,'LEU' ,'LYS' ,'MET' ,'PHE' ,'PRO' ,'SER' ,'THR' ,'TRP' ,'TYR' ,'VAL']
aa1s3=[aa31dict[k] for k in aa3s]


class ShiftDict(dict):

    def __init__(self):
        dict.__init__(self)
        self.counts={'H':0,'C':0,'N':0,'P':0}#P is for DNA

    def writeTable(self,pdbID,pref='predictions_',col=0):
        if pref!=None:
            pdbID=''.join(pdbID.split())##+'R'
            fil=open(pref+pdbID+'.out','w')
            fil.write(' NUM    RES      HA       H        N       CA        CB       C   \n')
            fil.write(' ----  ------ -------- ------- -------- -------- -------- --------\n')
        else:fil=open('junk','w')
        ress=list(self.keys())
        ress.sort(lambda x,y: cmp(eval(x),eval(y)))
        ##avedct =dict(zip(['HA','H','N','CA','CB','C'],[SubContainer() for i in range(6)]))
        lavedct=dict(list(zip(['HA','H','N','CA','CB','C'],[SubContainer() for i in range(6)])))
        for res in ress:
            if len(self[res])>0:
                resn=None
                fil.write('  %3s  '%res)
                fil.write('  %1s  '%self[res][list(self[res].keys())[0]][2])#generalize
                for at in ['HA','H','N','CA','CB','C']:
                    if at in self[res]:
                        vals=self[res][at];shift=vals[col]
                        fil.write(' %8.4f'%shift)
                        if shift>0.0:
                            ##avedct[at].update(shift)
                            lavedct[at].update(log(shift))
                    else:
                        fil.write('   0.0000')
                fil.write('\n')
        fil.close()
        ##return avedct,lavedct
        return lavedct


class Parser:

    def __init__(self,buf):
        self.buffer=buf
        self.start=0
        self.numlines=len(buf)
        self.terminated=False

    def search(self,s='',s2=None,stopstr=None,stop=-1,numhits=1,changeStart=True,
               doReturn=True,positions=None,positions2=None,incr=1,verb=False):
        hits=0
        for k in range(self.start,len(self.buffer)):
            match=False
            if stopstr=='':
                if self.buffer[k]==[]:return None
            if s=='':#to nearest new-line
                if self.buffer[k]==[]:match=True
            elif s=='noneblank':
                if len(self.buffer[k])>0:
                    match=True
            if s!='' or stopstr!=None:
                if positions==None:searchlist=list(range(len(self.buffer[k])))
                else:searchlist=positions
                for j in searchlist:
                    if len(self.buffer[k])>j:
                        if self.buffer[k][j]==s:
                            if verb:print(self.buffer[k])
                            if s2==None:match=True
                            else:
                                if positions2==None:searchlist2=list(range(len(self.buffer[k])))
                                else:searchlist2=positions2
                                for j2 in searchlist2:
                                    if self.buffer[k][j2]==s2:
                                        match=True
                        if self.buffer[k][j]==stopstr:return None
            if match:
                if verb:print('matching')
                if verb:print(self.buffer[k])
                if changeStart:self.start=k+incr
                hits+=1
                if hits==numhits:
                    if doReturn:return k+incr
                    break
        self.terminated=True

    def getExcerpt(self,end=None):
        if end==None:end=self.numlines
        return self.buffer[self.start:end]

    def getCurrent(self):
        return self.buffer[self.start]

    def findShiftData(self,ch,verb=True,skipCO=False):
        self.search(s="_Saveframe_category",s2='assigned_chemical_shifts',
                    positions=[0],positions2=[1])
        print('finding NMR shifts for chain',ch)
        if verb:print(self.start)
        li,mi=None,None
        while mi==None:
            li=self.search(s='loop_')
            mi=self.search(s='_Chem_shift_value',stopstr='')
            if verb:print(li,mi)
            if self.terminated:
                return ShiftDict()#empty
                print('WARNING: no _Chem_shift_value entry found')
        pos=mi-li-1
        idict={}
        self.search()#nearest blank
        for i in range(self.start-li-1):
            if verb:print('**',i,self.buffer[li+i])
            key=self.buffer[li+i][0][1:]
            idict[key]=i
        if verb:print(idict)
        startI=self.search('noneblank',incr=0)
        endI=self.search(incr=0)
        return getShiftDBA(startI,endI,self.buffer,ch,idict,skipCO=skipCO)

    def findShiftData31(self,ch,verb=True):
        if verb:print(self.start)
        li,mi=None,None
        while mi==None:
            li=self.search(s='loop_')
            mi=self.search(s='_Atom_chem_shift.Val',stopstr='')
            if verb:print(li,mi,self.start)
        pos=mi-li-1
        idict={}
        self.search()#nearest blank
        for i in range(self.start-li-1):
            if verb:print('**',i,self.buffer[li+i])
            key=self.buffer[li+i][0][1:]
            idict[key]=i
        if verb:print(idict)
        startI=self.search('noneblank',incr=0)
        endI=self.search(incr=0)
        if verb:print(startI,endI)
        return getShiftDBA31(startI,endI,self.buffer,ch,idict)

    def findReference(self,verb=True):
        self.search(s="_Saveframe_category",s2='chemical_shift_reference',
                    positions=[0],positions2=[1])
        print('finding reference')
        if verb:print(self.start)
        li,mi=None,None
        while mi==None:
            li=self.search(s='loop_')
            mi=self.search(s='_Mol_common_name',stopstr='')
            if verb:print(li,mi)
            if self.terminated:
                print('WARNING: no _Mol_common_name entry found')
                return None
        pos=mi-li-1
        idict={}
        self.search()#nearest blank
        for i in range(self.start-li-1):
            if verb:print('**',i,self.buffer[li+i])
            key=self.buffer[li+i][0][1:]
            idict[key]=i
        if verb:print(idict)
        startI=self.search('noneblank',incr=0)
        endI=self.search(incr=0)
        ##return [self.buffer[i][idict['Mol_common_name']] for i in range(startI,endI)]
        return [self.buffer[i][pos] for i in range(startI,endI)]

    def findSampleConditions(self,verb=True):
        self.search(s="_Saveframe_category",s2='sample_conditions',
                    positions=[0],positions2=[1])
        print('finding sample conditions')
        if verb:print(self.start)
        li,mi=None,None
        while mi==None:
            li=self.search(s='loop_')
            mi=self.search(s='_Variable_type',stopstr='')
            if verb:print(li,mi)
            if self.terminated:
                print('WARNING: no _Variable_type entry found')
                return None
        pos=mi-li-1
        idict={}
        self.search()#nearest blank
        for i in range(self.start-li-1):
            if verb:print('**',i,self.buffer[li+i])
            key=self.buffer[li+i][0][1:]
            idict[key]=i
        if verb:print(idict)
        startI=self.search('noneblank',incr=0)
        endI=self.search(incr=0)
        dct={}
        for i in range(startI,endI):
            lin=self.buffer[i]
            key=lin[pos]
            if key[0]=="'":
                key=key[1:]
                for k in range(1,10):
                    wordk=lin[pos+k]
                    key+=(' '+wordk)
                    if wordk[-1]=="'":
                        key=key[:-1]
                        break
                ##dct[key]=lin[pos+k+1]
                dct[key]=(lin[pos+k+1],lin[pos+k+1+2])#value,unit
            else:
                dct[key]=lin[pos+1]
        return dct

    def findDatabaseMatches(self,verb=False):
        dct={}
        self.start=0
        k=self.search('_Database_name')
        if k==None:
            print('warning no database matches')
            return {}
        for i in range(len(self.buffer)-k):
            lin=self.buffer[k+i]
            if len(lin)>0:
                if lin[0]=='stop_':return dct
            if len(lin)>1:
                dbnam=lin[0]
                if not dbnam in dct:dct[dbnam]=[]
                if dbnam in ['BMRB','PDB','DBJ','EMBL','GB','REF','SP','TPG']:
                    dbid=lin[1]
                    dct[dbnam].append(dbid)

def getShiftDBA31(start,end,buf,chnum,idict,includeLabel=True,includeAmb=False):
    dba=ShiftDict()
    for lst in buf[start:end]:
        ambc=lst[idict['Atom_chem_shift.Ambiguity_code']]
        ##if ambc in ['1','.']:
        ##if ambc in ['1','.','2']:#to include GLY
        if True:
        ##if ambc in ['1','2','3','.']:#unamb, geminal, arom (sym degenerate), None
            val=lst[idict['Atom_chem_shift.Val_err']]
            if val=='.':std=None
            else:std=float(val)
            if std==None or std<=1.3:#was 1.3
                elem=lst[idict['Atom_chem_shift.Atom_type']]
                res=lst[idict['Atom_chem_shift.Seq_ID']]
                rl3=lst[idict['Atom_chem_shift.Comp_ID']]
                at= lst[idict['Atom_chem_shift.Atom_ID']]
                avg=float(lst[idict['Atom_chem_shift.Val']])
                if res not in dba:dba[res]={}
                dba[res][at]=[avg,std,rl3,ambc]
                dba.counts[elem]+=1
            else:print('skipping',std)
    return dba

def getShiftDBA(start,end,buf,chnum,idict,includeLabel=True,includeAmb=True,skipCO=False):#was includeAmb=False
    dba=ShiftDict()
    for lst in buf[start:end]:
        ambc=lst[idict['Chem_shift_ambiguity_code']]
        ##if ambc in ['1','.']:
        ##if ambc in ['1','.','2']:#to include GLY
        if True:
        ##if ambc in ['1','2','3','.']:#unamb, geminal, arom (sym degenerate), None
            val=lst[idict['Chem_shift_value_error']]
            ##if val=='.':std=None
            if val in ['.','@']:std=None
            else:std=float(val)
            if std==None or std<=1.3:#was 1.3
                elem=lst[idict['Atom_type']]
                res=lst[idict['Residue_seq_code']]
                rl3=lst[idict['Residue_label']]
                at= lst[idict['Atom_name']]
                avg=float(lst[idict['Chem_shift_value']])
                if res not in dba:dba[res]={}
                if not (skipCO and at=='C'):
                    if includeLabel:
                        if includeAmb:
                            dba[res][at]=[avg,std,rl3,ambc]
                        else:
                            dba[res][at]=[avg,std,rl3]
                    else:
                        if includeAmb:
                            dba[res][at]=[avg,std,'X',ambc]
                        else:
                            dba[res][at]=[avg,std,'X']
                dba.counts[elem]+=1
                ##print res,rl3,at,avg,ambc
                ##print dba[res][at]
            else:print('skipping',std)
    ##dba.show()
    if False:#includeAmb:
        dba.defineambiguities()
        dba.show()
    return dba

def convChi2CDF(rss,k):
    return ((((rss/k)**(1.0/6))-0.50*((rss/k)**(1.0/3))+1.0/3*((rss/k)**(1.0/2)))\
            - (5.0/6-1.0/9/k-7.0/648/(k**2)+25.0/2187/(k**3)))\
            / sqrt(1.0/18/k+1.0/162/(k**2)-37.0/11664/(k**3))



class ShiftGetter:

    def __init__(self, bmrID, overwrite=True, from_bmrb=False):
        self.bmrID=bmrID
        path = os.getcwd()
        if from_bmrb:
          bmrname= os.path.join(path, 'bmr'+self.bmrID+'.str')
        else:
          bmrname= os.path.join(path, self.bmrID+'.str')

        print('opening bmr shift file', bmrname)
        if not os.path.exists(bmrname) or overwrite:
            print(('getting bmrfile ' + self.bmrID))
            bmrpath = 'https://bmrb.io/ftp/pub/bmrb/entry_directories/bmr%s/bmr%s_31.str' % (self.bmrID, self.bmrID) # THIS NEEDS UPDATE
            try:
                response = requests.get(bmrpath)
            except:
                print('Error in downloading from BMRB')
                return
            f = open(bmrname, 'w')
            f.write(response.text)
            f.close()
        buf=initfil2(bmrname)
        parser=Parser(buf)
        parser.search(s="Polymer",s2='residue',positions=[1],positions2=[2])
        self.dbdct={}
        self.title='no title...'
        seq=''
        if True:
            k=parser.search('_Mol_residue_sequence')
            if k==None:raise SystemExit("no sequence found (bmrID might not exist) %s"%self.bmrID)
            k-=1
            ##print 'try buf[k]',buf[k]
            if len(buf[k])>1:
                seq=buf[k][1]
                print('found sequence',seq)
        if len(seq)==0:
            i0=parser.search(s=";",positions=[0])
            print(i0)
            if i0==None:
                print('warning no residues found (maybe missing semicolons?)',self.bmrID)
                self.moldba=ShiftDict()#counts er all 0
                return
            i1=parser.search(s=";",positions=[0])
            for i in range(i0,i1-1):
                if len(buf[i])>0:#some lines can be blank
                    seq+=buf[i][0]
        ##print i0,i1,seq
        seq=seq.upper()
        self.seq=seq
        if len(seq)<10:
            print('WARNING small or empty sequence!')
            self.moldba=ShiftDict()#counts er all 0
            return
        print('seq: ',seq)
        xcount=seq.count('X')
        xcount+=seq.count('U')#RNA
        print('xcount:',self.bmrID,xcount)
        if xcount>5 or xcount*1.0/len(seq)>0.15:
            print('warning: high xcount',xcount,seq)
            self.moldba=ShiftDict()#counts er all 0
            return
        moldba=parser.findShiftData('none',verb=False,skipCO=False)
        print(moldba.counts)
        self.moldba=moldba
        parser.start=0
        self.title = ID
        print(self.title)
        self.references=parser.findReference(verb=False)
        print(self.references)
        parser.start=0
        parser.terminated=False#OK?
        conddct=parser.findSampleConditions(verb=False)
        print(conddct)
        self.pH=-9.99
        self.temperature=999.9
        if 'pH' in conddct:
          if conddct['pH']=='.':
            self.pH=-9.99
          else:
            self.pH=eval(conddct['pH'])
        if 'temperature' in conddct:
          if conddct['temperature']=='.':
            self.temperature=-999
          else:
            self.temperature=eval(conddct['temperature'])
        if 'ionic strength' in conddct:
          ionstr=conddct['ionic strength'][0]
          if ionstr in ['.',' ','']:
            self.ion=0.1
          else:
            self.ion=eval(conddct['ionic strength'][0])
          unit=conddct['ionic strength'][1]
          if unit=='mM':
            self.ion/=1000.0
        else:
          #self.ion=0.1
          self.ion=ionic_strength
        parser.start=0
        k=parser.search('_System_physical_state')
        if k==None:
            print('warning: phys_state not defined in bmrbfile',self.bmrID)
            self.phys_state='unknown'
        else: self.phys_state= ' '.join(buf[k-1][1:])
        print(self.phys_state)
        print('summary_info: %5s %4.2f %5.1f %3d'%(self.bmrID,self.pH,self.temperature,len(self.seq)), end=' ')
        print(self.phys_state, end=' ')
        print(self.title)
        self.dbdct=parser.findDatabaseMatches(verb=True)
        print(self.dbdct)
        if False:##self.bmrID=='5387':
            #out=open('allshifts5387w2.dat','w')
            out=open('allshifts5387w3.dat','w')
            self.xcamformat(out)

    def write_rereferenced(self,lacsoffs):
        out=open('rereferenced/bmr%s.str'%self.bmrID,'w')
        out.write('data_%s\n'%self.bmrID)
        out.write('''
#######################
#  Entry information  #
#######################

save_entry_information
   _Saveframe_category      entry_information

   _Entry_title
;
''')
        out.write('%s\n'%self.title)
        out.write(';\n')
        out.write('''
        ##############################
        #  Polymer residue sequence  #
        ##############################

''')
        s=self.seq
        out.write('_Residue_count   %d\n'%len(s))
        out.write('''_Mol_residue_sequence
;
''')
        for i in range((len(s)-1)/20+1):
            out.write('%s\n'%s[i*20:min(len(s),(i+1)*20)])
        out.write('''

        ###################################
        #  Assigned chemical shift lists  #
        ###################################

save_assigned_chem_shift_list_1
   _Saveframe_category               assigned_chemical_shifts

   loop_
      _Atom_shift_assign_ID
      _Residue_author_seq_code
      _Residue_seq_code
      _Residue_label
      _Atom_name
      _Atom_type
      _Chem_shift_value
      _Chem_shift_value_error
      _Chem_shift_ambiguity_code

''')
        cnt=1
        for i in range(len(s)):
            res=str(i+1)
            if res in self.moldba:
                shdct=self.moldba[res]
                for at in shdct:
                    shave,shstd,rl3,ambc=shdct[at]
                    if at in lacsoffs:refsh=shave+lacsoffs[at]
                    else:refsh=shave
                    if shstd==None:
                        if at[0] in 'CN':shstd=0.3
                        else:shstd=0.05
                    data=(cnt,res,res,rl3,at,at[0],refsh,shstd,ambc);print(data)
                    out.write('     %4d %3s %3s %3s %-4s %1s %7.3f %4.2f %1s\n'%data)
                    cnt+=1
        out.write('''

   stop_

save_
''')
        out.close()

    def writeShiftY(self,out):
        header='#NUM AA HA CA CB CO N HN'
        bbatns =['HA','CA','CB','C','N','H']##,'HA3','HB','HB2','HB3']
        out.write(header+'\n')
        seq=self.seq
        for i in range(1,len(seq)-1):
            res=str(i+1)
            resi=seq[i]
            out.write('%s %1s'%(res,resi))
            if res in self.moldba:
                shdct=self.moldba[res]
                for at in bbatns:
                    sho=0.0
                    if resi=='G' and at=='HA':
                        if 'HA2' in shdct and 'HA3' in shdct:
                            sho=(shdct['HA2'][0]+shdct['HA3'][0])/2
                    if at in shdct:
                        sho=shdct[at][0]
                    out.write(' %7.3f'%sho)
            out.write('\n')

    def cmp2pred1(self,verb=False):
        seq=self.seq
        predshiftdct=potenci(seq,self.pH,self.temperature,self.ion)
        bbatns0=['C','CA','CB','HA','H','N']
        bbatns =['C','CA','CB','HA','H','N','HB']##'HA2','HA3','HB','HB2','HB3']
        ##bbatns =['C','CA','CB','H','N']##'HA2','HA3','HB','HB2','HB3']
        cmpdct={}
        self.shiftdct={}
        for i in range(1,len(seq)-1):
            res=str(i+1)
            ##if res in self.moldba:
            if res in self.moldba and seq[i] in aa1s:
                trip=seq[i-1]+seq[i]+seq[i+1]
                shdct=self.moldba[res]
                for at in bbatns:
                    sho=None
                    if at in shdct:
                        sho=shdct[at][0]
                    elif seq[i]=='G' and at=='HA' or at=='HB':
                        shs=[]
                        for pref in '23':
                            atp=at+pref
                            if atp in shdct:
                                shs.append(shdct[atp][0])
                        if len(shs)>0:sho=average(shs)
                    if sho!=None:
                        if i==1:
                            pent='n'+     trip+seq[i+2]
                        elif i==len(seq)-2:
                            pent=seq[i-2]+trip+'c'
                        else:
                            pent=seq[i-2]+trip+seq[i+2]
                        ##shp=refinedpred(paramdct[at],pent,at,tempdct,self.temperature)
                        if not (seq[i]=='C' and at in ('CA','CB')):
                            try:
                                shp=predshiftdct[(i+1,seq[i])][at]
                            except:
                                shp = None
                            if shp!=None:
                                self.shiftdct[(i,at)]=[sho,pent]
                                diff=sho-shp
                                if verb:print('diff is:',self.bmrID,i,seq[i],at,sho,shp,abs(diff),diff)
                                if not at in cmpdct:cmpdct[at]={}
                                cmpdct[at][i]=diff
        return cmpdct

    def visresults(self,dct,doplot=True,dataset=None,offdct=None,label='',minAIC=999.0,lacsoffs=None,cdfthr=6.0):##6.0):#was minAIC=9.0
        shout=open('shifts%s.txt'%self.bmrID,'w')
        bbatns=['C','CA','CB','HA','H','N','HB']
        cols='brkgcmy'
        refined_weights={'C':0.1846,'CA':0.1982,'CB':0.1544,'HA':0.02631,'H':0.06708,'N':0.4722,'HB':0.02154}
        outlivals={'C':5.0000,'CA':7.0000,'CB':7.0000,'HA':1.80,   'H':2.30,   'N':12.00, 'HB':1.80}
        dats={}
        maxi=max([max(dct[at].keys()) for at in dct])
        mini=min([min(dct[at].keys()) for at in dct])#is often 1
        nres=maxi-mini+1
        resids=list(range(mini+1,maxi+2))
        self.mini=mini
        tot=zeros(nres)
        newtot=zeros(nres)
        newtotsgn=zeros(nres)
        newtotsgn1=zeros(nres)
        newtotsgn2=zeros(nres)
        totnum=zeros(nres)
        allrmsd=[]
        totbbsh=0
        oldct={}
        allruns=zeros(nres)
        rdct={}
        sgnw={'C':1.0,'CA':1.0,'CB':-1.0,'HA':-1.0,'H':-1.0,'N':-1.0,'HB':1.0}#was 'HB':0.0
        ##wbuf=initfil2('weights_oplsda123new7');wdct={}
        wbuf=[['weights:', 'N', '-0.0626', '0.0617', '0.2635'], ['weights:', 'C', '0.2717', '0.2466', '0.0306'], ['weights:', 'CA', '0.2586', '0.2198', '0.0394'], ['weights:', 'CB', '-0.2635', '0.1830', '-0.1877'], ['weights:', 'H', '-0.3620', '1.3088', '0.3962'], ['weights:', 'HA', '-1.0732', '0.4440', '-0.4673'], ['weights:', 'HB', '0.5743', '0.2262', '-0.3388']]
        wdct={}
        for lin in wbuf:wdct[lin[1]]=[eval(lin[n]) for n in (2,3,4)]#lin[2] is first component
        for at in dct:
            vol=outlivals[at]
            subtot=zeros(nres)
            subtot1=zeros(nres)
            subtot2=zeros(nres)
            if dataset!=None:dataset[at][self.bmrID]=[]
            A=array(list(dct[at].items()))
            totbbsh+=len(A)
            I=bbatns.index(at)
            w=refined_weights[at]
            shw=A[:,1]/w
            off=average(shw)
            rms0=sqrt(average(shw**2))
            if offdct!=None:
                shw-=offdct[at]#offset correction
                ##print 'using predetermined offset correction',at,offdct[at],offdct[at]*w
            ##shw-=off
            shwl=list(shw)
            for i in range(len(A)):
                resi=int(A[i][0])-mini#minimum value for resi is 0
                ashwi=abs(shw[i])
                if ashwi>cdfthr:oldct[(at,resi)]=ashwi
                tot[resi]+=(min(4.0,ashwi)**2)
                for k in [-1,0,1]:
                    if 0<=resi+k<len(subtot):##maxi:
                        ##subtot[resi+k]+=(shw[i]*w*wdct[at][0])
                        subtot[resi+k]+=(clip(shw[i]*w,-vol,vol)*wdct[at][0])
                        ##subtot1[resi+k]+=(shw[i]*w*wdct[at][1])
                        subtot1[resi+k]+=(clip(shw[i]*w,-vol,vol)*wdct[at][1])
                        subtot2[resi+k]+=(clip(shw[i]*w,-vol,vol)*wdct[at][2])
                totnum[resi]+=1
                if offdct==None:
                    if 3<i<len(A)-4:
                        vals=shw[i-4:i+5]
                        runstd=std(vals)
                        allruns[resi]+=runstd
                        if not resi in rdct:rdct[resi]={}
                        rdct[resi][at]=average(vals),sqrt(average(vals**2)),runstd
            dats[at]=shw
            stdw=std(shw)
            dAIC=log(rms0/stdw)*len(A)-1
            ##print 'rmsd:',at,stdw,off,dAIC
            allrmsd.append(std(shw))
            if doplot:
                subplot(511)
                ##sca=scatter(A[:,0]+1,shw,alpha=0.5,s=25,faceted=False,c=cols[I])
                #sca=scatter(A[:,0]+1,shw*w*wdct[at][0]*16,alpha=0.5,s=25,faceted=False,c=cols[I])
                sca=scatter(A[:,0]+1,shw*w*wdct[at][0]*16,alpha=0.5,s=25,c=cols[I])
                plot((mini+1,maxi+1),[0.0,0.0],'k--')
                axis([mini+1,max(resids),-20,20])
            newtot+=((subtot/3.0)**2)
            newtotsgn+=subtot
            newtotsgn1+=subtot1
            newtotsgn2+=subtot2
        T0=list(tot/totnum)
        cdfs=convChi2CDF(tot,totnum)
        Th=list(tot/totnum*0.5)
        tot3=array([0,0]+Th)+array([0]+T0+[0])+array(Th+[0,0])
        Ts=list(tot)
        Tn=list(totnum)
        tot3f=array([0,0]+Ts)+array([0]+Ts+[0])+array(Ts+[0,0])
        totn3f=array([0,0]+Tn)+array([0]+Tn+[0])+array(Tn+[0,0])
        cdfs3=convChi2CDF(tot3f[1:-1],totn3f[1:-1])
        newrms=(newtot*3)/totn3f[1:-1]
        newcdfs=convChi2CDF(newtot*3,totn3f[1:-1])
        avc=average(cdfs3[cdfs3<20.0])
        numzs=len(cdfs3[cdfs3<20.0])
        numzslt3=len(cdfs3[cdfs3<cdfthr])
        stdcp=std(cdfs3[cdfs3<20.0])
        atot=sqrt(tot3/2)[1:-1]
        aresids=array(resids)
        if offdct==None:
            tr=(allruns/totnum)[4:-4]
            offdct={}
            mintr=None;minval=999
            for j in range(len(tr)):
                if j+4 in rdct and len(rdct[j+4])==len(dct):#all ats must be represented for this res
                ##if j+4 in rdct and len(rdct[j+4])>=len(dct)-1:#all ats (except one as max) must be represented for this res
                    if tr[j]<minval:
                        minval=tr[j]
                        mintr=j
            if mintr==None:return None#still not found
            print(len(tr),len(resids[4:-4]),len(atot),mintr+4,min(tr),tr[mintr])##,tr
            for at in rdct[mintr+4]:
                roff,std0,stdc=rdct[mintr+4][at]
                dAIC=log(std0/stdc)*9-1
                print('minimum running average',at,roff,dAIC)
                if dAIC>minAIC:
                    print('using offset correction:',at,roff,dAIC,self.bmrID,label)
                    offdct[at]=roff
                else:
                    print('rejecting offset correction due to low dAIC:',at,roff,dAIC,self.bmrID,label)
                    offdct[at]=0.0
            return offdct #with the running offsets
        if dataset!=None:
            csgns= newtotsgn/totn3f[1:-1]*10
            csgnsq=newtotsgn/sqrt(totn3f[1:-1])*10
            for I in range(len(resids)):
                pass##print 'datapoints:',self.bmrID,resids[I],csgns[I],cdfs3[I],csgnsq[I],totn3f[1:-1][I]
        if doplot:
            subplot(512)
            plot(resids,newtotsgn/sqrt(totn3f[1:-1])*8.0,'r-')
            plot(resids,newtotsgn1/sqrt(totn3f[1:-1])*8.0,'b-')
            ##plot(resids,newtotsgn2/sqrt(totn3f[1:-1])*8.0,'m-') #PC3
            plot(resids,cdfs3,'k-')
            ##plot((mini+1,maxi+1),[cdfthr,cdfthr],'g--')
            plot((mini+1,maxi+1),[8.0,8.0],'g--')
            plot((mini+1,maxi+1),[0.0,0.0],'k--')
            axis([mini+1,max(resids),-16,16])
            title('CheSPI components CheZOD Z-scores for: %s'%self.bmrID)
        if True:
            sferr3=0.0
            for at in dats:
                I=bbatns.index(at)
                ashw=abs(dats[at])
                Terr=linspace(0.0,5.0,26)
                ferr=array([sum(ashw>T) for T in Terr])*1.0/len(ashw)+0.000001
                sferr3+=ferr[15]#3.0std-fractile
            aferr3=sferr3/len(dats)
            F=zeros(2)
            for at in dats:
                ashw=abs(dats[at])
                fners=sum(ashw>1.0)*1.0/len(ashw),sum(ashw>2.0)*1.0/len(ashw)
                ##print 'fnormerr:',at,fners[0],fners[1]
                F+=fners
            totnorm=sum(atot>1.5)*1.0/len(atot)
            outli0=aresids[atot>1.5]
            outli1=aresids[cdfs>cdfthr]
            outli3=aresids[cdfs3>cdfthr]
            newoutli3=aresids[newcdfs>cdfthr]
            finaloutli=[i+mini+1 for i in range(nres) if cdfs[i]>cdfthr or cdfs3[i]>cdfthr and cdfs[i]>0.0 and totnum[i]>0]
            ##print 'outliers:',self.bmrID,len(outli0),len(outli1),len(outli3),len(finaloutli),sum(totnum==0)##,finaloutli
            Fa=F/len(dats)
            fout=len(finaloutli)*1.0/nres
            print(len(oldct),mini,maxi,nres,aresids[totnum==0])
            print('summary_stat: %5s %5d %6.3f %6.3f %6.3f %6.3f %6.3f %6.3f %4d'%\
             (self.bmrID, sum(list(self.moldba.counts.values())),
              average(allrmsd), Fa[0], Fa[1],
              fout, aferr3, totnorm, totbbsh))

        #now accumulate the validated data
        atns=list(dct.keys())
        accdct=dict(list(zip(atns,[[] for _ in atns])))
        numol=0
        iatns=list(self.shiftdct.keys());iatns.sort()
        for i,at in iatns:#i is seq enumeration (starting from 0, but terminal allways excluded)
            I=bbatns.index(at)
            w=refined_weights[at]
            ol=False
            if i+1 in finaloutli:ol=True
            elif (at,i-mini) in oldct:ol=True
            if not ol:
                accdct[at].append(dct[at][i])
            else:numol+=1
            if dataset!=None:
                dataset[at][self.bmrID].append(self.shiftdct[(i,at)]+[ol])
                vals=dataset[at][self.bmrID][-1]
                shout.write('%3d %2s %7.3f %5s %6.3f\n'%(i+1,at,vals[0],vals[1],dct[at][i]))
        sumrmsd=0.0;totsh=0
        newoffdct={}
        for at in accdct:
            I=bbatns.index(at)
            w=refined_weights[at]
            vals=accdct[at]
            vals=array(vals)/w
            anum=len(vals)
            if anum==0:newoffdct[at]=0.0
            else:
                aoff=average(vals)
                astd0=sqrt(average(array(vals)**2))
                astdc=std(vals)
                adAIC=log(astd0/astdc)*anum-1
                if adAIC<minAIC or anum<4:
                    print('rejecting offset correction due to low adAIC:',at,aoff,adAIC,anum,self.bmrID,label, end=' ')
                    if lacsoffs!=None and at in lacsoffs:print('LACS',lacsoffs[at],-aoff*w)
                    else:print()
                    astdc=astd0
                    aoff=0.0
                    shout.write('off %2s   0.0\n'%at)
                else:
                    print('using offset correction:',at,aoff,adAIC,anum,self.bmrID,label, end=' ')
                    if lacsoffs!=None and at in lacsoffs:print('LACS',lacsoffs[at],-aoff*w)
                    else:print()
                    shout.write('off %2s %7.3f\n'%(at,aoff*w))
                sumrmsd+=(astdc*anum);totsh+=anum
                ##print 'accepted stats: %2s %3d %6.3f %5.3f %5.3f %6.3f'%(at,anum,aoff,astd0,astdc,adAIC)
                newoffdct[at]=aoff
        compl=calc_complexity(cdfs3,self.bmrID,thr=cdfthr)
        fullrmsd=average(allrmsd)
        ps=self.phys_state
        ps6=ps.strip("'")[:6]
        fraczlt3=numzslt3*1.0/numzs
        if totsh==0:avewrmsd,fracacc=9.99,0.0
        else:avewrmsd,fracacc=sumrmsd/totsh,totsh/(0.0+totsh+numol)
        allsh=sum(totnum)
        ratsh=allsh*1.0/numzs
        print('finalstats %5s %8s %6s %7.4f %6.4f %6.4f %4d %4d %4d %7.3f %3d %3d %4d %6.4f %6.4f %7.3f %8.5f'\
          %(self.bmrID,label,ps6,avewrmsd,fullrmsd,fracacc,nres,totsh,numol,avc,numzs,numzslt3,allsh,fraczlt3,ratsh,stdcp,compl))##,
        if dataset!=None:
            fracol3=len(outli3)*1.0/len(totnum>0)
            newfracol3=len(newoutli3)*1.0/len(totnum>0)
            if newfracol3<=0:lratf=0.0
            else:lratf=log(fracol3/newfracol3)
            ##print 'fraccdfs3gt3 %5s %7.4f %7.4f %6.3f'%(self.bmrID,fracol3,newfracol3,lratf)
            if doplot:
                subplot(511)
                ##title('%5s %5.3f %5.3f '%(self.bmrID,1-fracol3,compl)+self.title[:60])
                title('Weighted secondary chemical shifts for: %s'%self.bmrID)
            ##return cdfs3,newtotsgn/sqrt(totn3f[1:-1])*8.0,newtotsgn1/sqrt(totn3f[1:-1])*8.0
            return resids,cdfs3,newtotsgn/sqrt(totn3f[1:-1])*8.0,newtotsgn1/sqrt(totn3f[1:-1])*8.0,newtotsgn2/sqrt(totn3f[1:-1])*8.0
        print()
        return avewrmsd,fracacc,newoffdct,cdfs3 #offsets from accepted stats

    def savedata(self,cdfs3,pc1ws,pc2ws,pc3ws):
        ##out=open('zscores%s.txt'%self.bmrID,'w')
        out=open('components%s.txt'%self.bmrID,'w')
        s=self.seq
        for i,x in enumerate(cdfs3):
            if x<99:#not nan
                I=i+self.mini
                aai=s[I]
                pci1=pc1ws[i]
                pci2=pc2ws[i]
                pci3=pc3ws[i]
                ##out.write('%s %3d %6.3f %6.3f %6.3f\n'%(aai,I+1,x,pci1,pci2))
                out.write('%s %3d %6.3f %6.3f %6.3f %6.3f\n'%(aai,I+1,x,pci1,pci2,pci3))
        out.close()

def calc_borders(c,ID,thr=3.0,lim=10,lim2=10,verb=False):
    a=''
    for x in c:
        if x<thr:a+='0'
        elif x>=thr:a+='1'
        else:a+='-'
    ##a='00000000000000000111111100000----0000000111111111111111111111110000-0000-00000011111--1111111000'
    borders=[]
    prev='-'
    nancounts=[0]
    for i,x in enumerate(a):
        if x!=prev and prev!='-' and x!='-':
            borders.append(i)
            nancounts.append(0)
        if x!='-':prev=x
        else:nancounts[-1]+=1
    N=len(a)
    first=a[0]
    ni=first!='0'
    b0=array([0]+borders)
    b1=array(borders+[N])
    d=b1-b0
    if verb:
        print(borders)
        print(d)
        print(nancounts)
    lst=[]
    for j,dj in enumerate(d):
        if j%2==ni and dj>lim:
            if dj-nancounts[j]>lim2:
                if verb:print('idrs:',ID,j,dj,b0[j:j+2],dj-nancounts[j])
                lst.append((dj,dj-nancounts[j],b0[j:j+2]))
                if nancounts[j]>0:
                    print('testidrs:',ID,lim,lim2,j,dj,b0[j:j+2],dj-nancounts[j])
    return lst
##calc_borders([0,6],'test',lim=15,lim2=11,verb=True)
##1/0

def calc_complexity(c,ID,thr=3.0,ret=1,verb=False):
    ##c=array([random.rand() for _ in range(1000)])
    ##a=c<0.5
    if isinstance(c[0],str):a=c
    else:
        a=''
        for x in c:
            if x<thr:a+='0'
            elif x>=thr:a+='1'
            else:a+='-'
    ##a='000000000000000001111111000000000----000000000001111111111111111111111100000000000000111111111111'
    ##print 'binstr:',a
    ##print a.count('-')
    borders=[]
    prev='-'
    for i,x in enumerate(a):
        if x!=prev and prev!='-' and x!='-':
            borders.append(i)
        if x!='-':prev=x
    if verb:print(len(borders))
    if verb:print(borders)
    N=len(a)
    b0=array([0]+borders)
    b1=array(borders+[N])
    d=b1-b0
    f=d*1.0/N
    s=sum(f*log(f))
    entr=exp(-s)-1
    ##if isinstance(c[0],str):nonnans=array([True]*len(a))
    if isinstance(c[0],str):avc=9.999
    else:
        nonnans=c<10.0
        avc=average(c[nonnans])
    if verb:print('entropy: %5s %7.4f %8.5f %6.3f'%(ID,entr,entr/N,avc))
    if ret==1:return entr/N
    else:return entr/N,d

def getCheZODandPCs(ID,usetcor=True,minAIC=5.0, from_bmrb=True):
    bbatns=['C','CA','CB','HA','H','N','HB']
    dataset=dict(list(zip(['HA','H','N','CA','CB','C','HB'],[{} for _ in range(7)])))
    refined_weights={'C':0.1846,'CA':0.1982,'CB':0.1544,'HA':0.02631,'H':0.06708,'N':0.4722,'HB':0.02154}
    sg=ShiftGetter(ID, overwrite=False, from_bmrb=from_bmrb)
    # ionic strength from the google colab form.
    if not usetcor:sg.temperature=298.0
    totsh=sum(sg.moldba.counts.values())
    print(totsh,sg.seq)
    if sg.moldba.counts['P']>1 or 'U' in sg.seq:
        raise SystemExit('skipping DNA/RNA %s %s'%(ID,sg.title))
    if len(sg.seq)<5:## or totsh/len(sg.seq)<1.5:
        raise SystemExit('too short sequence or too few shifts %s %s'%(ID,sg.title))
    dct=sg.cmp2pred1()
    totbbsh=sum([len(list(dct[at].keys())) for at in dct])
    print('total backbone shifts:',totbbsh)
    offr=sg.visresults(dct,False,minAIC=minAIC)
    if offr!=None:
        atns=list(offr.keys())
        off0=dict(list(zip(atns,[0.0 for _ in atns])))
        armsdc,frac,noffc,cdfs3c=sg.visresults(dct,False,offdct=offr,label='ofcor',minAIC=minAIC)
    else:
        print('warning: no running offset could be estimated',ID)
        off0=dict(list(zip(bbatns,[0.0 for _ in bbatns])))
        armsdc=999.9;frac=0.0
    armsd0,fra0,noff0,cdfs30=sg.visresults(dct,False,offdct=off0,label='nocor',minAIC=minAIC)
    usefirst=armsd0/(0.01+fra0)<armsdc/(0.01+frac)
    av0=average(cdfs30[cdfs30<20.0])#to avoid nan
    if offr!=None:
        avc=average(cdfs3c[cdfs3c<20.0])
        orusefirst=av0<avc
        if usefirst!=orusefirst:print() #'warning hard decission',usefirst,orusefirst
        ##print 'decide',orusefirst,ID,armsd0,fra0,av0,armsdc,frac,avc
    else:orusefirst=True
    if orusefirst: #was usefirst
        ##resids,cdfs3,pc1ws,pc2ws=sg.visresults(dct,True,dataset,offdct=noff0,label='nocornew',minAIC=minAIC)
        resids,cdfs3,pc1ws,pc2ws,pc3ws=sg.visresults(dct,True,dataset,offdct=noff0,label='nocornew',minAIC=minAIC)
    else:
        resids,cdfs3,pc1ws,pc2ws,pc3ws=sg.visresults(dct,True,dataset,offdct=noffc,label='ofcornew',minAIC=minAIC)
    sg.savedata(cdfs3,pc1ws,pc2ws,pc3ws)
    ##show()
    return sg

def getseccol(pc1,pc2):
    i=(clip(pc1,-12,12)+12)/24 #from 0 to 1
    j=(clip(pc2,-8,8)+8)/16
    return (i,1-j,1-i)

def getprobs(pc1,pc2):
    ##N=array(histdct_flattened).reshape((25, 35, 3))
    ##N=array(eval(open('histdct_flattened7.json','r').readline())).reshape((17, 23, 7))
    ##N=array(eval(open('histdct_flattened4w.json','r').readline())).reshape((17, 23, 4))
    datatup=(0.98171424500655113, 4.1628083587833546e-10, 0.00010422256433052112, 0.018181532012837631, 0.95389240995270841, 3.646053796928148e-09, 0.00042615881550044289, 0.045681427585737483, 0.89254837061258774, 2.9014518111819331e-08, 0.0015888819772150828, 0.10586271839567915, 0.77635281957751678, 2.0250708568752149e-07, 0.0052143379824462497, 0.21843263993295131, 0.60122798563175128, 1.1872859613607641e-06, 0.014426194017912381, 0.384344633064375, 0.29107478643044832, 0.28036442055259708, 0.023625558201352419, 0.40493523481560223, 0.38183714273601438, 1.967438188659186e-05, 0.053806768606641416, 0.56433641427545755, 0.14838035757740095, 9.2397785269914174e-05, 0.12053114209183108, 0.73099610254549807, 0.22401315416342565, 0.00035844259158211608, 0.22382779672950998, 0.55180060651548235, 0.31862854263990947, 0.00074277820688757731, 0.10506317687340512, 0.57556550227979797, 0.28271365887306293, 0.039999788627106111, 0.19975877307036255, 0.47752777942946856, 0.040502487821895694, 0.12034052448091581, 0.28045736310488079, 0.55869962459230782, 0.033758946445869575, 0.03343473071813681, 0.3673403843856155, 0.56546593845037818, 0.058396665742545067, 0.11567166629857463, 0.30808736321704056, 0.51784430474183973, 0.017148877122362634, 0.18682600139384378, 0.4749860185474733, 0.32103910293632021, 0.02198932793815481, 0.23955960397349951, 0.4567918610655905, 0.2816592070227551, 0.029750318067257552, 0.2062522041281192, 0.47086748524061534, 0.2931299925640079, 7.6945682912780432e-05, 0.40826300546368899, 0.22242149460536143, 0.36923855424803681, 5.7278109287640667e-05, 0.45530743937780765, 0.27285640824097357, 0.27177887427193109, 4.1377227366976436e-05, 0.48106005073308394, 0.27960612233402937, 0.23929244970551972, 5.0090476741020825e-06, 0.94491722472237427, 0.050488323056098891, 0.0045894431738526826, 8.2406349216419691e-06, 0.87443765242341298, 0.1173111568096175, 0.0082429501320480016, 1.8187462750890629e-06, 0.96347114652142685, 0.034624697994194695, 0.0019023367381034563, 0.98549745697150992, 3.7262350613752053e-10, 6.4770680953371481e-05, 0.014437771974913157, 0.96606861954397183, 3.0306778978481652e-09, 0.0002459354106826981, 0.03368544201466752, 0.91330426221250027, 2.6473569344551454e-08, 0.0010065182528138207, 0.085689193061116636, 0.67581239742386034, 3.3257840312741192e-07, 0.0059454656766025496, 0.31824180432113391, 0.49356252059720035, 2.385976523192557e-06, 0.020127761634219886, 0.48630733179205649, 0.63558899811550595, 1.283468396588345e-05, 0.051275131221273133, 0.31312303597925517, 0.58816311310028446, 3.3755154710401247e-05, 0.06409273366507684, 0.34771039807992837, 0.25389026903933459, 0.0001368378327409936, 0.12393009305707106, 0.62204280007085333, 0.35314791820196045, 0.00044956665939357423, 0.049905190384912, 0.59649732475373396, 0.33605905573592365, 0.0013088827108719029, 0.099729573967688306, 0.56290248758551609, 0.19562195118359352, 0.048435807015388917, 0.25801409361809269, 0.49792814818292486, 0.11731905659417331, 0.058096171212297425, 0.24661222565939797, 0.57797254653413133, 0.029807403932577945, 0.014760569105592015, 0.2358855004432901, 0.7195465265185399, 0.087997695613345223, 0.087152579283431494, 0.29378673515415105, 0.53106298994907231, 0.015105659271966922, 0.17952704213253695, 0.41839339706795814, 0.38697390152753808, 0.00068767049145058848, 0.33373988027489859, 0.38667336355520393, 0.27889908567844679, 0.00026398425848365948, 0.30193515683503724, 0.37011179780293318, 0.3276890611035459, 0.00012231581561533543, 0.41564484052440309, 0.39627545106990503, 0.18795739259007666, 7.2826655364269293e-05, 0.55613689159978186, 0.29625016048171032, 0.14754012126314367, 2.9295586517953867e-05, 0.7634703174869728, 0.21787242830362427, 0.018627958622884896, 4.531514727326354e-05, 0.6843464485762869, 0.28276488118461279, 0.032843355091827127, 6.87167549494299e-06, 0.93399558163627017, 0.060560238760721585, 0.0054373079275133228, 1.7381505674518064e-06, 0.9780745722079992, 0.020485547007703574, 0.0014381426337297274, 0.98861562202809428, 3.3285054570226594e-10, 4.1045153320071541e-05, 0.011343332485735168, 0.97102078618804288, 2.9469494424403537e-09, 0.00016965175706919072, 0.02880955910793857, 0.80436429683308652, 2.076141096184759e-08, 0.00055997728997730792, 0.19507570511552536, 0.6590303811944257, 3.9911234319034631e-07, 0.0050616415411362239, 0.33590757815209488, 0.24530713036900889, 2.9186767217273318e-06, 0.017467055605380158, 0.73722289534888918, 0.5021571371308452, 6.2393634747107083e-06, 0.017683420787632392, 0.48015320271804768, 0.73786131270140665, 4.7374671085983032e-05, 0.063814488753991511, 0.19827682387351589, 0.50817320994218429, 0.00018072860644977287, 0.11611862444677726, 0.37552743700458868, 0.47391616525258728, 0.00064963416224728208, 0.029300069220435918, 0.4961341313647295, 0.3030730720911668, 0.016675689163092654, 0.016655664050508393, 0.66359557469523223, 0.22632786170909813, 0.059774464999089678, 0.074628355542508698, 0.6392693177493034, 0.075959835974993714, 0.041794627442766345, 0.19202441519360633, 0.69022112138863367, 0.065343166342474279, 0.072805073204473325, 0.18583398101907042, 0.676017779433982, 0.028926769225487876, 0.12032563613419481, 0.35482051533617204, 0.49592707930414515, 0.023269911451763849, 0.19013305411929943, 0.33377195246124503, 0.45282508196769167, 0.012414784415440295, 0.28279775892737719, 0.36228329134261417, 0.34250416531456829, 0.0088705969463435709, 0.4216994447060935, 0.33344449325733438, 0.23598546509022864, 0.00022112366390570243, 0.46956006134853834, 0.40728616240878146, 0.12293265257877445, 0.0001509280492664293, 0.61157250970975496, 0.27765368126424139, 0.11062288097673717, 4.9932199362522329e-05, 0.87432158982867303, 0.10076211402858964, 0.024866363943374908, 1.9277153607589737e-05, 0.84259863614560138, 0.052599174746996477, 0.10478291195379461, 7.3618710388992567e-06, 0.90503552828739697, 0.090394871033525948, 0.004562238808038215, 3.1750258593840896e-06, 0.97430092538081048, 0.023638444542548813, 0.0020574550507812804, 0.99115501923568483, 2.9673180819272127e-10, 2.6524830753532964e-05, 0.0088184556368299423, 0.97740353404159841, 2.6376597821785481e-09, 0.00011007288861345238, 0.022486390432128352, 0.50313691071123134, 5.7388221245742739e-08, 0.0011220500325960989, 0.49574098186795135, 0.7539498584355403, 3.3109695735474726e-07, 0.0030438785889176541, 0.24300593187858471, 0.65757961017472766, 4.2550868278164541e-06, 0.018459419712759068, 0.3239567150256854, 0.65599646650862187, 1.0132307352418529e-05, 0.020816622174526955, 0.32317677900949865, 0.71022359228434306, 4.7443385110399929e-05, 0.046325985252491625, 0.24340297907805494, 0.46685786408587193, 0.00022812438707111655, 0.072918787548077138, 0.45999522397897968, 0.34698489142254252, 0.015620568268644264, 0.062407240820101587, 0.57498729948871152, 0.22258724972453858, 0.045926990838337518, 0.11009241385196376, 0.62139334558516013, 0.12813482760060815, 0.025380848086065708, 0.15210221595187118, 0.69438210836145497, 0.093585706126665238, 0.054769545647532655, 0.20198317023966955, 0.64966157798613255, 0.041060292019339202, 0.094887229014798929, 0.24708748795906288, 0.61696499100679891, 0.042305117393859441, 0.15562420920503162, 0.29293957749701799, 0.509131095904091, 0.016699063280945239, 0.29769638483529026, 0.28742759767394788, 0.39817695420981652, 0.003831980073596964, 0.32259015775537581, 0.38285270699338841, 0.29072515517763881, 0.00073118363271205869, 0.44409738656751269, 0.38180200088033267, 0.17336942891944265, 0.00033448830629823002, 0.44313670293339175, 0.41971121999481908, 0.13681758876549091, 0.00018717810636113052, 0.69049875843108899, 0.22519822641316806, 0.084115837049381886, 9.0823002325693601e-05, 0.9500644472751224, 0.024971672527505408, 0.024873057195046625, 3.0894585515255684e-05, 0.82795728688492765, 0.10337037860665128, 0.068641439922905848, 1.5197528048166157e-05, 0.91640632768978458, 0.076275487919776994, 0.0073029868623902027, 5.527768943495125e-06, 0.97068925507786152, 0.026527610603952936, 0.0027776065492421107, 0.99319839115808439, 2.6402976516824606e-10, 1.7481908100030506e-05, 0.0067841266697858645, 0.92619639912232798, 9.9711766791545676e-09, 0.00030821617238478152, 0.073495374734110497, 0.71664515555292285, 6.2869127125359066e-08, 0.00091048818471942908, 0.28244429339323057, 0.71114520104289658, 4.5036948564555998e-07, 0.003066821636836439, 0.28578752695078141, 0.69865765363711574, 2.1732075373992277e-06, 0.043194807676679207, 0.25814536547866762, 0.5463136727476321, 1.5143364863930654e-05, 0.023044734871145289, 0.43062644901635866, 0.65835647774352091, 0.014818948259585133, 0.031970538564797112, 0.29485403543209676, 0.4878739962203138, 0.00017418669874311391, 0.060091536033630523, 0.45186028104731257, 0.36601405982054924, 0.0007461970222364697, 0.032183431809738414, 0.60105631134747584, 0.25755493307909422, 0.004812856889198875, 0.067299082730519447, 0.67033312730118744, 0.17430407518337507, 0.033775451542685082, 0.10495299753980315, 0.68696747573413675, 0.089968394369863897, 0.045825095186892796, 0.13731019744683903, 0.72689631299640423, 0.064413532367412513, 0.11562828291696042, 0.21305808623541247, 0.60690009848021453, 0.024445718603063642, 0.16745904097173253, 0.30428855357157364, 0.50380668685363017, 0.026738569066251376, 0.29350635025395172, 0.34384967689050006, 0.33590540378929679, 0.0070557039766344035, 0.38200750043826798, 0.3745692136184639, 0.23636758196663371, 0.010108941577264901, 0.50393012850188179, 0.30999485562908485, 0.17596607429176842, 0.00048887540066157081, 0.60850851542556628, 0.27813559602895321, 0.11286701314481906, 0.0002417391622133475, 0.81524510234744674, 0.14270643161922472, 0.041806726871115175, 0.0087810276316259168, 0.87836629531763943, 0.095548777586239891, 0.017303899464494888, 2.6691353580702212e-05, 0.9497114761110681, 0.041242217771692555, 0.0090196147636587305, 1.4779086063830962e-05, 0.96027841730304209, 0.03425447359139551, 0.0054523300194984836, 7.6349645744529816e-06, 0.97294813736526031, 0.02409889155092142, 0.0029453361192437705, 0.96344661025841127, 1.6558133064113064e-09, 8.2978628482687826e-05, 0.036470409457292713, 0.89603129983971563, 1.6394403368367889e-08, 0.00038355139621603263, 0.10358513236966488, 0.72485288182265317, 4.1566063380185782e-08, 0.00045561154432947947, 0.27469146506695397, 0.86362506733354272, 3.9138250800641389e-07, 0.0020171579833437579, 0.13435738330060559, 0.86540807821318988, 2.2181600622251401e-06, 0.0053947194588636459, 0.12919498416788422, 0.76837740209334593, 9.8721690196149303e-06, 0.011370533769103273, 0.22024219196853101, 0.66380835220524992, 4.6289706078462378e-05, 0.0091200521642899463, 0.32702530592438173, 0.53731208251118601, 0.00018737592434185611, 0.0061093423204007062, 0.4563911992440714, 0.38459935320654154, 0.0081915208643078968, 0.020454210054569551, 0.58675491587458095, 0.27558623354819323, 0.014215601341724666, 0.062473533944858529, 0.6477246311652235, 0.18143189927369449, 0.025367923090871949, 0.082346744516350628, 0.71085343311908289, 0.069749652789795405, 0.052632219318577596, 0.14292201107242833, 0.73469611681919866, 0.045356131602030343, 0.087118619718450002, 0.20801785030687364, 0.65950739837264616, 0.026935299794109729, 0.15205671871817622, 0.23846901359961187, 0.58253896788810222, 0.018159439368536406, 0.26977558360102477, 0.31517674548960961, 0.39688823154082925, 0.0079789612765996595, 0.41092129312471237, 0.3295261948874012, 0.25157355071128673, 0.0052377369736108783, 0.55505549723099323, 0.26424146459660847, 0.17546530119878737, 0.00065352477488155643, 0.74811912951223902, 0.19039759384719088, 0.060829751865688529, 0.00022595184429379233, 0.88121666728629444, 0.077781444628249694, 0.040775936241162124, 8.9748311324807306e-05, 0.93457924808965387, 0.047564685470801997, 0.017766318128219216, 3.4737294976996425e-05, 0.98133252502980184, 0.0093348008125724458, 0.009297936862648612, 1.1315129332434811e-05, 0.97267629160287972, 0.013683214743504871, 0.013629178524282897, 4.3544987058722367e-06, 0.9475225334738091, 0.026288463742167752, 0.026184648285317236, 0.99609985498477416, 2.0791672936075976e-10, 8.0581393768450565e-06, 0.00389208666793234, 0.91018376452106686, 7.5048897188050658e-09, 0.00013578841612919658, 0.089680439557914077, 0.88579433791542117, 4.3127966524089099e-08, 0.00036559922126690631, 0.11384001973534545, 0.9266604317684779, 3.1541935239931037e-07, 0.0012572374041237696, 0.072082015408045819, 0.87696122237386132, 1.198132525619937e-06, 0.0022535712711035721, 0.12078400822250937, 0.75131621309025842, 7.057754460728566e-06, 0.0062867366946944307, 0.2423899924605864, 0.71578579112627039, 3.8838640528003524e-05, 0.010187916452039442, 0.27398745378116224, 0.54780005696461742, 0.0035229809707695214, 0.014075001502268059, 0.43460196056234507, 0.35783127110748447, 0.0052894733527369467, 0.036981850173606147, 0.59989740536617242, 0.24064348225596952, 0.0073901512953871125, 0.053514256676026849, 0.69845210977261651, 0.17051544416254008, 0.0082379434181076815, 0.082280508287941631, 0.73896610413141062, 0.079284843655520798, 0.036162094046522916, 0.14447467421851914, 0.74007838807943715, 0.046013447335647349, 0.056964426583459356, 0.18819452925272928, 0.7088275968281641, 0.02398574229511799, 0.13929295055529564, 0.24481805650228558, 0.59190325064730076, 0.011370955571939418, 0.28295148543521759, 0.31354432527429887, 0.39213323371854408, 0.013415252517038366, 0.47498931822659446, 0.26540918832720856, 0.24618624092915878, 0.0041422515435999892, 0.60716555956714624, 0.24380383935726369, 0.14488834953198995, 0.00073722684536596408, 0.79882766987247777, 0.14332965131778855, 0.057105451964367594, 0.00026049972731033216, 0.90248659190885705, 0.066770580360294471, 0.030482328003538107, 9.6890265687975664e-05, 0.92810379670987253, 0.049187186130441159, 0.022612126893998292, 3.2336370135497518e-05, 0.97439688903123411, 0.015366738600415257, 0.010204035998215181, 1.3241398784780716e-05, 0.98282860181082843, 0.014363746919463316, 0.0027944098709234083, 4.8837626417169846e-06, 0.99183266504353318, 0.0070847358401223753, 0.0010777153537027137, 0.89032227394682772, 7.6296825753799897e-10, 2.3367582331258662e-05, 0.10965435770787285, 0.95297697967570894, 5.2165288316014195e-09, 7.4586802813858584e-05, 0.046948428304948525, 0.98368295830186003, 2.4376524312505359e-08, 0.00016329768739814751, 0.016153719634217561, 0.89450090510575797, 1.8288023832330686e-07, 0.00057604671996770013, 0.10492286529403586, 0.83723917977935458, 1.1034710861042749e-06, 0.0016401719069858555, 0.16111954484257343, 0.79259410988948797, 6.3112265427603516e-06, 0.0044425719198285469, 0.20295700696414076, 0.71308602427884316, 3.2756323063782699e-05, 0.0097071958570430095, 0.27717402354105014, 0.55598437720837446, 0.0047469378343950779, 0.018964949769708771, 0.42030373518752173, 0.42185055496760043, 0.0058297558205705879, 0.019409183731333084, 0.55291050548049581, 0.29046842015135399, 0.0083385161198207131, 0.054135267921197883, 0.64705779580762746, 0.17922116873504443, 0.016228567424395338, 0.082058463657228325, 0.72249180018333192, 0.072848596272900523, 0.028422321342728138, 0.10627373770370027, 0.79245534468067103, 0.047800046641680215, 0.058100296517926163, 0.17122587416082433, 0.72287378267956925, 0.04764727520633448, 0.14156903431786422, 0.24057473887942321, 0.57020895159637797, 0.021809273087225703, 0.30527745859954147, 0.26176310033519201, 0.41115016797804083, 0.014142965830056796, 0.48499718656514557, 0.23783541273026879, 0.26302443487452898, 0.0055826285561647593, 0.72430081440482486, 0.14910410602572627, 0.12101245101328414, 0.00080875585764526403, 0.85621011789706314, 0.10995196271975155, 0.033029163525540001, 0.0002476415682618976, 0.92936000965573751, 0.054602587146345118, 0.015789761629655622, 8.7286522016837462e-05, 0.95002521857247546, 0.036320932993324707, 0.013566561912182865, 2.4153483493045222e-05, 0.9617750142657544, 0.033124829666322041, 0.0050760025844305192, 9.8623396401931432e-06, 0.97971141409213858, 0.018727941073767046, 0.0015507824944542394, 5.4380752163027088e-06, 0.99358787574799567, 0.0055125381436227378, 0.0008941480331651709, 0.99246979847201389, 5.7035450668480748e-10, 1.410540876097723e-05, 0.0075160955488706195, 0.92598653230150141, 3.2154261480093029e-09, 3.712379839706211e-05, 0.073976340684675318, 0.92052907825422248, 2.0078062658796242e-08, 0.00010860843209624405, 0.079362293235618608, 0.92664157578373652, 1.245065498124029e-07, 0.00031667706758602273, 0.073041622642127629, 0.90084468775218474, 8.218980823292965e-07, 0.00098646087565103604, 0.098168029474081875, 0.86760042638652601, 4.361807041073851e-06, 0.0024792517815296145, 0.12991596002490324, 0.73603209010310644, 2.7373212976354709e-05, 0.0046081517129579093, 0.25933238497095928, 0.61759723762953822, 0.0018043242736839661, 0.012615102771895861, 0.36798333532488209, 0.44917525718112122, 0.0073409479722501073, 0.032261383201969231, 0.51122241164465954, 0.35176908692646597, 0.014299620366052136, 0.057129794286139485, 0.57680149842134243, 0.22141842838567435, 0.0070739341892086137, 0.099925500200884795, 0.67158213722423221, 0.11015036853007881, 0.023323224423930599, 0.13225671345397091, 0.73426969359201966, 0.083951680593777181, 0.063225164318563412, 0.16695620975245215, 0.68586694533520731, 0.036498959483766705, 0.17024744024152533, 0.23293561296862514, 0.56031798730608284, 0.022755965754081717, 0.31032295014243855, 0.29782933543171441, 0.36909174867176536, 0.016696253455163027, 0.50710109297655781, 0.24223536998717171, 0.23396728358110747, 0.0035261275009554754, 0.77702854307492708, 0.14301084570680669, 0.076434483717310597, 0.0015515127408644443, 0.87433237093673033, 0.073668816006405791, 0.050447300315999297, 0.00025285444011177846, 0.94566734741069525, 0.041949117235661998, 0.012130680913530987, 7.3545652776642339e-05, 0.97548344991021685, 0.0187090937124346, 0.0057339107245719069, 2.3345291081770908e-05, 0.98701978383062128, 0.0092653619787429753, 0.003691508899553976, 9.3417096198527734e-06, 0.98555955604198575, 0.013347471732527439, 0.0010836305158670259, 5.4658313761702796e-06, 0.99538092980436887, 0.0039506183414070029, 0.00066298602284802725, 0.94198627310609251, 2.456682498440032e-10, 5.0129668546428111e-06, 0.058008713681384536, 0.93985224511756271, 1.6266842944477656e-09, 1.5496090446806676e-05, 0.060132257165306062, 0.96686745368717353, 1.2152833625113411e-08, 5.4240576130831453e-05, 0.033078293583862106, 0.94254190129693272, 8.6805113120526318e-08, 0.00018216910561498113, 0.057275842792339292, 0.89715873970996285, 5.4672129867043289e-07, 0.00054141825370502856, 0.1022992953150334, 0.84096789244048076, 0.0022510577464523469, 0.0044967090974789327, 0.15228434071558794, 0.80355086091415495, 2.5052527386624796e-05, 0.0020329360610959364, 0.1943911504973625, 0.66031903833426109, 0.00012504069447605775, 0.0083957853819485104, 0.33116013558931451, 0.51452023792286772, 0.0015535940997518771, 0.038793211397807587, 0.4451329565795728, 0.37659781753886801, 0.0083503215680626464, 0.077842744267848166, 0.53720911662522131, 0.2858186282444567, 0.012808763353529606, 0.13049249501894208, 0.57088011338307154, 0.17264442709076513, 0.03442678722985399, 0.15702686820679507, 0.63590191747258584, 0.083811107180247715, 0.054891195584878774, 0.22197552036563134, 0.6393221768692422, 0.047323300182646487, 0.1673886231733912, 0.23907828720277097, 0.54620978944119125, 0.017445161384909535, 0.34339271218700246, 0.26101020099164002, 0.37815192543644793, 0.011084957346061394, 0.56209915500389029, 0.21711324724167724, 0.20970264040837111, 0.0036602966949757791, 0.79209391345370228, 0.12129648143466061, 0.082949308416661385, 0.0010987786885863252, 0.89437307088330609, 0.074315201687096086, 0.030212948741011405, 0.00027403652805922527, 0.96735601126533011, 0.021193940697899854, 0.011176011508710618, 7.0720345353050276e-05, 0.97170925699868016, 0.024704714960662611, 0.0035153076953041511, 2.1603948765290998e-05, 0.9866396299604786, 0.011662187185543441, 0.0016765789052128335, 9.239648469010017e-06, 0.99439056074626186, 0.0028056396616024269, 0.0027945599436666854, 6.7884827529058064e-06, 0.98910103365958912, 0.010290763177963312, 0.00060141467969469439, 0.97902686077924395, 1.6284801227457002e-10, 2.8015913073583304e-06, 0.020970337466600573, 0.95991552775885614, 9.9397777863774784e-10, 7.9831090629300649e-06, 0.040076488138103127, 0.95261171817070545, 7.2514320064407445e-09, 2.7286450102528087e-05, 0.047360988127759997, 0.95918834397396291, 5.6569492194092425e-08, 0.00010008943025024331, 0.040711510026294716, 0.91843697160246207, 4.5627639323277868e-07, 0.00038095301814583462, 0.081181619102998884, 0.86734688130339455, 3.0251641325053718e-06, 0.0019024067826739295, 0.13074768674979895, 0.81792798019422319, 0.0019060534722671807, 0.00571129372571601, 0.17445467260779357, 0.71178920377998001, 0.0036431694562179054, 0.012735780861547816, 0.27183184590225434, 0.58207872971869512, 0.0068834451958608833, 0.039532280197451412, 0.37150554488799259, 0.42890529790865956, 0.0016723864465202458, 0.1035634453061086, 0.46585887033871148, 0.29183562791917977, 0.010510286670857743, 0.14521770363468256, 0.55243638177527976, 0.15562583343028469, 0.035713333055152473, 0.21026789492735018, 0.59839293858721265, 0.11649625608712379, 0.066235199314402818, 0.26035453421537286, 0.55691401038310062, 0.046241159112510317, 0.17046685727938343, 0.29224100547615184, 0.49105097813195442, 0.021522512596748141, 0.38368464654750645, 0.25852405701423647, 0.33626878384150899, 0.0085421194342522599, 0.64860630456381008, 0.14646533004565068, 0.1963862459562869, 0.0056798592033878645, 0.84749689508219961, 0.1039091200121149, 0.042914125702297544, 0.0013658372985012404, 0.91004085220006969, 0.056130256435679038, 0.032463054065750056, 0.00030801033909668818, 0.95937075409828654, 0.026916255262014993, 0.013404980300601705, 7.0558089566360253e-05, 0.98754727710295531, 0.0078908909949341709, 0.0044912738125442147, 1.9963658857414541e-05, 0.98963997675542537, 0.007762708594137975, 0.0025773509915792323, 8.9840919114980021e-06, 0.98896023644392184, 0.01048034628059508, 0.00055043318357159967, 5.6087694364545662e-06, 0.99744540232365775, 0.0021896607172448481, 0.00035932818966092337, 0.99926911843902522, 9.9935580759966773e-11, 1.4811208430241913e-06, 0.00072940034019616773, 0.98702856322178278, 6.5155008415478556e-10, 4.5080759677391826e-06, 0.012966928050699452, 0.94911600309529764, 5.3403463735791694e-09, 1.7311739939404146e-05, 0.050866679824416561, 0.94605387957674525, 4.2470287273491769e-08, 6.4735002495542004e-05, 0.053881342950471985, 0.92540961562142621, 3.7256008804575312e-07, 0.0024153601908792847, 0.072174651627606556, 0.9000008514539154, 2.8118949916971745e-06, 0.0043641519082659817, 0.095632184742827045, 0.83008729101173206, 1.9277424809515661e-05, 0.0063163693675808283, 0.16357706219587756, 0.70811848326090454, 0.0022054019569000029, 0.01541927509672621, 0.27425683968546938, 0.57174498179275679, 0.0022293465785535732, 0.048986727962513237, 0.37703894366617635, 0.44792225225180476, 0.0079217942117071772, 0.092309948176569318, 0.45184600535991865, 0.28186763201886267, 0.014564901842467096, 0.20366376076086659, 0.49990370537780365, 0.18754950587249999, 0.029612049304432054, 0.2070354263422651, 0.57580301848080284, 0.1159206141341985, 0.11480733039085032, 0.22933892648441434, 0.53993312899053669, 0.0832849874678976, 0.2710225741463938, 0.2353887955479029, 0.41030364283780557, 0.020980341150813629, 0.44466737250124, 0.25734831985665119, 0.27700396649129522, 0.013657103177115151, 0.68982306542918514, 0.12158729767038928, 0.17493253372331058, 0.0032690657210290301, 0.83855656025161329, 0.087312117754121676, 0.070862256273235863, 0.0016787416122339652, 0.93324483772425482, 0.033807611456180116, 0.031268809207331119, 0.00030883420737675137, 0.95436346676069805, 0.029284713149755798, 0.016042985882169347, 7.1127755812246582e-05, 0.97776289059535992, 0.01479679905310592, 0.0073691825957218236, 2.3476991431103495e-05, 0.98183577231516184, 0.013207498023940828, 0.0049332526694663113, 1.1388706203271232e-05, 0.98867710853496049, 0.010811932653647778, 0.00049957010518844754, 7.1848479205166355e-06, 0.97733618563902758, 0.011350727266978508, 0.011305902246073357, 0.98812611848722531, 5.351850778725582e-11, 6.9822259360719382e-07, 0.011873183236662484, 0.97932002684583808, 4.9611464692836384e-10, 3.0216559879428645e-06, 0.020676951002059397, 0.96381051018927399, 4.4207555365686012e-09, 1.2615002528254258e-05, 0.036176870387442321, 0.95469576853720828, 3.6500056810887266e-08, 4.8974167248287128e-05, 0.045255220795486731, 0.95473822651428286, 3.1240320431497031e-07, 0.00019780008839449009, 0.045063660994118314, 0.88665724355803233, 2.3196517326546309e-06, 0.00069554634693992699, 0.11264489044329506, 0.867756532504117, 0.0029533427225888671, 0.0029497961812770608, 0.12634032859201721, 0.77201134405273109, 0.0029750858594596325, 0.017829079246541129, 0.20718449084126808, 0.64847530185387903, 0.0067251041342941791, 0.060453254233148561, 0.28434633977867829, 0.48909245696507697, 0.0071762264926961399, 0.10393032866191916, 0.3998009878803076, 0.29754776130980659, 0.024557513199080262, 0.20323219177715224, 0.47466253371396105, 0.25251994527321325, 0.04246892534205788, 0.2120896312486357, 0.49292149813609304, 0.13791928152257779, 0.10813749138674518, 0.22169987982062964, 0.53224334727004741, 0.047527186652862895, 0.28914884902462989, 0.26193635547228034, 0.40138760885022695, 0.032619392265867998, 0.4652081372326396, 0.20005741884803974, 0.3021150516534527, 0.0067824346276525839, 0.73890268858891928, 0.093929229210179765, 0.16038564757324833, 0.00864763253531085, 0.83766929730179485, 0.076993562258058978, 0.076689507904835294, 0.0020555861048107589, 0.95451621967379974, 0.025374866454460403, 0.018053327766929101, 0.0022290183780343375, 0.96914132930011243, 0.01984464183421935, 0.0087850104876337314, 8.259181493928097e-05, 0.97536397341568903, 0.019308323805209391, 0.0052451109641622291, 2.7048053242150058e-05, 0.99220717292719263, 0.0069954047599342529, 0.00077037425963101677, 1.2197068569038236e-05, 0.99014484962972427, 0.0094636921299640318, 0.00037926117174272251, 9.8917647118310226e-06, 0.99740725658229223, 0.00226122652291288, 0.00032162513008320199, 0.9884058422255817, 3.3084914752477579e-11, 3.8824957295468822e-07, 0.011593769491760483, 0.95959255912099684, 3.6826037558526321e-10, 2.0174790160637764e-06, 0.040405423031726659, 0.94265750681674887, 3.548391948063723e-09, 9.1078001434514851e-06, 0.057333381834715744, 0.94699549400395011, 2.912745197446888e-08, 3.5153379217367056e-05, 0.052969323489380556, 0.93464019839217505, 2.8614237974905113e-07, 0.0001629612138513812, 0.065196554251593916, 0.8891839795466504, 2.6910343500795301e-06, 0.00072579436876456, 0.11008753505023493, 0.86862562390616538, 2.0270033538779847e-05, 0.014646313634700803, 0.11670779242559501, 0.70093669802520875, 0.00012337478570047391, 0.039340219523489275, 0.25959970766560136, 0.58482263491306885, 0.0007769813613048884, 0.060261515084276095, 0.35413886864135019, 0.47850753916805416, 0.022042419831719173, 0.1431036752912459, 0.35634636570898076, 0.34618552307130851, 0.014589821726365927, 0.1457230144160904, 0.49350164078623515, 0.2206986294215991, 0.075661987063811248, 0.27709413549349632, 0.42654524802109328, 0.11353164757632404, 0.10221937009113342, 0.30628985783579232, 0.47795912449675027, 0.12029821452293575, 0.30977151134530501, 0.2498996124363162, 0.32003066169544298, 0.040834452825724739, 0.5763025615821894, 0.16157487854211358, 0.2212881070499722, 0.0093552186984460356, 0.73196443677457301, 0.14806793972604193, 0.11061240480093912, 0.01092607755172314, 0.91732006665025478, 0.044912671408248409, 0.026841184389773693, 0.0025338594137043887, 0.92327133322873534, 0.055701097652329931, 0.018493709705230309, 0.00053918136214247824, 0.96478689853516186, 0.021703340715122255, 0.012970579387573296, 0.0001161910068314554, 0.98963660788736418, 0.0068404719457741767, 0.0034067291600301509, 3.9424250166732796e-05, 0.98975757272925902, 0.0094149430070935795, 0.00078806001348070162, 2.0816934078249514e-05, 0.99671829933252754, 0.0028065972835658176, 0.00045428644982840253, 1.7723850370418961e-05, 0.95203332320405742, 0.047544503381817295, 0.00040444956375495459, 0.97759894900611422, 3.5770683049595084e-11, 3.8580760140237603e-07, 0.022400665150513775, 0.96713919333188114, 2.7930883482875037e-10, 1.406375486162433e-06, 0.032859400013324054, 0.95110015690650096, 2.8221626684041637e-09, 6.6577353854220161e-06, 0.048893182535950937, 0.95709701479483922, 3.4293696628004989e-08, 3.8040083897082744e-05, 0.042864910827567049, 0.9444110394527292, 2.421537707741248e-07, 0.00012675230991649711, 0.055461966083583475, 0.93872937420186975, 2.4888717418876586e-06, 0.00061696346918096252, 0.060651173457207323, 0.82724223483711767, 1.6111877485504934e-05, 0.013869723199758899, 0.15887193008563799, 0.78562309378934247, 0.0082774264943349194, 0.0578724054405413, 0.14822707427578122, 0.62605718973424895, 0.0087330229972557051, 0.078502822994939561, 0.2867069642735558, 0.36683491278368519, 0.011353496460005, 0.14741821299446201, 0.47439337776184792, 0.37822233168180286, 0.013873701577747215, 0.15242745375713271, 0.45547651298331715, 0.13386161543123365, 0.088384019381143514, 0.26483364852543279, 0.51292071666219008, 0.071022370853019878, 0.14068056586078109, 0.2634593037463297, 0.52483775953986933, 0.079771747773868737, 0.44769858236134696, 0.23673227322275633, 0.23579739664202787, 0.021493932622818547, 0.65991275422562423, 0.23388139450041148, 0.084711918651145787, 0.031085064104914788, 0.70809014243136081, 0.12299823089734961, 0.13782656256637471, 0.013677963463088104, 0.88088210201486383, 0.07038594310926452, 0.035053991412783543, 0.0034274699706521002, 0.91812574398213109, 0.039300994566734776, 0.039145791480482126, 0.00069503059453137987, 0.98182795887391505, 0.0087557939662427052, 0.008721216565310887, 0.00017154110568130164, 0.98890258281673238, 0.0088355100657512425, 0.0020903660118350622, 4.8123711762959396e-05, 0.98129957405147294, 0.017983874750663851, 0.00066842748610031687, 2.008277441679425e-05, 0.99749626636351396, 0.0021791166709090185, 0.00030453419116044232, 1.1874080664476765e-05, 0.99807681861739506, 0.001723026679848867, 0.00018828062209155991, 0.9999258425603933, 2.5101198009085234e-11, 2.5425651632880635e-07, 7.3903157989160817e-05, 0.99983511423393323, 1.9414076717641317e-10, 9.1805236111416207e-07, 0.00016396751956478635, 0.99937524561214663, 2.5174497060608774e-09, 5.5774975200346181e-06, 0.0006191743728836698, 0.98381084960802789, 3.1964268531968693e-08, 3.3298604307989681e-05, 0.01615581982339544, 0.95294098346901601, 2.2810590851441687e-07, 0.00011213347390698225, 0.046946654951168516, 0.92521574736251699, 2.4265458887056538e-06, 0.015003766172744442, 0.059778059918849782, 0.82264112022219205, 1.5585043213535249e-05, 0.0017244322286822068, 0.17561886250591227, 0.75726290665582463, 0.018749756755196995, 0.037454481969415004, 0.18653285461956337, 0.63927968140422253, 0.00064475521877950764, 0.036135990122346993, 0.32393957325465089, 0.4080168086045165, 0.023770486938206374, 0.16619359393266381, 0.40201911052461331, 0.33628840312191471, 0.078366762597057063, 0.1565453106947286, 0.42879952358629958, 0.20212401620990605, 0.066727616085240388, 0.2332662002380064, 0.49788216746684716, 0.042179660992311116, 0.25064744410578632, 0.16689763496688262, 0.54027525993501979, 0.056137583309896488, 0.58378368926591784, 0.13882920207807581, 0.22124952534610989, 0.14325927871884275, 0.45414136663017979, 0.25199778218901847, 0.15060157246195896, 0.037747540991270659, 0.73822491720967887, 0.12823276780743306, 0.095794773991617427, 0.0090604173192782318, 0.88718485700099936, 0.083228676578426683, 0.020526049101295709, 0.0033311548145993439, 0.92401763764481526, 0.053764174047842839, 0.018887033492742619, 0.00081481370021199955, 0.94481382032496419, 0.036295355167132705, 0.018076010807691133, 0.0002128021026853037, 0.98900203365445938, 0.0090011487861839275, 0.001784015456671278, 0.00010004145239561525, 0.99263220024186305, 0.0063117894609174907, 0.00095596884482391912, 3.9366074510521297e-05, 0.99604213290360022, 0.0035078215194222803, 0.00041067950246696165, 1.9178020609117296e-05, 0.99748625533231883, 0.0022853587961671985, 0.00020920785090494553, 0.9452161781443178, 1.8915437532002397e-11, 1.838652451928459e-07, 0.054783637971521651, 0.99986141278377538, 2.0892028333747018e-10, 9.4806241075703526e-07, 0.00013763894489364676, 0.92782366809885453, 1.8015017305898783e-09, 3.8301772978994468e-06, 0.072172499922345604, 0.9775803724094605, 1.9374666987587546e-08, 1.9368728787991562e-05, 0.022400239487084313, 0.88377844861171517, 2.4662010838925387e-07, 0.00011634101210852015, 0.11610496375606798, 0.85517079037186339, 1.7088579277848872e-06, 0.00038177070289194492, 0.14444573006731684, 0.91869142837956674, 1.3427198517686595e-05, 0.0014257032555129478, 0.07986944116640253, 0.72781640776597134, 7.5361708195218925e-05, 0.024826240054004911, 0.24728199047182864, 0.43666907963531704, 0.033267336690583266, 0.13290954954949419, 0.39715403412460559, 0.39521176063898639, 0.0024232858280851264, 0.14216224470188113, 0.46020270883104741, 0.1872572480333313, 0.037091771646681877, 0.18523614872620103, 0.59041483159378583, 0.14436963876301237, 0.14298313496411216, 0.3570285817814271, 0.35561864449144853, 0.3361516734938923, 0.3324516026292777, 0.16602618795214577, 0.16537053592468423, 0.19038048481013789, 0.4924283011611349, 0.19471754955626855, 0.12247366447245872, 0.0663570315089788, 0.7002874517118427, 0.14046427264015751, 0.092891244139020945, 0.042413992455141693, 0.79240349293434509, 0.07195017544666292, 0.093232339163850264, 0.010035685554048129, 0.86730220862569385, 0.077249486702872808, 0.045412619117385269, 0.0049111190292477095, 0.8627753784084482, 0.066287639141479518, 0.066025863420824657, 0.0015340522490435227, 0.95658838084597686, 0.034516585640502223, 0.0073609812644773818, 0.00030308660180648842, 0.98722351430948119, 0.010742677392133521, 0.0017307216965787623, 9.4069079581714438e-05, 0.99432037013148222, 0.0049732830819640434, 0.00061227770697199347, 8.351191213296182e-05, 0.99308732738348071, 0.0062357339171511773, 0.000593426787235127, 2.2405072450076699e-05, 0.99757383432171121, 0.0022372820301678384, 0.00016647857567079067)
    N=array(datatup).reshape((17, 23, 4))
    ##dx, dy = 1,1
    dx, dy = 1.5,1.5
    xmax, ymax = 18,14
    xmin, ymin = -18,-12
    x = arange(xmin, xmax, dx)[:-1]+dx/2.0
    y = arange(ymin, ymax, dy)[:-1]+dy/2.0
    print(len(x),len(y))
    ##interp_splines = [RectBivariateSpline(y, x, N[:,:,n]) for n in range(3)]
    interp_splines = [RectBivariateSpline(y, x, N[:,:,n]) for n in range(4)]
    ##print('probabilies for reference below')
    ##print [ip.ev(0.0,0.0) for ip in interp_splines]
    ##print [ip.ev(1.188,1.475) for ip in interp_splines]
    ##print [ip.ev(-1.188,1.475) for ip in interp_splines]
    ind1=18+clip(pc1,-18,16.999)
    ind2=12+clip(pc2,-12,12.999)
    ##pr0=[array([dct[ss][0][int(ind2[i]),int(ind1[i])] for ss in secs]) for i in range(len(ind1))]
    ##nprobs=[prob/sum(prob) for prob in pr0]
    #was nprobs=[N[int(ind2[i]),int(ind1[i])] for i in range(len(ind1))]
    nprobs=[[ip.ev(pc2[i],pc1[i]) for ip in interp_splines] for i in range(len(ind1))]
    return nprobs

def viscolentry(ID,pref='',delta=0,doreturn=False,pdbID='',returnpcs=False):
    ##zbuf=initfil2('%szscores%s.txt'%(pref,ID))
    zbuf=initfil2('%scomponents%s.txt'%(pref,ID))
    ##zbuf=initfil2('CheZOD%s/zscoresmod%s.txt'%(pref,ID))
    resi=[eval(zlin[1])+delta for zlin in zbuf]
    zsco=[eval(zlin[2]) for zlin in zbuf]
    pc1s=[eval(zlin[3]) for zlin in zbuf]
    pc2s=[eval(zlin[4]) for zlin in zbuf]
    if returnpcs: return resi,pc1s,pc2s,zsco##,C
    rgbs=getseccol(array(pc1s),array(pc2s))
    C=array(rgbs).transpose()
    if doreturn:
        return resi,C,zsco
        C3=zeros((len(C),1,3))
        C3[:,0,:]=C
        imshow(rot90(C3),interpolation='none');show();1/0
    for i,ri in enumerate(resi):
        zi=zsco[i]
        coli=C[i]
        ##bari=bar(ri+0.5,zi,width=1.0,fc=coli,ec='none')
        bari=bar(ri-0.5,zi,width=1.0,fc=coli,ec='none')
    title(ID+'  '+pdbID)
    ##return resi,pc1s,pc2s,C
    return resi,pc1s,pc2s,C,zsco
    ##axis([-7,105,0,16])

def getramp(buf):
    dct={}
    for i in range(64):
        for j in range(4):
            rgb=[float(x)/255 for x in buf[i][4*j+1:4*j+4]]
            dct[i+j*64]=rgb
    return dct

def getColor(f,ramp):
    return ramp[int(255*f)]

def gencolpml(ID,pdbid='',delta=0):
    ##ramp1=getramp(initfil2('ramp1.dat'))
    resi,coli,zsco=viscolentry(ID,'',delta,doreturn=True)
    ##pmlfile=open('colCheZOD%s_%s.pml'%(ID,pdbid),'w')
    pmlfile=open('colCheSPI%s.pml'%ID,'w')
    for i,ri in enumerate(resi):
        rgbi=coli[i]
        ##print i,ri,rid,delta,rgbi,1/0
        pmlfile.write('set_color coluser%d, '%ri)
        pmlfile.write('[%5.3f, %5.3f, %5.3f]\n'%tuple(rgbi))
        ##pmlfile.write('color coluser%d, resi %s and chain A and %s\n'%(ri,ri,pdbid))
        pmlfile.write('color coluser%d, resi %s\n'%(ri,ri))
    pmlfile.close()

def savecolors(resi,coli):
    outfile=open('colors%s.txt'%ID,'w')
    for i,ri in enumerate(resi):
        rgbi=tuple(array(coli[i]*255,dtype=int))
        hexstr='#%02x%02x%02x' % rgbi
        outfile.write('%3d'%ri)
        outfile.write(' '+hexstr)
        outfile.write(' %3d %3d %3d\n'%rgbi)

def visprobs(resi,probs,pid='',seq=None):
    outfile=open('populations%s.txt'%pid,'w')
    secs='EHTpeh+'
    secs='EHTN'
    ##seccols=('b','r','g','0.5','xkcd:light blue','xkcd:orange','k')
    seccols=('b','r','g','0.5','c','y','k')
    reord=[1,2,3,0]# => order will be: HTNE
    for i,ri in enumerate(resi):
        probi=probs[i]
        probi=[probi[n] for n in reord]
        ##bottoms=[0.0,probi[0],probi[0]+probi[1]]
        acum=cumsum([0.0]+list(probi))##*10.0
        for n in range(4):
            bari=bar(ri-0.5,probi[n],bottom=acum[n],width=1.0,fc=seccols[reord[n]],ec='none')
        outfile.write('%s %3d '%(seq[ri-1],ri))
        ##outfile.write('%5.3f %5.3f %5.3f\n'%tuple(probi))
        outfile.write('%5.3f %5.3f %5.3f %5.3f\n'%tuple(probi))
    outfile.close()

def lineplot2dpcs2(resi,pc1s,pc2s,cols,ID):
    clf()
    title('Principal components '+ID)
    scatter(pc1s,pc2s,c=cols,s=100,faceted=False)
    plot(pc1s,pc2s,'k')
    plot([-18,18],[0,0],'k--')
    plot([0,0],[-16,16],'k--')
    axis([-18,18,-16,16])
    show(block=False);1/0

def run(bmrbID, workDir):
    if bmrbID.find('file://') == 0: # file:///Users/wlee/bmr6457_2.str
        fname = os.path.basename(bmrbID[7:]) # fname = bmr6457_2.str
        ID = '.'.join(fname.split('.')[:-1]) # ID = bmr6457_2

        f = open(bmrbID[7:], 'r')
        content = f.read()
        f.close()

        f = open(os.path.join(workDir, fname), 'w') # workDir/bmr6457_2.str
        f.write(content)
        f.close()
        from_bmrb = False
    else:
        ID = bmrbID
        from_bmrb = True
    os.chdir(workDir) # current directory: workDir
    plot2d=False

    # default value for minAIC
    minAIC = 5.0

    # get the chemical shift data
    # and transform to Z-scores and CheSPI components (PCs)
    sg=getCheZODandPCs(ID, minAIC=minAIC, from_bmrb=from_bmrb)

    inc=0
    if not PLOT12:
        clf()
        inc=202
    if True:
        # process all data, plot everything and store in text output files
        subplot(513-inc)
        resi,pc1s,pc2s,cols,zsco=viscolentry(ID)
        savecolors(resi,cols)
        title('CheSPI color plot for: %s'%ID)
        if plot2d:lineplot2dpcs2(resi,pc1s,pc2s,cols,ID)
        axis([resi[0],resi[-1]+0.0,0,16])
        subplot(514-inc)
        probs=getprobs(pc1s,pc2s)
        visprobs(resi,probs,ID,seq=sg.seq)
        title('CheSPI populations for: %s'%ID)
        axis([resi[0],resi[-1]+0.0,0,1])
        gencolpml(ID)##,delta=98+44)##,'3ezb')
        subplot(515-inc)
        predict8ss(ID,sg.seq,resi,pc1s,pc2s,zsco,dovis=False)
        title('CheSPI DSSP secondary structure 8-class predictions for: %s'%ID)
    tight_layout()
    savefig('cheSPIplot%s.pdf'%ID)
    show(block=False)

real_in_file = os.path.realpath(chespi_star)
real_path = os.path.dirname(real_in_file)

print(f'WORKING FOLDER: \t{real_path}')
print(f'FILENAME: \t{real_in_file}')
run(f'file://{real_in_file}', real_path)
