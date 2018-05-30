### Test bench object

The XSimBench object is a test bench descriptor, it is made of 
three types of variables:

* attributes: like libraries, language etc..
* parameters: simulation parameters
* stimuli: a list of stimulus (test signals)

Bench object is either built from a list of dictionnaries, or from a file:

```python
    params = [{'type': 'attribute'}, 'lang': 'vhdl'},]
    params.append({
        'type': 'attribute',
        'library': ('ieee', 'std_logic_1164')
    })
```

```python


```