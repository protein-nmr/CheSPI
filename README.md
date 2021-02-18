# CheSPI
Chemical shift Secondary structure Population Inference

1. Derives Principal components from chemical shifts to infer local structure and dynamics.
2. Predicts secondary structure populations from chemical shifts.
3. Predicts secondary structure DSSP 8-state classes from chemical shifts.

python command-line application

usage: python_exe cheSPI4c.py ID [-p] [option] > logfile &
if option is 2: will plot a 2d plot or first two CheSPI components
if option is any other number: will interpret this value as so-called minAIC, which controls automatic re-referencing

note: default value is minAIC = 5.0. Lowering this value will favour re-referencing even with small offset corrections, increasing it will dis-favour re-referencing and only envoke it with high offsets. Setting minAIC very high to e.g. 999 will de facto disable re-referencing.

requirements: python must be version 2 with packages: numpy, scipy, matplotlib

Arguments for cheSPI: ID specifies id for either (i) published BMRB id or (ii) a local provided NMR-STAR file id (version 2.1). (i) The data will be downloaded automatically from the corresponding ftp site for the specified bmrid. (ii) An NMR-STAR file (v2.1) must be placed in the running directory. The NMR-STAR file must contain chemical shifts (SCSs) and specify: “_Mol_residue_sequence", "assigned_chemical_shifts" and sample_conditions loop

Output files:
i) Secondary chemical shifts (SCSs), “shiftsID.txt”. Shift file has: residue number, residue type, atom type, assigned chemical shift, pentapeptide context, and SCS.
ii) CheZOD Z-scores and CheSPI principal components: “zscoresID.txt”. Z-score output has the following columns: residue name, residue number, Z-score, and principal components 1-3
iii) CheSPI colors: "colorsID.txt" with the following columns: residue number, hexstring, rgb integers in the final three columns
iv) PyMol script for coloring residues with CheSPI colors: "colCheSPIID.txt"
v) CheSPI secondary structure populations: "populationsID.txt" with columns: residue type, residues number, and populations for helix, sheet, and coil, respectively, in the three following columns
vi) Probability for all 8-state DSSP secondary structure classes: "probs8_ID.txt" with columns: residue type, residue number, and probabilities for H/G/I/E/-/T/S/B in the eight following column corresponding to alpha-helix/3_10-helix/I-helix/sheet/none(extended or disordered)/turn/bend/bridge.
vii) Probability for all 3-state DSSP secondary structure classes: "probs3_ID.txt" with columns: residue type, residue number, and probabilities for H/S/C in the three following column corresponding to helix/sheet/coil
viii) Best prediction with maximum probability for 8-state DSSP secondary structure class: "max8_ID.txt" with columns: residue type, residue number, and DSSP 8-state label, estimated probability for the given maximum state, posterior probabilty (higher values implies more confident assignment)
iv) Best prediction with maximum probability for 3-state DSSP secondary structure class: same as the above - but for 3-state secondary structure
x) short summary of 8-class predictions. Each property is joined for all residues to the following single lines: residue numbering, amino acid sequence, confidence digit (higher values implies higher confidence), 8-class DSSP prediction
xi) short summary of 3-class predictions. Same as the above but for 3-classes H/S/C for helix/sheet/coil

A plot windwow opens with 3 panels ##(change flag "-p" to "-n" to omit plot. In this case pylab and pyqt are not required).
Panel 1: Bar plot with colored with derived CheSPI colors using CheZOD Z-scores for the bar heights.
Panel 2: CheSPI secondary structure populations shown as accumulated bar-chart using red, blue, green and grey for helical, extended, turn and non-folded conformations, respectively.
Panel 3: Derived probabilities of 8-state DSSP secondary structure classes shown as accumulated bar-chart using red, magenta, white, black, grey, green, cyan, and blue colors, respectively, for 8-classes labeled, H/G/I/S/-/T/B/E, respectively, corresponding to alpha-helix/3_10-helix/I-helix/bend/none(extended or disordered)/turn/bridge/sheet
note that in cases of missing experimental chemical shifts, the secondary structure prediction will still be provided but based on the sequence alone.
