from subprocess import Popen,PIPE
from itertools import product
from joblib import Parallel, delayed
from itertools import izip_longest
from subprocess import call
from random import seed, random
import sys, io
import numpy

def run_input( run_fs, msusy, ma2, tan_beta, xt ):
  mu = msusy

  at = - xt + mu / tan_beta
  ab = mu * tan_beta
  atau = mu * tan_beta

  print(msusy)
  sys.stdout.flush()
  
  template_file_name = 'template'

  template_file = open( template_file_name, 'r' )
  template = template_file.read()
  template_file.close()
  
  fs_input_str = template.replace(
    "${TanBeta}", str(tan_beta)
  ).replace(
    "${MA2}", str(ma2)
  ).replace(
    "${At}", str(at)
  ).replace(
    "${Ab}", str(ab)
  ).replace(
    "${Atau}", str(atau)
  ).replace(
    "${Mu}", str(mu)
  )

  seed()
  while "${MS}" in fs_input_str:
    fs_input_str = fs_input_str.replace(
      "${MS}",
      str( msusy + 2.0 * (random() - 0.5) * msusy / 1000.0 ),
      1
    )
  
  fs = Popen(
    [run_fs, "--slha-input-file=-"],
    stdin=PIPE, stdout=PIPE )
  fs_output = fs.communicate(
    input=fs_input_str.encode() )[0].decode()
  
  matching_worked = False
  fs_worked = False
  for line in io.StringIO(fs_output):
    if "Matching to THDMII" in line:
      matching_data = ' '.join( line.split()[-1:] )
      matching_worked = True
      break
  for line in io.StringIO(fs_output):
    if "hh(1)" in line:
      fs_mass = line.split()[1]
      fs_worked = True
      break
  
  if not matching_worked:
    matching_data = '0'
  if not fs_worked:
    fs_mass = '0'

  return (str(msusy) + ", " +
    str(ma2) + ", " +
    str(tan_beta) + ", " +
    str(xt) + ", " +
    matching_data + ", " +
    fs_mass)

def group_iterable( n, iterable, fillvalue=None ):
    args = [iter( iterable )] * n
    return izip_longest( fillvalue=fillvalue, *args )

if __name__ == '__main__':
  if len(sys.argv) == 1:
    print 'No output file specified.'
    sys.exit(1)

  output_file_name = sys.argv[1]

  run_fs_orig = '../../FlexibleSUSY/models/NUHMSSMNoFV/run_NUHMSSMNoFV.x'
  run_fs_local = './run_NUHMSSMNoFV.x'

  call(["cp", run_fs_orig, run_fs_local])

  msusy_range = numpy.array( [300, 10000] )
  ma_range = numpy.array( [300, 300] )
  tan_beta_range = numpy.array( [10, 10] )
  xt_range = numpy.array( [0, 0] )
  
  num_parallel_workers = 8
  num_msusy_points = 80
  num_ma2_points = 20
  num_tan_beta_points = 10
  num_xt_points = 100
  
  msusy_points = numpy.unique(
    numpy.linspace( msusy_range[0], msusy_range[1], 
      num = num_msusy_points ) )
  ma2_points = numpy.square( numpy.unique(
    numpy.linspace( ma_range[0], ma_range[1], 
      num = num_ma2_points ) ) )
  tan_beta_points = numpy.unique(
    numpy.linspace( tan_beta_range[0], tan_beta_range[1], 
      num = num_tan_beta_points ) )
  xt_points = numpy.unique(
    numpy.linspace( xt_range[0], xt_range[1], 
      num = num_xt_points ) )
  
  with open(output_file_name, 'w') as output_file:
    with Parallel( n_jobs = 8 ) as parallel:
      input_data = product(
        msusy_points, ma2_points, tan_beta_points, xt_points )
      batch_size = num_parallel_workers

      for batch_candidate in group_iterable( batch_size, input_data ):
        batch = filter( lambda args: not None in args, batch_candidate )
        results = parallel( delayed(run_input)( 
          run_fs_local, *input_args ) for input_args in batch )
      
        output_file.write("\n".join( results ) + "\n")
        output_file.flush()

