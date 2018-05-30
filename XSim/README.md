### Test bench object

The XSimBench object is a test bench descriptor, it is made of 
three types of variables:

* attributes: like libraries, language etc..
* parameters: simulation parameters
* stimuli: a list of stimulus (test signals)

Bench object is built from a list of dictionnaries:

```python
    params = [{'type': 'attribute'}, 'lang': 'vhdl'},]
    params.append({
        'type': 'attribute',
        'library': ('ieee', 'std_logic_1164')
    })
    ...
    
    bench = XSimBench(params)
    ...
```

It is possible then possible to build a simulation object
from a previously dumped dictionnary:

```python
    fd = open('dump.json', 'r')
    content = fd.read()
    fd.close()
    bench = XSimBench(eval(content))
```

which is quite handy to create default environment setups.

It is possible to create the dictionnary dump directly from a valid XSimBench object:

```python
    bench = XSimBench(params)
    fd = open('dump.json', 'w')
    fd.write(str(bench))
    fd.close()
```

#### Simulation parameters

Several types of parameters are available:

```python

    params.append({
        'type': 'parameter',
        'ptype': 'float',
        'key': 'sample_rate',
        'value: 100E6
    })
    
    params.append({
        'type': 'parameter',
        'ptype': 'bool',
        'key': 'use_tlast',
        'value: 1,
        'help': 'Activate TLAST'
    })
```

The command line interface allows to modify simulation parameters on the fly:

```python
    bench.runCLI()
```

Optionnal information is passed to the CLI by adding an 'help' value to a simulation parameter:

```python
    params.append({
        'type': 'string',
        'ptype': 'bool',
        'key': 'use_tlast',
        'value: 1,
        'help': 'Activate TLAST'
    })
```

Fixed point numbers can be used:

```python
    params.append({
        'type': 'parameter',
        'ptype': 'fixed_point',
        'key': 'data_in',
        'value': 's24.20,
        'help': 'Input data'
    })
```

Simulations parameters range can be constrained:

* maximum number of bits for fixed point numbers
* range [a:b] for integers: use '-inf' and '+inf' for maximum range
* same thing for floating point numbers

#### Signal generation

Several stimulus can be generated:
* sine waves
* square waves
* ramp signal

The test bench will run through all stimuli by insertion order:

#### Sine waves

Signal model is:

$$
s(t) = a_0 \left(1+\frac{\alpha(t)}{m}\right) \sin \left(2 \pi f \left(1+\frac{\beta(t)}{m}\right)t + \phi(t) \left(1+\frac{\Omega(t)}{m}\right)\right) + \gamma(t)
$$

where

$$
    \gamma(t) = \displaystyle{\sum_{n=0}^{M-1} \gamma_i(t)}
$$

represents all noise processes, 

&alpha;(t) is the AM modulation, &beta;(t) is the FM modulation and &Omega;(t) is the PM modulation


```python
...
    params.append({
        'type': 'stimulus',
        'stype': 'sinewave':
        'amplitude': 1.0,
        'frequency': 10e6,
        'n-symbols': 1000
    })
```

It is possible to add more options to the stimulus using an *option* subdictionnary:

```python
    params.append({
        'type': 'stimulus',
        'stype': 'sinewave',
        'amplitude': 1.0,
        'frequency: 25e6,
        'n-symbols': 128,
        'options': {
            'addnoise': {'type': 'white', 'density': -180},
            'AM-Tone': {'freq': 10e3, 'power': -10},
        },
    })
```

Modulation tones are specific to sine waves. Power is expressed in [dBc]. Added noise processes
are possible for all available types of stimulus.

#### Square waves

```python
...
    params.append({
        'type': 'stimulus',
        'stype': 'squarewave',
        'amplitude': 1.0,
        'n-cycles': 10,
        'n-symbols': 512,
        'options': {
            'addnoise': {'type': 'pink', 'density': -120},
            'duty': 0.25
        },
    })
...
```

n-cycles is the number of periods in the total stimulus. 
'Duty=0.25' is an optionnal 25% duty cycle (50% is the default value).

#### Ramps

```python
...
    params.append({
        'type': 'stimulus',
        'stype': 'ramp',
        'amplitude': 0.5,
        'n-cycles': 10,
        'n-symbols': 1024,
        'options': {
            'down': True
        },
    })
...
```
