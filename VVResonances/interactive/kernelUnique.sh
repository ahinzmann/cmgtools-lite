#!bin/bash

name=2016_VV_VH_scheme2_deepAK8_W_0p05_0p10_ZHbb_0p02_0p10_DDT_nominalMaps_OPT3_0and2_OPTXY0and2_OPTZ1and2_PTZ2and2 #OPT31and1_OPTXY2_OPTZ2
postfitdir=postfit_qcd/${name}/
mkdir $postfitdir
cat=VH_LPHP
#               pythia
#HPLP
python transferKernelUnique.py -i results_2016/JJ_2016_nonRes_${cat}.root --sample pythia --year 2016 -p x --pdfIn results_2016/JJ_2016_nonRes_3D_none.root | tee KernelTransf_2016_${cat}_pythia_x_${name}.out

#python transferKernel.py -i results_2016/JJ_2016_nonRes_${cat}.root --sample pythia --year 2016 -p y --pdfIn results_2016/JJ_2016_nonRes_3D_none.root | tee KernelTransf_2016_${cat}_pythia_y_${name}.out

#python transferKernel.py -i results_2016/JJ_2016_nonRes_${cat}.root --sample pythia --year 2016 -p z --pdfIn results_2016/JJ_2016_nonRes_3D_none.root | tee KernelTransf_2016_${cat}_pythia_z_${name}.out
#                madgraph
#HPLP
python transferKernelUnique.py -i results_2016/JJ_2016_nonRes_${cat}.root --sample madgraph --year 2016 -p x --pdfIn results_2016/JJ_2016_nonRes_3D_none.root | tee KernelTransf_2016_${cat}_madgraph_x_${name}.out                                                                  

#python transferKernel.py -i results_2016/JJ_2016_nonRes_${cat}.root --sample madgraph --year 2016 -p y --pdfIn results_2016/JJ_2016_nonRes_3D_none.root | tee KernelTransf_2016_${cat}_madgraph_y_${name}.out

#python transferKernel.py -i results_2016/JJ_2016_nonRes_${cat}.root --sample madgraph --year 2016 -p z --pdfIn results_2016/JJ_2016_nonRes_3D_none.root | tee KernelTransf_2016_${cat}_madgraph_z_${name}.out

#         herwig
#HPLP
python transferKernelUnique.py -i results_2016/JJ_2016_nonRes_${cat}.root --sample herwig --year 2016 -p x --pdfIn results_2016/JJ_2016_nonRes_3D_none.root | tee KernelTransf_2016_${cat}_herwig_x_${name}.out

#python transferKernel.py -i results_2016/JJ_2016_nonRes_${cat}.root --sample herwig --year 2016 -p y --pdfIn results_2016/JJ_2016_nonRes_3D_none.root | tee KernelTransf_2016_${cat}_herwig_y_${name}.out

#python transferKernel.py -i results_2016/JJ_2016_nonRes_${cat}.root --sample herwig --year 2016 -p z --pdfIn results_2016/JJ_2016_nonRes_3D_none.root | tee KernelTransf_2016_${cat}_herwig_z_${name}.out

#        merge 
python transferKernel.py -i results_2016/JJ_2016_nonRes_${cat}.root --sample pythia --year 2016 -p z --pdfIn results_2016/JJ_2016_nonRes_3D_none.root --merge



mv postfit_qcd/PostFit_*.* $postfitdir



#     control plots
#HPLP
python Projections3DHisto_HPHP.py --mc results_2016/JJ_2016_nonRes_${cat}.root,nonRes -k save_new_shapes_2016_pythia_${cat}_3D.root,histo -o control-plots-QCD_pythia_signals_${cat}_${name}/       
python Projections3DHisto_HPHP.py --mc results_2016/JJ_2016_nonRes_${cat}_altshapeUp.root,nonRes -k save_new_shapes_2016_herwig_${cat}_3D.root,histo -o control-plots-QCD_herwig_signals_${cat}_${name}/
python Projections3DHisto_HPHP.py --mc results_2016/JJ_2016_nonRes_${cat}_altshape2.root,nonRes -k save_new_shapes_2016_madgraph_${cat}_3D.root,histo -o control-plots-QCD_madgraph_signals_${cat}_${name}/

#HPHP
#python Projections3DHisto_HPHP.py --mc results_2016/JJ_2016_nonRes_VV_HPHP.root,nonRes -k save_new_shapes_2016_pythia_VV_HPHP_3D.root,histo -o control-plots-QCD_pythia_signals_VV_HPHP_${name}/
#python Projections3DHisto_HPHP.py --mc results_2016/JJ_2016_nonRes_VV_HPHP_altshapeUp.root,nonRes -k save_new_shapes_2016_herwig_VV_HPHP_3D.root,histo -o control-plots-QCD_herwigh_signals_VV_HPHP_${name}
#python Projections3DHisto_HPHP.py --mc results_2016/JJ_2016_nonRes_VV_HPHP_altshape2.root,nonRes -k save_new_shapes_2016_madgraph_VV_HPHP_3D.root,histo -o control-plots-QCD_madgraph_signals_VV_HPHP_${name}/

