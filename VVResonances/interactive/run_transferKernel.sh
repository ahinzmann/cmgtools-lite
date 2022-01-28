#!/bin/bash

catIn=$1
catOut=$2
samples=(pythia herwig madgraph)
labels=("" _altshapeUp _altshape2)
nicelabels=("Pythia8" "Herwig++" "Madgraph+Phythia8")
period=Run2
year="2016,2017,2018"
inputdir=results_Run2/
normdir=results_Run2/

#create the directory to store the results
mkdir postfit_qcd


#fit MC in catOut category with templates of catIn category
for i in ${!samples[*]}
do
    echo "----------------------------------- start "  ${nicelabels[$i]}
    python transferKernel.py -i ${normdir}/JJ_${period}_nonRes_${catOut}${labels[$i]}.root --sample ${samples[$i]} --year ${year} -p xyz --pdfIn ${inputdir}/JJ_${period}_nonRes_3D_${catIn}.root --channel ${catOut}
    echo "----------------------------------- end "  ${nicelabels[$i]}
done

#merge post-fit 1Dx2Dx2D templates for catOut category
echo "----------------------------------- merging "
python transferKernel.py -i ${normdir}/JJ_${period}_nonRes_${catOut}.root --year ${year} --pdfIn ${inputdir}/JJ_${period}_nonRes_3D_${catIn}.root --merge
echo "----------------------------------- done merging "

#make post-fit validation plots for category catOut
for i in ${!samples[*]}
do
        python Projections3DHisto.py --mc ${normdir}/JJ_${period}_nonRes_${catOut}${labels[$i]}.root,nonRes -k save_new_shapes_${period}_${samples[$i]}_${catOut}_3D.root,histo -o control-plots-${period}-${catOut}-${samples[$i]} --period "${period}" -l ${nicelabels[$i]}

        python Projections3DHisto_HPHP.py --mc ${normdir}/JJ_${period}_nonRes_${catOut}${labels[$i]}.root,nonRes -k save_new_shapes_${period}_${samples[$i]}_${catOut}_3D.root,histo -o control-plots-coarse-${period}-${catOut}-${samples[$i]} --period "${period}" -l ${nicelabels[$i]}
done	
