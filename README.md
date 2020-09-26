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

To build revelation first `cd` to a suitable location and run:

```bash
git clone https://github.com/mikelolasagasti/revelation.git
```

Navigate to the directory where revelation source has been downloaded
and type these commands:

```
cd revelation
./autogen.sh
./configure #by default it will be /usr/local
make
sudo make install
```

[revelation-logo]: data/icons/scalable/info.olasagasti.revelation.svg
[GNOME 3 desktop]: https://www.gnome.org
