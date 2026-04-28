{ pkgs }: {
    deps = [
        pkgs.ffmpeg
        pkgs.python39      # Меняем python311 на python39 (рабочая версия)
        pkgs.python39Packages.pip
        pkgs.python39Packages.virtualenv
    ];
}