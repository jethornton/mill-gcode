==========
Installing
==========

Mill G code Generator

1. Install required dependencies. In a terminal do:
::

    sudo apt install python3-pip python3-pyqt5 libpci-dev git

2. Install the Mill G code Generator. In a terminal do:
::

    pip install git+https://github.com/jethornton/mill-gcode.git

3. Create a file in your home directory called ``.xsessionrc`` and add the
following if your using Debian 9 then log out and back in or reboot the PC.

::

  if [ -d $HOME/.local/bin ]; then
    export PATH="$HOME/.local/bin:$PATH"
  fi

4. Run the Mill G code Generator. In a terminal do:
::

    mill-gcode


To upgrade the Mill G code Generator. In a terminal do:
::

    pip3 install git+https://github.com/jethornton/mill-gcode.git --upgrade


To uninstall the Mill G code Generator In a terminal do:
::

    pip uninstall mill-gcode

