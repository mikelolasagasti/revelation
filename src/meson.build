install_data(
  'revelation.py',
  rename: 'revelation',
  install_mode: 'rwxr-xr-x',
  install_dir: bindir,
)

install_subdir(
  'lib',
  install_dir: libdir,
  strip_directory: true,
  exclude_files: ['Makefile.am', 'Makefile.in',
                  'datahandler/Makefile.am', 'datahandler/Makefile.in',
                  'config.py.in']
)

config_conf = configuration_data()
config_conf.set('pkgdatadir', rvl_pkgdatadir)
config_conf.set('datadir', rvl_datadir)
config_conf.set('PACKAGE', rvl_name)
config_conf.set('VERSION', rvl_version)

configure_file(
  input: 'lib/config.py.in',
  output: 'config.py',
  install: true,
  install_dir: libdir,
  configuration: config_conf,
)
