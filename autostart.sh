#!/bin/sh
# Autostart for Qtile Configuration
#
# Set screen resolution according to kanshi to double DPI scale
dbus-update-activation-environment --systemd WAYLAND_DISPLAY XDG_CURRENT_DESKTOP
kanshi &
playerctld daemon &
swaync &
swww init &
wlsunset -l 49.8 -L 97.1 &
wl-mpris-idle-inhibit &
swayidle -w timeout 300 'swaylock -f -c 000000' timeout 600 'swaymsg "output * dpms off"' resume 'swaymsg "output * dpms on"' before-sleep 'swaylock -f -c 000000' &
easyeffects --gapplication-service &
