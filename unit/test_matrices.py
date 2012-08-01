# This file is part of PyOP2
#
# PyOP2 is Copyright (c) 2012, Imperial College London and
# others. Please see the AUTHORS file in the main source directory for
# a full list of copyright holders.  All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * The name of Imperial College London or that of other
#       contributors may not be used to endorse or promote products
#       derived from this software without specific prior written
#       permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTERS
# ''AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
# OF THE POSSIBILITY OF SUCH DAMAGE.

import pytest
import numpy

from pyop2 import op2

backends = ['sequential']

# Data type
valuetype = numpy.float64

# Constants
NUM_ELE   = 2
NUM_NODES = 4
NUM_DIMS  = 2

class TestMatrices:
    """
    Matrix tests

    """

    def pytest_funcarg__nodes(cls, request):
        # FIXME: Cached setup can be removed when __eq__ methods implemented.
        return request.cached_setup(
                setup=lambda: op2.Set(NUM_NODES, "nodes"), scope='session')

    def pytest_funcarg__elements(cls, request):
        return op2.Set(NUM_ELE, "elements")

    def pytest_funcarg__elem_node(cls, request):
        elements = request.getfuncargvalue('elements')
        nodes = request.getfuncargvalue('nodes')
        elem_node_map = numpy.asarray([ 0, 1, 3, 2, 3, 1 ], dtype=numpy.uint32)
        return op2.Map(elements, nodes, 3, elem_node_map, "elem_node")

    def pytest_funcarg__mat(cls, request):
        elem_node = request.getfuncargvalue('elem_node')
        sparsity = op2.Sparsity(elem_node, elem_node, 1, "sparsity")
        return request.cached_setup(
                setup=lambda: op2.Mat(sparsity, 1, valuetype, "mat"),
                scope='session')

    def pytest_funcarg__coords(cls, request):
        nodes = request.getfuncargvalue('nodes')
        coord_vals = numpy.asarray([ (0.0, 0.0), (2.0, 0.0),
                                     (1.0, 1.0), (0.0, 1.5) ],
                                   dtype=valuetype)
        return op2.Dat(nodes, 2, coord_vals, valuetype, "coords")

    def pytest_funcarg__f(cls, request):
        nodes = request.getfuncargvalue('nodes')
        f_vals = numpy.asarray([ 1.0, 2.0, 3.0, 4.0 ], dtype=valuetype)
        return op2.Dat(nodes, 1, f_vals, valuetype, "f")

    def pytest_funcarg__b(cls, request):
        nodes = request.getfuncargvalue('nodes')
        b_vals = numpy.asarray([0.0]*NUM_NODES, dtype=valuetype)
        return request.cached_setup(
                setup=lambda: op2.Dat(nodes, 1, b_vals, valuetype, "b"),
                scope='session')

    def pytest_funcarg__x(cls, request):
        nodes = request.getfuncargvalue('nodes')
        x_vals = numpy.asarray([0.0]*NUM_NODES, dtype=valuetype)
        return op2.Dat(nodes, 1, x_vals, valuetype, "x")

    def pytest_funcarg__mass(cls, request):
        kernel_code = """
void mass(double* localTensor, double* c0[2], int i_r_0, int i_r_1)
{
  const double CG1[3][6] = { {  0.09157621, 0.09157621, 0.81684757,
                                   0.44594849, 0.44594849, 0.10810302 },
                                {  0.09157621, 0.81684757, 0.09157621,
                                   0.44594849, 0.10810302, 0.44594849 },
                                {  0.81684757, 0.09157621, 0.09157621,
                                   0.10810302, 0.44594849, 0.44594849 } };
  const double d_CG1[3][6][2] = { { {  1., 0. },
                                       {  1., 0. },
                                       {  1., 0. },
                                       {  1., 0. },
                                       {  1., 0. },
                                       {  1., 0. } },

                                     { {  0., 1. },
                                       {  0., 1. },
                                       {  0., 1. },
                                       {  0., 1. },
                                       {  0., 1. },
                                       {  0., 1. } },

                                     { { -1.,-1. },
                                       { -1.,-1. },
                                       { -1.,-1. },
                                       { -1.,-1. },
                                       { -1.,-1. },
                                       { -1.,-1. } } };
  const double w[6] = {  0.05497587, 0.05497587, 0.05497587, 0.11169079,
                            0.11169079, 0.11169079 };
  double c_q0[6][2][2];
  for(int i_g = 0; i_g < 6; i_g++)
  {
    for(int i_d_0 = 0; i_d_0 < 2; i_d_0++)
    {
      for(int i_d_1 = 0; i_d_1 < 2; i_d_1++)
      {
        c_q0[i_g][i_d_0][i_d_1] = 0.0;
        for(int q_r_0 = 0; q_r_0 < 3; q_r_0++)
        {
          c_q0[i_g][i_d_0][i_d_1] += c0[q_r_0][i_d_0] * d_CG1[q_r_0][i_g][i_d_1];
        };
      };
    };
  };
  for(int i_g = 0; i_g < 6; i_g++)
  {
    double ST0 = 0.0;
    ST0 += CG1[i_r_0][i_g] * CG1[i_r_1][i_g] * (c_q0[i_g][0][0] * c_q0[i_g][1][1] + -1 * c_q0[i_g][0][1] * c_q0[i_g][1][0]);
    localTensor[0] += ST0 * w[i_g];
  };
}"""
        return op2.Kernel(kernel_code, "mass")

    def pytest_funcarg__rhs(cls, request):

        kernel_code = """
void rhs(double** localTensor, double* c0[2], double* c1[1])
{
  const double CG1[3][6] = { {  0.09157621, 0.09157621, 0.81684757,
                                   0.44594849, 0.44594849, 0.10810302 },
                                {  0.09157621, 0.81684757, 0.09157621,
                                   0.44594849, 0.10810302, 0.44594849 },
                                {  0.81684757, 0.09157621, 0.09157621,
                                   0.10810302, 0.44594849, 0.44594849 } };
  const double d_CG1[3][6][2] = { { {  1., 0. },
                                       {  1., 0. },
                                       {  1., 0. },
                                       {  1., 0. },
                                       {  1., 0. },
                                       {  1., 0. } },

                                     { {  0., 1. },
                                       {  0., 1. },
                                       {  0., 1. },
                                       {  0., 1. },
                                       {  0., 1. },
                                       {  0., 1. } },

                                     { { -1.,-1. },
                                       { -1.,-1. },
                                       { -1.,-1. },
                                       { -1.,-1. },
                                       { -1.,-1. },
                                       { -1.,-1. } } };
  const double w[6] = {  0.05497587, 0.05497587, 0.05497587, 0.11169079,
                            0.11169079, 0.11169079 };
  double c_q1[6];
  double c_q0[6][2][2];
  for(int i_g = 0; i_g < 6; i_g++)
  {
    c_q1[i_g] = 0.0;
    for(int q_r_0 = 0; q_r_0 < 3; q_r_0++)
    {
      c_q1[i_g] += c1[q_r_0][0] * CG1[q_r_0][i_g];
    };
    for(int i_d_0 = 0; i_d_0 < 2; i_d_0++)
    {
      for(int i_d_1 = 0; i_d_1 < 2; i_d_1++)
      {
        c_q0[i_g][i_d_0][i_d_1] = 0.0;
        for(int q_r_0 = 0; q_r_0 < 3; q_r_0++)
        {
          c_q0[i_g][i_d_0][i_d_1] += c0[q_r_0][i_d_0] * d_CG1[q_r_0][i_g][i_d_1];
        };
      };
    };
  };
  for(int i_r_0 = 0; i_r_0 < 3; i_r_0++)
  {
    for(int i_g = 0; i_g < 6; i_g++)
    {
      double ST1 = 0.0;
      ST1 += CG1[i_r_0][i_g] * c_q1[i_g] * (c_q0[i_g][0][0] * c_q0[i_g][1][1] + -1 * c_q0[i_g][0][1] * c_q0[i_g][1][0]);
      localTensor[i_r_0][0] += ST1 * w[i_g];
    };
  };
}"""
        return op2.Kernel(kernel_code, "rhs")

    def pytest_funcarg__mass_ffc(cls, request):
        kernel_code = """
void mass_ffc(double *A, double *x[2], int j, int k)
{
    // Compute Jacobian of affine map from reference cell
    const double J_00 = x[1][0] - x[0][0];
    const double J_01 = x[2][0] - x[0][0];
    const double J_10 = x[1][1] - x[0][1];
    const double J_11 = x[2][1] - x[0][1];

    // Compute determinant of Jacobian
    double detJ = J_00*J_11 - J_01*J_10;

    // Compute inverse of Jacobian

    // Set scale factor
    const double det = fabs(detJ);

    // Cell Volume.

    // Compute circumradius, assuming triangle is embedded in 2D.


    // Facet Area.

    // Array of quadrature weights.
    static const double W3[3] = {0.166666666666667, 0.166666666666667, 0.166666666666667};
    // Quadrature points on the UFC reference element: (0.166666666666667, 0.166666666666667), (0.166666666666667, 0.666666666666667), (0.666666666666667, 0.166666666666667)

    // Value of basis functions at quadrature points.
    static const double FE0[3][3] = \
    {{0.666666666666667, 0.166666666666667, 0.166666666666667},
    {0.166666666666667, 0.166666666666667, 0.666666666666667},
    {0.166666666666667, 0.666666666666667, 0.166666666666667}};

    // Reset values in the element tensor.

    // Compute element tensor using UFL quadrature representation
    // Optimisations: ('eliminate zeros', False), ('ignore ones', False), ('ignore zero tables', False), ('optimisation', False), ('remove zero terms', False)

    // Loop quadrature points for integral.
    // Number of operations to compute element tensor for following IP loop = 108
    for (unsigned int ip = 0; ip < 3; ip++)
    {

      // Number of operations for primary indices: 36
      // Number of operations to compute entry: 4
      *A += FE0[ip][j]*FE0[ip][k]*W3[ip]*det;
    }// end loop over 'ip'
}
"""

        return op2.Kernel(kernel_code, "mass_ffc")

    def pytest_funcarg__rhs_ffc(cls, request):

        kernel_code="""
void rhs_ffc(double **A, double *x[2], double **w0)
{
    // Compute Jacobian of affine map from reference cell
    const double J_00 = x[1][0] - x[0][0];
    const double J_01 = x[2][0] - x[0][0];
    const double J_10 = x[1][1] - x[0][1];
    const double J_11 = x[2][1] - x[0][1];

    // Compute determinant of Jacobian
    double detJ = J_00*J_11 - J_01*J_10;

    // Compute inverse of Jacobian

    // Set scale factor
    const double det = fabs(detJ);

    // Cell Volume.

    // Compute circumradius, assuming triangle is embedded in 2D.


    // Facet Area.

    // Array of quadrature weights.
    static const double W3[3] = {0.166666666666667, 0.166666666666667, 0.166666666666667};
    // Quadrature points on the UFC reference element: (0.166666666666667, 0.166666666666667), (0.166666666666667, 0.666666666666667), (0.666666666666667, 0.166666666666667)

    // Value of basis functions at quadrature points.
    static const double FE0[3][3] = \
    {{0.666666666666667, 0.166666666666667, 0.166666666666667},
    {0.166666666666667, 0.166666666666667, 0.666666666666667},
    {0.166666666666667, 0.666666666666667, 0.166666666666667}};


    // Compute element tensor using UFL quadrature representation
    // Optimisations: ('eliminate zeros', False), ('ignore ones', False), ('ignore zero tables', False), ('optimisation', False), ('remove zero terms', False)

    // Loop quadrature points for integral.
    // Number of operations to compute element tensor for following IP loop = 54
    for (unsigned int ip = 0; ip < 3; ip++)
    {

      // Coefficient declarations.
      double F0 = 0.0;

      // Total number of operations to compute function values = 6
      for (unsigned int r = 0; r < 3; r++)
      {
        F0 += FE0[ip][r]*w0[r][0];
      }// end loop over 'r'

      // Number of operations for primary indices: 12
      for (unsigned int j = 0; j < 3; j++)
      {
        // Number of operations to compute entry: 4
        A[j][0] += FE0[ip][j]*F0*W3[ip]*det;
      }// end loop over 'j'
    }// end loop over 'ip'
}
"""

        return op2.Kernel(kernel_code, "rhs_ffc")

    def pytest_funcarg__zero_dat(cls, request):

        kernel_code="""
void zero_dat(double *dat)
{
  *dat = 0.0;
}
"""

        return op2.Kernel(kernel_code, "zero_dat")

    def pytest_funcarg__expected_matrix(cls, request):
        expected_vals = [(0.25, 0.125, 0.0, 0.125),
                         (0.125, 0.291667, 0.0208333, 0.145833),
                         (0.0, 0.0208333, 0.0416667, 0.0208333),
                         (0.125, 0.145833, 0.0208333, 0.291667) ]
        return numpy.asarray(expected_vals, dtype=valuetype)

    def pytest_funcarg__expected_rhs(cls, request):
        return numpy.asarray([[0.9999999523522115], [1.3541666031724144],
                              [0.2499999883507239], [1.6458332580869566]],
                              dtype=valuetype)

    def test_assemble(self, backend, mass, mat, coords, elements, elem_node,
                      expected_matrix):
        op2.par_loop(mass, elements(3,3),
                     mat((elem_node(op2.i(0)), elem_node(op2.i(1))), op2.INC),
                     coords(elem_node, op2.READ))
        eps=1.e-6
        assert (abs(mat.values-expected_matrix)<eps).all()

    def test_rhs(self, backend, rhs, elements, b, coords, f, elem_node,
                     expected_rhs):
        op2.par_loop(rhs, elements,
                     b(elem_node, op2.INC),
                     coords(elem_node, op2.READ),
                     f(elem_node, op2.READ))

        eps = 1.e-12
        assert all(abs(b.data-expected_rhs)<eps)

    def test_solve(self, backend, mat, b, x, f):
        op2.solve(mat, b, x)
        eps = 1.e-12
        assert all(abs(x.data-f.data)<eps)

    def test_zero_matrix(self, backend, mat):
        """Test that the matrix is zeroed correctly."""
        mat.zero()
        expected_matrix = numpy.asarray([[0.0]*4]*4, dtype=valuetype)
        eps=1.e-14
        assert (abs(mat.values-expected_matrix)<eps).all()

    def test_zero_rhs(self, backend, b, zero_dat, nodes):
        """Test that the RHS is zeroed correctly."""
        op2.par_loop(zero_dat, nodes,
                     b(op2.IdentityMap, op2.WRITE))
        assert all(map(lambda x: x==0.0, b.data))

    def test_assemble_ffc(self, backend, mass_ffc, mat, coords, elements,
                          elem_node, expected_matrix):
        """Test that the FFC mass assembly assembles the correct values."""
        op2.par_loop(mass_ffc, elements(3,3),
                     mat((elem_node(op2.i(0)), elem_node(op2.i(1))), op2.INC),
                     coords(elem_node, op2.READ))
        eps=1.e-6
        assert (abs(mat.values-expected_matrix)<eps).all()

    def test_rhs_ffc(self, rhs_ffc, elements, b, coords, f, elem_node,
                         expected_rhs):
        op2.par_loop(rhs_ffc, elements,
                     b(elem_node, op2.INC),
                     coords(elem_node, op2.READ),
                     f(elem_node, op2.READ))

        eps = 1.e-6
        assert all(abs(b.data-expected_rhs)<eps)

    def test_zero_rows(self, mat, expected_matrix):
        expected_matrix[0] = [12.0, 0.0, 0.0, 0.0]
        mat.zero_rows([0], 12.0)
        eps=1.e-6
        assert (abs(mat.values-expected_matrix)<eps).all()

if __name__ == '__main__':
    import os
    pytest.main(os.path.abspath(__file__))
