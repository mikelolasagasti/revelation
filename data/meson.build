subdir('icons')

# Compile the resources
resource_data = files(
  'ui/help-overlay.ui',
  'ui/menubar.ui',
  'ui/popup-tree.ui',
  'ui/password-generator.ui',
)

gnome.compile_resources(
  rvl_name,
  rvl_name + '.gresource.xml',
  gresource_bundle: true,
  source_dir: meson.current_build_dir(),
  install_dir: rvl_pkgdatadir,
  install: true,
  dependencies: resource_data,
)

# Install the schema file
install_data(
  rvl_namespace + '.gschema.xml',
  install_dir: join_paths(rvl_datadir, 'glib-2.0', 'schemas')
)

# Install the mime file
install_data(
  rvl_name + '.xml',
  install_dir: join_paths(rvl_datadir, 'mime', 'packages')
)

# Merge the translations with the desktop file
desktop_conf = configuration_data()
desktop_conf.set('icon', rvl_namespace)
i18n.merge_file(
  type: 'desktop',
  input: configure_file(
    output: rvl_namespace + '.desktop.in',
    input: rvl_namespace + '.desktop.in.in',
    configuration: desktop_conf),
  output: rvl_namespace + '.desktop',
  po_dir: join_paths(meson.source_root(), 'po'),
  install: true,
  install_dir: join_paths(rvl_datadir, 'applications')
)

# Validate the desktop file
desktop_file_validate = find_program('desktop-file-validate', required:false)
if desktop_file_validate.found()
  test (
    'Validate desktop file',
    desktop_file_validate,
    args: join_paths(meson.current_build_dir (), rvl_namespace + '.desktop')
  )
endif

metainfo = rvl_namespace + '.metainfo.xml'
rvl_appstreamdir = join_paths(rvl_datadir, 'metainfo')

# Merge the translations with the MetaInfo file
i18n.merge_file(
  input: metainfo + '.in',
  output: metainfo,
  po_dir: join_paths(meson.source_root(), 'po'),
  install: true,
  install_dir: rvl_appstreamdir,
)

# Validate the MetaInfo file
appstream_util = find_program('appstream-util', required: false)
if appstream_util.found()
  test (
    'Validate MetaInfo file',
    appstream_util,
    args: ['validate-relax', join_paths(meson.current_build_dir (),
                                        rvl_namespace + '.metainfo.xml')]
  )
endif
