from subprocess import Popen,PIPE
from itertools import product
import sys, io
import numpy

run_fs = '../../FlexibleSUSY/models/NUHMSSMNoFV/run_NUHMSSMNoFV.x'

template_file_name = 'ms_tb_ma2_at'
fs_input_file_name = 'fs_input'
output_file_name = 'result_ms_xt_2'

msusy_range = numpy.array( [2000, 2000] )
xt_over_ms_range = numpy.array( [-numpy.pi, numpy.pi] )

num_msusy_points = 40
num_xt_over_ms_points = 40

msusy_points = numpy.unique(
  numpy.logspace( numpy.log10( msusy_range[0] ),
    numpy.log10( msusy_range[1] ), 
    num = num_msusy_points ) )
xt_over_ms_points = numpy.unique(
  numpy.linspace( xt_over_ms_range[0], xt_over_ms_range[1], 
    num = num_xt_over_ms_points ) )

template_file = open(template_file_name, 'r')
template = template_file.read()
template_file.close()

output_file = open(output_file_name, 'w')

for msusy, xt_over_ms in product(
  msusy_points, xt_over_ms_points ):

  xt = xt_over_ms * msusy
  ma2 = msusy ** 2
  tan_beta = 5.0
  at = xt - msusy / tan_beta

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
  
  data_point = (str(msusy) + ", " +
    str(tan_beta) + ", " +
    str(ma2) + ", " +
    str(at) + ", " +
    higgs_mass + "\n")
    
  output_file.write(data_point)
  output_file.flush()  
  
output_file.close()

