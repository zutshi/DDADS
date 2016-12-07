#DDADS
Data Driven Analysis of Dynamical Systems

Using only trajectories/traces/runs of a dynamical system, we comment
about reachability and other properties.

##Current Status: [Partial Implementation]
- SAL + YICES are required as they are the only working BMC engine.

##Installation
Clone the repository and install the dependencies.

Python modules available on PyPI (Python Package Index) can be installed using the Makefile

    sudo make install

External Dependencies can be installed as required. Refer to the below section.

##Dependencies

- py_utils
    Clone the below repo and add it to the Python Path environment variable: PYTHONPATH

    ```
    https://github.com/zutshi/pyutils.git
    ```

- Graph Library (two options)
    1. Networkx
        - Slower
        - Gets installed using make
    2. graph-tool-2.13
        - Faster
        - Warning: Takes a few hours to compile (and painful to install)
        - Partial integration. Instead of K-shortest paths, All-shortest paths are being computed!
        - Needs Boost >= 1.60 [set environment variable BOOST_ROOT - not working]
            - Install using `./configure .... `
            - set `LD_LIBRARY_PATH LD_LIBRARY_PATH+=:../boost-1.60.0/lib/`

- BMC engine (two options)
    1. SAL
        - Download and install SAL: http://sal.csl.sri.com/
        - set environment variable SAL_PATH to point to the installation
        ```
        export SAL_PATH='<path>/sal-3.3/'
        ```
        - Yices2 [Performs better than Yices]
            - Download and install Yices2: http://yices.csl.sri.com/

    2. S3CAMSMT [**under development**]
    
        ```
        https://github.com/cuplv/S3CAMSMT.git
        ```

##Usage

**Print List of Options**
    
    python ./ddads.py --help

####Example runs


**Reproducible output using seeds:**
S3CAMR is random in nature. It's output can be made reproducible by using the same seed passed using the switch.

    --seed <integer>


##Common Issues

- PyGObject related issues

    **Reason**: Missing GTK3 libraries
    
    **Details**: S3CAMR uses Matplotlib as one of the optional plotting lib. It also uses graph-tool as an optional graph lib. Matplotlib by default (at least on Ubuntu 12.04-14.04) uses Qt4Agg as its backend which uses GTK by default. graph-tool on the other hand uses GTK3 as its backend. As both GTK2 and GTK3 are not compatible we switch Matplotlib's backend to GTK3Agg (plotMP.py).
    
    **Solutions**: 
    - If not using graph-tool, simply uncomment the line `matplotlib.use('GTK3Agg')` in plotMP.py
    - Otherwise, either switch Matplotlib's backend to something else than GTK2/3 or install GTK3 [suggestions for Ubuntu only!].

            sudo apt-get install python-gobject python-gi
            sudo apt-get install libgtk-3-dev
    
    **Refer**: 
    -   https://git.skewed.de/count0/graph-tool/issues/98
    -   http://matplotlib.org/faq/usage_faq.html
