# Swaysnex: smart split and execute command in Sway

A script for those who always confuse split modes in [Sway](https://swaywm.org).

Every time you open a new console window, you have to set the correct split
mode: vertical or horizontal. Every time I make the wrong choice. I give up.
I just want to split the current window in a simple way: a narrow window should
be split vertically, a wide window - horizontally. Or vice versa, I always
confuse them.

So, let the script decide which mode to activate based on the geometry of the
current window:

```
        ╒═══╕    ╒═══╕
        │   │    │   │        ╒═══════════╕    ╒═════╤═════╕
        │   │ => ╞═══╡        │           │ => │     │     │
        │   │    │   │        └───────────┘    └─────┴─────┘
        └───┘    └───┘
```

The script gets the window size and starts executing applications using Sway
IPC.

The script is written in Python and uses only standard libraries.

## Usage

You can run the script manually from the command line:
```
swaysnex.py [-r] [PROGRAM [ARGS...]]
```
The `-r` flag reverses the split mode algorithm. If no program is specified,
only the correct split mode will be set.

I would recommend adding the following bindings to the Sway configuration file
(example with launching the [Alacritty](https://github.com/alacritty/alacritty)
terminal):
```
bindsym {
  $mod+Return       exec "/path/to/swaysnex.py alacritty"
  $mod+Shift+Return exec "/path/to/swaysnex.py -r alacritty"
}
```
