from subprocess import Popen,PIPE
from itertools import product
import sys, io
import numpy

run_fs = '../../FlexibleSUSY/models/NUHMSSMNoFV/run_NUHMSSMNoFV.x'

template_file_name = 'ms_tb_ma2'
fs_input_file_name = 'fs_input'
output_file_name = 'result_taurus_3'

msusy_range = numpy.array( [500, 15000] )
tan_beta_range = numpy.array( [1.1, 50] )
ma2_range = numpy.array( [750000, 750000] )

num_msusy_points = 40
num_tan_beta_points = 20
num_ma2_points = 100

msusy_points = numpy.unique(
  numpy.linspace( msusy_range[0], msusy_range[1], 
    num = num_msusy_points ) )
tan_beta_points = numpy.unique(
  numpy.linspace( tan_beta_range[0], tan_beta_range[1], 
    num = num_tan_beta_points ) )
ma2_points = numpy.unique(
  numpy.linspace( ma2_range[0], ma2_range[1], 
    num = num_ma2_points ) )

template_file = open(template_file_name, 'r')
template = template_file.read()
template_file.close()

output_file = open(output_file_name, 'w')

for msusy, tan_beta, ma2 in product(
  msusy_points, tan_beta_points, ma2_points ):
  print(msusy, tan_beta, ma2)
  sys.stdout.flush()  
 
  fs_input_str = template.replace(
    "${MS}", str(msusy)
  ).replace(
    "${TanBeta}", str(tan_beta)
  ).replace(
    "${MA2}", str(ma2)
  )
  
  fs_input_file = open(fs_input_file_name, 'w')
  fs_input_file.write( fs_input_str )
  fs_input_file.close()
  
  fs = Popen(
    [run_fs, "--slha-input-file=" + fs_input_file_name],
    stdout=PIPE)
  fs_output = fs.communicate()[0].decode()
  
  matching_worked = False
  for line in io.StringIO(fs_output):
    if "Matching to THDMII" in line:
      higgs_mass = line.split()[-1]
      matching_worked = True
      break
  
  if not matching_worked:
    higgs_mass = "0"
  
  data_point = (str(msusy) + ", " +
    str(tan_beta) + ", " +
    str(ma2) + ", " +
    higgs_mass + "\n")
    
  output_file.write(data_point)
  output_file.flush()  

output_file.close()

