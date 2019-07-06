==========
Installing
==========

Mill G code Generator

1. Install the Mill G code Generator. In a terminal do:
::

    pip install git+https://github.com/jethornton/mill-gcode.git

2. Run the Mill G code Generator. In a terminal do:
::

    mill-gcode
    
3. If you get `mill-gcode: command not found' create a file in your home
directory called ``.xsessionrc`` and add the following.
::

  if [ -d $HOME/.local/bin ]; then
    export PATH="$HOME/.local/bin:$PATH"
  fi

Log out and back in or reboot the PC.

To upgrade the Mill G code Generator. In a terminal do:
::

    pip3 install git+https://github.com/jethornton/mill-gcode.git --upgrade


To uninstall the Mill G code Generator In a terminal do:
::

    pip uninstall mill-gcode

