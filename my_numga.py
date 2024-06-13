#!/usr/bin/env python
# coding: utf-8

# In[1]:
"""Test the tennis racket theorem, or medial axis theorem."""

import numpy as np

from numga.algebra.algebra import Algebra
from numga.backend.numpy.context import NumpyContext as Context
from numga.examples.physics.core import Body

dt = 1 / 4
runtime = 200

# works for p=2,3,4,5
# p>3 is fascinating; some medial axes become seemingly chaotic
# but stranger still, some medial axes actually stabilize?
context = Context(Algebra.from_pqr(3, 0, 0), dtype=np.float64)


def make_n_cube(N):
  b = ((np.arange(2**N)[:, None] & (1 << np.arange(N))) > 0)
  return (2 * b - 1)


def make_n_rect(N):
  return make_n_cube(N) * (np.arange(N) + 1)


def make_point_cloud():
  points = make_n_rect(context.algebra.description.n_dimensions)
  return context.multivector.vector(points).dual()


# create a point cloud with distinct moments of inertia
points = make_point_cloud()
# set up independent identical copies of the point cloud
# equal to the number of independent spin planes
nb = len(context.subspace.bivector())
body = Body.from_point_cloud(points=points.repeat('... -> b ...', b=nb))

# set up initial conditions;
# each body gets a spin in a different plane; plus some jitter.
body.rate = body.rate + context.multivector.bivector(
  np.eye(nb) + np.random.normal(size=(nb, nb)) * 1e-5)
E = body.kinetic_energy()


#states = []
def timesteps(body=body, runtime=runtime, dt=dt, E=E):
  for i in range(int(runtime / dt)):
    body = body.integrate(dt)

    if False:
      # optionally, enforce strict energy conservation
      energy_violation = body.kinetic_energy() / E
      body = body.copy(rate=body.rate / energy_violation.sqrt())


#	print(i)
#	states.append(body.motor)
    yield body.motor
states = list(timesteps())

# visualize tumbling behavior
import matplotlib.pyplot as plt
plt.close()
v = np.array([s.values for s in states])
fig, ax = plt.subplots(nb, squeeze=False)
for i in range(nb):
  ax[i, 0].plot(v[:, i])
  # this shows initial energy; so we can distinguish medial axes from extrema
  ax[i, 0].set_ylabel(int(E.values[i][0]))
plt.show()

# In[2]:
"""Explore working with CGA in numga"""

import numpy as np

from numga.backend.numpy.context import NumpyContext
from numga.examples.conformal import Conformal, Conformalize


def plot_point(plt, cga, p, color='b'):
  assert p.subspace.inside.vector()
  plt.scatter(*cga.point_position(cga.normalize(p)).values.T, c=color)


def plot_circle(plt, cga, circle):
  assert circle.subspace.inside.antivector()
  circle = cga.normalize(circle.dual())
  # this is pretty elegant; center is point at infinity reflected in the circle
  center = cga.normalize(circle >> cga.ni)
  radius = circle.norm()

  ang = np.linspace(0, 2 * np.pi, 100, endpoint=True)
  cx, cy = np.cos(ang), np.sin(ang)
  r = radius.values
  px, py = cga.point_position(center).values.T
  if isinstance(px, float):
    plt.plot(cx * r + px, cy * r + py)
  else:
    for xx, yy, rr in zip(px, py, r):
      plt.plot(cx * rr + xx, cy * rr + yy)


def test_circle_reflect():
  # construct 2d cga
  cga = Conformalize(NumpyContext('x+y+'))

  # construct a point grid
  points = np.meshgrid(np.linspace(-1, 1, 11), np.linspace(-1, 1, 11))
  P = cga.embed_point(np.array(points).T.reshape(-1, 2), r=0.1)
  # construct a circle
  #
  C = cga.embed_point((-1.5, -1.5), r=2).dual()
  #C = cga.embed_point((0.1, 0.2), r=2).dual()
  Q = C >> P
  import matplotlib.pyplot as plt
  plt.close()
  plot_circle(plt, cga, P.dual())
  plot_circle(plt, cga, Q.dual())
  plot_circle(plt, cga, C)
  #plot_point(plt, cga, cga.project(Q, C.dual()))
  plt.axis('equal')
 # plt.xlim(left=-2.0,right=2.0)
 #  print(plt.ylim(top=-1.0,bottom=1.0))
  plt.show()

def test_circle_fit():
  # construct 2d cga
  cga = Conformal(NumpyContext(Conformal.algebra('x+y+')))

  assert np.allclose(cga.ni.norm().values, 0)
  assert np.allclose(cga.no.norm().values, 0)
  assert np.allclose(((cga.N * cga.N)).values, 1)

  # create some points
  a, b, c = cga.embed_point((-1.5, -0.5)), cga.embed_point(
    (1, -0.5)), cga.embed_point((0, 1.5))

  assert np.allclose(b.inner(cga.ni).values, -1)
  assert np.allclose((b * b).values, 0)
  assert np.allclose(cga.point_position(b).values, (1, -0.5))

  # construct a circle as the wedge of three points
  C = a ^ b ^ c
  # direct construction of a circle
  D = cga.embed_point((-1, -1), r=1).dual()
  # get intersection set of two circles
  T = C & D
  # split them out into two points
  l, r = cga.split_points(T)

  import matplotlib.pyplot as plt
  plt.close()

  plot_circle(plt, cga, C)
  plot_circle(plt, cga, D)

  plot_point(plt, cga, a, 'b')
  plot_point(plt, cga, b, 'b')
  plot_point(plt, cga, c, 'b')

  plot_point(plt, cga, l, 'r')
  plot_point(plt, cga, r, 'r')

  plt.axis('equal')
  
  plt.show()

# In[3]:

test_circle_fit()

# In[4]:

test_circle_reflect()

# In[ ]:

