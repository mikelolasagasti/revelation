project('revelation',
    version : '0.5.6',
    meson_version: '>= 0.51.0'
)

# Importing modules
gnome = import('gnome')
i18n = import('i18n')
python = import('python')

# Module objects
py_installation = python.find_installation('python3',
  modules: ['Cryptodome',
            'pwquality'] )

# Dependencies
dependency('gobject-introspection-1.0', version: '>= 1.35.0')
dependency('gtk+-3.0', version: '>= 3.22')
dependency('glib-2.0')
dependency('pygobject-3.0', version: '>= 3.29.1')

rvl_name = meson.project_name().to_lower()
rvl_namespace = 'info.olasagasti.revelation'
rvl_datadir = join_paths(get_option('prefix'), get_option('datadir'))
rvl_appstreamdir = join_paths(rvl_datadir, 'metainfo')
rvl_pkgdatadir = join_paths(rvl_datadir, rvl_name)
rvl_version = meson.project_version()

bindir = join_paths(get_option('prefix'), get_option('bindir'))
libdir = join_paths(py_installation.get_install_dir(), rvl_name)

subdir('src')
subdir('data')
subdir('po')

meson.add_install_script('meson_post_install.py')

output = '\n' + meson.project_name() + ' ' + rvl_version + ' configure summary\n'
output += '============================\n\n'
output += 'pythondir.: ' + libdir + '\n'
output += 'bindir....: ' + bindir + '\n'
output += 'datadir...: ' + rvl_datadir + '\n'
output += 'pkgdatadir: ' + rvl_pkgdatadir
message(output)

