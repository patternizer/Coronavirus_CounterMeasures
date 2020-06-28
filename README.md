![image](https://github.com/patternizer/Coronavirus_CounterMeasures/blob/master/countermeasures_video.gif)

# Coronavirus_CounterMeasures

Plotly Dash Python visualisation of global daily national and US state level interventions to stem the spread of SARS-COV-2.
The code reads in the daily update data provided by Olivier Lejeune: https://github.com/OlivierLej/Coronavirus_CounterMeasures.
A drop-down menu allows access to previous days' plots.

An online app is daily updated at: https://patternizer-covid19.herokuapp.com/

## Contents

* `countermeasures_app.py` - main script to be run with Python 3.6+
* `countermeasures_video.py` - script to generate daily global status maps and generate animated GIF loop

The first step is to clone the latest Coronavirus_CounterMeasures code and step into the check out directory: 

    $ git clone https://github.com/patternizer/Coronavirus_CounterMeasures.git
    $ cd Coronavirus_CounterMeasures
    
### Using Standard Python 

The code should run with the [standard CPython](https://www.python.org/downloads/) installation and was tested 
in a conda virtual environment running a 64-bit version of Python 3.6+.

Coronavirus_CounterMeasures can be run from sources directly, once the following module requirements.txt are resolved.

Run a static version at localhost with:

    $ python countermeasures_app.py

To generate an animated GIF of daily maps to date run:

    $ python countermeasures_video.py
	        
## License

The code is distributed under terms and conditions of the [MIT license](https://opensource.org/licenses/MIT).

## Contact information

* [Michael Taylor](https://patternizer.github.io)

