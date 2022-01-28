#!bin/bash
basedir=results_Run2/
categories=("VV_HPHP" "VV_HPLP" "VH_HPHP" "VH_LPHP" "VH_HPLP" "VBF_VV_HPHP" "VBF_VV_HPLP" "VBF_VH_HPHP" "VBF_VH_LPHP" "VBF_VH_HPLP")
dir40=${basedir}pseudo40/
mkdir $dir40
#dir20=${basedir}pseudo20/
#mkdir $dir20

for cat in ${categories[*]}; do
    echo $cat
    #echo $dir20
    echo $dir40
    python rebinPseudodataAndTemplates.py -c $cat -i ${basedir}pseudo80/ -o $dir40 -b 2 -p "Run2" --wtd "datanormttshapes" #pseudo" #tt
    #python rebinPseudodataAndTemplates.py -c $cat -i ${basedir}pseudo80/ -o $dir20 -b 4 -p "Run2" --wtd "datanormttshapes" #pseudo" #tt
    #python rebinPseudodataAndTemplates.py -c $cat -i ${basedir}pseudo80/ -o $dir40 -b 2 -p "Run2" --wtd "dib"
done


