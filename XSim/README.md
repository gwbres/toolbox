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
    ...
    bench.runCLI()
    ...
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
