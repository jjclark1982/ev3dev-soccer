# ev3dev-soccer

Currently this program has one mode: `align_shot`.
It uses the seeker, gyro, and color sensor to get behind the ball, as in [this scratch simulation](https://scratch.mit.edu/projects/239417866/#fullscreen).

### Installation

Assemble an EV3 robot with left and right motors plugged into ports B and C. Sensors can be plugged into any ports.

Install [ev3dev](https://www.ev3dev.org/) on a microSD card and boot the robot from it.
Connect to the robot by bluetooth and copy these files into the home directory.

    scp *.* robot@ev3dev.local:

Run `mv python.nanorc .nanorc` to set up editing for Python syntax.

### Usage

Run the main program:

    python3 reloader.py
    
[`reloader.py`](./reloader.py) monitors [`main.py`](./main.py) for changes and automatically reloads it.
If you run this in a terminal you will see sensor readings print several times per second.
If you run it from the brick menu, the output will be logged to a file.

Edit the source code in a separate terminal:

    nano main.py
    
[`main.py`](./main.py) defines the `start()`, `stop()`, and `update()` functions that make up the robot's behavior.
