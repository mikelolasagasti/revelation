# ![revelation-logo] Revelation

Revelation is a simple password manager for the [GNOME 3 desktop],
released under the GNU GPL license.

It stores accounts and passwords in a single, secure place, and gives
access to them through a user-friendly graphical interface.

The project website is located at https://revelation.olasagasti.info.

## Install

- Fedora

```bash
dnf install revelation
```

- Flatpak

```bash
flatpak install flathub info.olasagasti.revelation
```

## Build

Revelation depends on the following software:

- GTK3-3.22
- PyGObject
- Python 3 (currently working on Python 3.7)
- pycryptodomex
- libpwquality

Additional packages required on Ubuntu 22.04: `gobject-introspection`, `libgirepository1.0-dev`

To build revelation first `cd` to a suitable location and run:

```bash
git clone https://github.com/mikelolasagasti/revelation.git
```

### Build with Meson

Navigate to the directory where revelation source has been downloaded
and type these commands:

```sh
$ cd revelation
$ meson setup --prefix=$HOME/.local _build
$ meson install -C _build
```

Meson will build revelation in the `_build` directory, and install it in
`.local` in your home directory, which is the best option for local installs in
Debian or Ubuntu systems.

You can choose whatever prefix you like, like `--prefix=$HOME/install`, but
because the installation directory may be non-standard, to run revelation you
will have to define some environment variables. In this example:

```sh
$ export XDG_DATA_DIRS=$HOME/install/share:$XDG_DATA_DIRS
$ export PYTHONPATH=$HOME/install/lib/python3.8/site-packages
```

and then run revelation:
```
$ $HOME/.local/bin/revelation
```

[revelation-logo]: data/icons/scalable/info.olasagasti.revelation.svg
[GNOME 3 desktop]: https://www.gnome.org
