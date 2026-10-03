# What the passive material baseline can sustain

This is a deduction from `scripts/report_material_specimen.py`, not a claim
about all possible Matrix Engine mechanisms. It gives a P09 baseline prediction
before selecting a more complex material or drive model.

## Declared forces imply a definite input-off outcome

For the two equal masses, after external forcing stops:

```
M x'' + C x' + K x = 0
M = m I
K = [[ka+kl, -kl], [-kl, ka+kl]]
C = [[ca+cl, -cl], [-cl, ca+cl]]
E = (x' transpose M x' + x transpose K x)/2
dE/dt = -ca(v0^2+v1^2) - cl(v1-v0)^2
```

With the chosen m>0, ka>0 and ca>0, and nonnegative kl and cl, both K and
C are positive definite. The only trajectory that can stay indefinitely in
the zero-dissipation set v=0 is x=0: otherwise the restoring force immediately
changes velocity. Therefore a nonzero unforced periodic orbit cannot persist.
Integrating dE/dt over a hypothetical period would require zero loss throughout
that period, which reduces to the resting solution. This conclusion follows
from the force law; a longer simulation cannot turn this passive model into an
attracting, sustained breathing cycle.

The normal coordinates q+=(x0+x1)/sqrt(2) and q-=(x0-x1)/sqrt(2) diagonalize
both matrices. Their stiffnesses are ka and ka+2kl, and their damping
coefficients are ca and ca+2cl. The baseline values m=1 kg, ka=4 N/m,
kl=2 N/m, ca=0.1 N s/m and cl=0.2 N s/m give displacement envelope factors
exp(-0.05 t) and exp(-0.25 t), with t in seconds and rates in inverse seconds.
Both modes are underdamped. Their damped
angular frequencies are sqrt(4-0.05^2) and sqrt(8-0.25^2) rad/s.

For either mode, with cutoff displacement q0 and velocity u0, elapsed time s
after input-off, gamma=c/(2m), and wd=sqrt(k/m-gamma^2):

```
q(s) = exp(-gamma*s) * [q0*cos(wd*s)
                      + (u0+gamma*q0)/wd * sin(wd*s)]
```

Differentiating this expression gives the independent velocity reference.
The cutoff state must be evolved through the driven segment first. Setting
force to zero leaves x and v continuous; it does not erase previously stored
energy or reset the cumulative work ledger.

## What would change the conclusion

- Removing all damping permits conservative oscillation from initial stored
  energy. It supplies neither an attracting cycle nor energy from elapsed time.
- Setting only ca=0 with cl>0 leaves the symmetric mode undamped, because the
  link sees no relative velocity in that mode. This changes the stability
  assumptions and must be recorded as a different model.
- A periodic force can maintain a driven response by replacing the dissipated
  energy. Its waveform is an input, so its frequency alone is not evidence of
  spontaneously selected breathing.
- An active feedback or environmental reservoir may support a sustained cycle.
  That requires explicit coupling, reservoir energy and saturation laws, with
  work exchange tracked. The present model does not contain those mechanisms.

The next useful question is which specified material/geometry/reservoir model
produces a desired mode, and under which controls it stops. Whole-structure
folding, finite-thickness contact and recursive exchange remain separate checks.
Neither a successful checkpoint replay nor this passive-limit result closes
those tasks.
