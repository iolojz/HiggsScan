from subprocess import Popen,PIPE
from itertools import product
from joblib import Parallel, delayed
from itertools import izip_longest
from subprocess import call
import sys, io
import numpy

def run_input( run_fs, msusy, ma2, tan_beta ):
  at = -msusy / tan_beta

  print(msusy, ma2, tan_beta)
  sys.stdout.flush()
  
  template_file_name = 'ms_tb_ma2_at'

  template_file = open( template_file_name, 'r' )
  template = template_file.read()
  template_file.close()
  
  fs_input_str = template.replace(
    "${MS}", str(msusy)
  ).replace(
    "${TanBeta}", str(tan_beta)
  ).replace(
    "${MA2}", str(ma2)
  ).replace(
    "${At}", str(at)
  )
  
  fs = Popen(
    [run_fs, "--slha-input-file=-"],
    stdin=PIPE, stdout=PIPE )
  fs_output = fs.communicate(
    input=fs_input_str.encode() )[0].decode()
  
  matching_worked = False
  for line in io.StringIO(fs_output):
    if "Matching to THDMII" in line:
      matching_data = ' '.join( line.split()[-9:] )
      matching_worked = True
      break
  
  if not matching_worked:
    matching_data = '0, 0, 0, 0, 0, 0, 0, 0, 0'
  
  return (str(msusy) + ", " +
    str(ma2) + ", " +
    str(tan_beta) + ", " +
    matching_data)

def group_iterable( n, iterable, fillvalue=None ):
    args = [iter( iterable )] * n
    return izip_longest( fillvalue=fillvalue, *args )

if __name__ == '__main__':
  run_fs_orig = '../../FlexibleSUSY/models/NUHMSSMNoFV/run_NUHMSSMNoFV.x'
  run_fs_local = './run_NUHMSSMNoFV.x'

  call(["cp", run_fs_orig, run_fs_local])

  msusy_range = numpy.array( [100, 5000] )
  ma_range = numpy.array( [566.667, 566.667] )
  tan_beta_range = numpy.array( [6.92308, 6.92308] )
  
  num_parallel_workers = 4
  num_msusy_points = 80
  num_ma2_points = 10
  num_tan_beta_points = 40
  
  msusy_points = numpy.unique(
    numpy.linspace( msusy_range[0], msusy_range[1], 
      num = num_msusy_points ) )
  ma2_points = numpy.square( numpy.unique(
    numpy.linspace( ma_range[0], ma_range[1], 
      num = num_ma2_points ) ) )
  tan_beta_points = numpy.unique(
    numpy.linspace( tan_beta_range[0], tan_beta_range[1], 
      num = num_tan_beta_points ) )
  
  output_file_name = 'result_ms'
  with open(output_file_name, 'w') as output_file:
    with Parallel( n_jobs = 4 ) as parallel:
      input_data = product(
        msusy_points, ma2_points, tan_beta_points )
      batch_size = num_parallel_workers

      for batch_candidate in group_iterable( batch_size, input_data ):
        batch = filter( lambda args: not None in args, batch_candidate )
        results = parallel( delayed(run_input)( 
          run_fs_local, *input_args ) for input_args in batch )
      
        output_file.write("\n".join( results ) + "\n")
        output_file.flush()

