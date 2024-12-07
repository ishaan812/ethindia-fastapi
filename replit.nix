{pkgs}: {
  deps = [
    pkgs.glibcLocales
    pkgs.libxcrypt
    pkgs.borgbackup
    pkgs.libuv
    pkgs.rustc
    pkgs.libiconv
    pkgs.cargo
    pkgs.cacert
  ];
}
