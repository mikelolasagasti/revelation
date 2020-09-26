# Application icons
apps_icons = [
  ['16x16', 'info.olasagasti.revelation.png'],
  ['24x24', 'info.olasagasti.revelation.png'],
  ['32x32', 'info.olasagasti.revelation.png'],
  ['48x48', 'info.olasagasti.revelation.png'],
  ['128x128', 'info.olasagasti.revelation.png'],
  ['256x256', 'info.olasagasti.revelation.png'],
  ['scalable', 'info.olasagasti.revelation.svg'],
]

foreach icon: apps_icons
  install_data(
    join_paths(icon[0], icon[1]),
    install_dir: join_paths(rvl_datadir, 'icons', 'hicolor', icon[0], 'apps'),
  )
endforeach

# Mime icons
install_data(
  join_paths('48x48', 'gnome-mime-application-x-revelation.png'),
  install_dir: join_paths(rvl_pkgdatadir, 'icons', 'hicolor', '48x48', 'mimetypes'),
)

# Actions icons
actions = [
  'document-export.svg',
  'document-import.svg',
  'object-locked.svg',
  'password-change.svg',
  'password-check.svg',
  'password-generate.svg',
]

foreach action: actions
  install_data(
    join_paths('scalable', action),
    install_dir: join_paths(rvl_pkgdatadir, 'icons', 'hicolor', 'scalable', 'actions'),
  )
endforeach
