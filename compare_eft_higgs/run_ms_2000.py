from subprocess import Popen,PIPE
from itertools import product
import sys, io
import numpy

run_fs = '../../FlexibleSUSY/models/NUHMSSMNoFV/run_NUHMSSMNoFV.x'

template_file_name = 'ms_tb_ma2_at'
fs_input_file_name = 'fs_input'
output_file_name = 'result_ms_2000'

msusy_range = numpy.array( [100, 100000] )

num_msusy_points = 40

msusy_points = numpy.unique(
  numpy.logspace( numpy.log10( msusy_range[0] ),
    numpy.log10( msusy_range[1] ), 
    num = num_msusy_points ) )

template_file = open(template_file_name, 'r')
template = template_file.read()
template_file.close()

output_file = open(output_file_name, 'w')

for msusy in msusy_points:

  tan_beta = 5.0
  ma2 = 2000.0 ** 2
  at = -msusy / tan_beta

  print(msusy, tan_beta, ma2, at)
  sys.stdout.flush()  
  
  fs_input_str = template.replace(
    "${MS}", str(msusy)
  ).replace(
    "${TanBeta}", str(tan_beta)
  ).replace(
    "${MA2}", str(ma2)
  ).replace(
    "${At}", str(at)
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
  
  data_point = (str(msusy) + ", " + higgs_mass + "\n")
    
  output_file.write(data_point)
  output_file.flush()  
  
output_file.close()

