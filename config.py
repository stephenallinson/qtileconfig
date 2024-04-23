import os
import subprocess
import re
import json
import random
import journaling.main as journal
from datetime import datetime
from zoneinfo import ZoneInfo
from libqtile import hook
from libqtile import qtile
from libqtile import bar, layout, widget
from qtile_extras.widget import StatusNotifier
from qtile_extras.popup.toolkit import PopupGridLayout, PopupText
from libqtile.config import Click, Drag, Group, Key, Match, Screen, ScratchPad, DropDown
from libqtile.lazy import lazy
from pathlib import Path
from libqtile.backend import base
from libqtile.backend.wayland.inputs import InputConfig

# Set environment variables to ensure applications utilize correct settings
os.environ["XDG_SESSION_DESKTOP"] = "qtile"
os.environ["XDG_CURRENT_DESKTOP"] = "qtile"

# Set home directory
home = str(Path.home())

# Set SUPER key to mod variable
mod = "mod4"
alt = "mod1"
ctrl = "control"
shift = "shift"

# Set default apps
terminal = "alacritty"
browser = "firefox"
explorer = "thunar"
lock = "swaylock"
vol = "amixer"
brightness = "brightnessctl"
media = "playerctl"
app_launcher = "rofi"


# Custom Functions


def show_journal_ideas(qtile):
    controls = [
        PopupText(
            row=0,
            col=0,
            can_focus=True,
            background="#1C1B1A",
            highlight="#1C1B1A",
            highlight_radius=0,
            background_highlighted="#282726",
            foreground=Color4,
            foreground_highlighted=Color5,
            font="JetBrainsMono NFP",
            fontsize=14,
            h_align="left",
            text=journal.journal_prompt(random.randint(0, 4)),
        )
    ]
    layout = PopupGridLayout(
        qtile,
        controls=controls,
        border=Color3,
        border_width=1,
        height=575,
        width=600,
        keyboard_navigation=False,
        cols=1,
        rows=1,
        initial_focus=None,
    )
    layout.show(centered=True)


def show_clocks(qtile):
    time_display = []
    timezones = {
        "Pacific": "America/Los_Angeles",
        "Mountain": "America/Denver",
        "Central": "America/Winnipeg",
        "Eastern": "America/New_York",
        "Germany": "Europe/Berlin",
        "New Zealand": "Pacific/Auckland",
    }
    for index, (k, v) in enumerate(timezones.items()):
        time_display.append(
            PopupText(
                row=0,
                col=index,
                can_focus=True,
                background="#1C1B1A",
                highlight="#1C1B1A",
                highlight_radius=0,
                background_highlighted="#282726",
                foreground=Color4,
                foreground_highlighted=Color5,
                font="JetBrainsMono NFP",
                fontsize=20,
                h_align="left",
                text=f"{k}\n------------\n{datetime.now(ZoneInfo(v)).strftime('%Y-%m-%d')}\n{datetime.now(ZoneInfo(v)).strftime('%H:%M:%S')}",
            )
        )

    layout = PopupGridLayout(
        qtile,
        border=Color3,
        border_width=1,
        height=175,
        width=1000,
        keyboard_navigation=False,
        cols=len(timezones.items()),
        rows=1,
        controls=time_display,
        initial_focus=None,
    )
    layout.show(centered=True)


@lazy.group.function
def cycle_windows(group, forwards=True):
    current = group.current_window
    if current:
        current.change_layer()

        if forwards:
            group.next_window()
        else:
            group.previous_window()

    current = group.current_window
    if current:
        current.bring_to_front()


@lazy.function
def window_to_prev_group(qtile):
    i = qtile.groups.index(qtile.current_group)
    if qtile.current_window is not None and i != 0:
        qtile.current_window.togroup(qtile.groups[i - 1].name)
        qtile.current_screen.prev_group()


@lazy.function
def window_to_next_group(qtile):
    i = qtile.groups.index(qtile.current_group)
    if qtile.current_window is not None and i != 6:
        qtile.current_window.togroup(qtile.groups[i + 1].name)
        qtile.current_screen.next_group()


@lazy.function
def float_to_front(qtile):
    """Bring all floating windows of the group to front"""
    for window in qtile.current_group.windows:
        if window.floating:
            window.bring_to_front()


keys = [
    # Media Controls (yay -S alsa-utils brightnessctl playerctl)
    Key(
        [],
        "XF86AudioMute",
        lazy.spawn(f"{vol} -q sset Master toggle"),
        desc="Mute/Unmute Media",
    ),
    Key(
        [],
        "XF86AudioLowerVolume",
        lazy.spawn(f"{vol} -q sset Master,0 3%-"),
        desc="Lower Volume by 3%",
    ),
    Key(
        [],
        "XF86AudioRaiseVolume",
        lazy.spawn(f"{vol} -q sset Master,0 3%+"),
        desc="Increase Voume by 3%",
    ),
    Key(
        [],
        "XF86AudioMicMute",
        lazy.spawn(f"{vol} -q sset 'Capture' toggle"),
        desc="Mute/Unmute Microphone",
    ),
    Key(
        [],
        "XF86MonBrightnessUp",
        lazy.spawn(f"{brightness} set +10%"),
        desc="Increase Brightness by 10%",
    ),
    Key(
        [],
        "XF86MonBrightnessDown",
        lazy.spawn(f"{brightness} set 10%-"),
        desc="Decrease Brightness by 10%",
    ),
    Key(
        [], "XF86AudioPlay", lazy.spawn(f"{media} play-pause"), desc="Play/Pause Media"
    ),
    Key([], "XF86AudioNext", lazy.spawn(f"{media} next"), desc="Play Next Media"),
    Key(
        [], "XF86AudioPrev", lazy.spawn(f"{media} previous"), desc="Play Previous Media"
    ),
    # Switch between windows
    Key([mod], "Left", lazy.layout.left(), desc="Move focus to left"),
    Key([mod], "Right", lazy.layout.right(), desc="Move focus to right"),
    Key([mod], "Down", lazy.layout.down(), desc="Move focus down"),
    Key([mod], "Up", lazy.layout.up(), desc="Move focus up"),
    # Move windows between left/right columns or move up/down in current stack.
    Key(
        [mod, shift], "Left", lazy.layout.shuffle_left(), desc="Move window to the left"
    ),
    Key(
        [mod, shift],
        "Right",
        lazy.layout.shuffle_right(),
        desc="Move window to the right",
    ),
    Key([mod, shift], "Down", lazy.layout.shuffle_down(), desc="Move window down"),
    Key([mod, shift], "Up", lazy.layout.shuffle_up(), desc="Move window up"),
    # Grow windows.
    Key([mod, ctrl], "Down", lazy.layout.shrink(), desc="Shrink window"),
    Key([mod, ctrl], "Up", lazy.layout.grow(), desc="Grow window"),
    # Cycle Windows
    Key([mod, shift], "Tab", cycle_windows(), desc="Cycle through windows"),
    # App Launcher
    Key([mod], "Return", lazy.spawn(terminal), desc="Launch terminal"),
    Key([mod], "g", lazy.spawn(browser), desc="Launch browser"),
    Key([mod], "e", lazy.spawn(explorer), desc="Launch File Explorer"),
    Key([mod], "r", lazy.spawncmd(), desc="Spawn a command using a prompt widget"),
    Key(
        [mod], "space", lazy.spawn(f"{home}/scripts/applauncher.sh"), desc="Launch rofi"
    ),
    Key(
        [mod],
        "t",
        lazy.spawn(f"{home}/scripts/controlcenter.sh"),
        desc="Launch notification center",
    ),
    # Kill Window with SUPER+q
    Key([mod], "q", lazy.window.kill(), desc="Kill focused window"),
    # Reload the config and then apply themes
    Key(
        [mod, ctrl],
        "r",
        lazy.spawn(f"{home}/scripts/updatewal.sh"),
        desc="Reload the config",
    ),
    Key(
        [mod, ctrl, shift], "q", lazy.shutdown(), desc="Shutdown QTile"
    ),  # Same as logout
    # Screenshots
    Key(
        [mod, shift],
        "s",
        lazy.spawn(f"{home}/scripts/screenshot.sh"),
        desc="Take screenshot of area and save to Pictures",
    ),
    # Fullscreen & Floating
    Key(
        [mod], "f", lazy.window.toggle_fullscreen(), desc="Toggle window to Full Screen"
    ),
    Key(
        [mod, ctrl],
        "f",
        lazy.window.toggle_floating(),
        desc="Toggle Window Floating Mode",
    ),
    # Lock Screen
    Key([mod], "l", lazy.spawn(lock), desc="Lock Computer"),
    # Tree Tab Key Bindings
    Key(
        [mod, shift],
        "j",
        lazy.layout.shuffle_down(),
        lazy.layout.section_down().when(layout=["treetab"]),
        desc="Move window down/move down a section in treetab",
    ),
    Key(
        [mod, shift],
        "k",
        lazy.layout.shuffle_up(),
        lazy.layout.section_up().when(layout=["treetab"]),
        desc="Move window downup/move up a section in treetab",
    ),
    # Bring Floating Windows to Front
    Key([mod], "d", lazy.function(float_to_front)),
    # Wallpaper Selector
    Key([mod], "w", lazy.spawn(f"{home}/scripts/wallpaper.sh select")),
    Key(
        [mod, shift],
        "f",
        lazy.window.static(screen=0, x=1353, y=26, width=570, height=321),
        desc="Make window static in upper right corner of Monitor 0",
    ),
]

# ----------------------
# Groups
# ----------------------

groups = [
    # Screen 0
    Group("1", screen_affinity=0, layout="monadtall"),
    Group("2", screen_affinity=0, layout="monadtall"),
    Group("3", screen_affinity=0, layout="monadtall"),
    Group("4", screen_affinity=0, layout="monadtall"),
    Group("5", screen_affinity=0, layout="monadtall"),
    # Screen 1
    Group("11", label="2.1", screen_affinity=1, layout="monadtall"),
    Group("12", label="2.2", screen_affinity=1, layout="monadtall"),
    Group("13", label="2.3", screen_affinity=1, layout="monadtall"),
]


def go_to_group(name: str):
    def _inner(qtile):
        if len(qtile.screens) == 1:
            qtile.groups_map[name].toscreen()
            return

        if name in "12345":
            qtile.focus_screen(0)
            qtile.groups_map[name].toscreen()
        else:
            qtile.focus_screen(1)
            qtile.groups_map[name].toscreen()

    return _inner


def go_to_group_and_move_window(name: str):
    def _inner(qtile):
        if len(qtile.screens) == 1:
            qtile.current_window.togroup(name, switch_group=True)
            return

        if name in "12345":
            qtile.current_window.togroup(name, switch_group=False)
            qtile.focus_screen(0)
            qtile.groups_map[name].toscreen()
        else:
            qtile.current_window.togroup(name, switch_group=False)
            qtile.focus_screen(1)
            qtile.groups_map[name].toscreen()

    return _inner


keys.extend(
    [
        # Control Groups on Screen 0
        Key([mod], "1", lazy.function(go_to_group("1"))),
        Key([mod], "2", lazy.function(go_to_group("2"))),
        Key([mod], "3", lazy.function(go_to_group("3"))),
        Key([mod], "4", lazy.function(go_to_group("4"))),
        Key([mod], "5", lazy.function(go_to_group("5"))),
        # Control Groups on Screen 1
        Key([mod, ctrl], "1", lazy.function(go_to_group("11"))),
        Key([mod, ctrl], "2", lazy.function(go_to_group("12"))),
        Key([mod, ctrl], "3", lazy.function(go_to_group("13"))),
        # Group Management
        Key(
            [mod],
            "Tab",
            lazy.screen.toggle_group(),
            desc="Switch between last used Group",
        ),
        Key(
            [mod, shift],
            "Page_Up",
            window_to_next_group(),
            desc="Move window to next Group",
        ),
        Key(
            [mod, shift],
            "Page_Down",
            window_to_prev_group(),
            desc="Move window to previous Group",
        ),
    ]
)


# -----------------------
# Scratchpads
# -----------------------

groups.append(
    ScratchPad(
        "6",
        [
            DropDown(
                "dynalist",
                "chromium --app=https://dynalist.io",
                x=0.3,
                y=0.1,
                width=0.40,
                height=0.80,
                on_focus_lost_hide=False,
            ),
            DropDown(
                "chatgpt",
                "brave --app=https://chat.openai.com",
                x=0.3,
                y=0.1,
                width=0.40,
                height=0.80,
                on_focus_lost_hide=False,
            ),
            DropDown(
                "spotify",
                f"{terminal} -e ncspot",
                x=0.3,
                y=0.1,
                width=0.40,
                height=0.40,
                on_focus_lost_hide=True,
            ),
            DropDown(
                "btop",
                f"{terminal} -e btop",
                x=0.3,
                y=0.1,
                width=0.40,
                height=0.45,
                on_focus_lost_hide=True,
            ),
            DropDown(
                "calendar",
                f"{terminal} -e calcurse",
                x=0.3,
                y=0.1,
                width=0.40,
                height=0.80,
                on_focus_lost_hide=True,
            ),
            DropDown(
                "whiteboard",
                "lorien",
                x=0.1,
                y=0.1,
                width=0.80,
                height=0.80,
                on_focus_lost_hide=False,
            ),
        ],
    )
)

keys.extend(
    [
        Key([mod], "F5", lazy.group["6"].dropdown_toggle("chatgpt")),
        Key([mod], "F6", lazy.group["6"].dropdown_toggle("dynalist")),
        Key([mod], "F9", lazy.group["6"].dropdown_toggle("spotify")),
        Key([mod], "F10", lazy.group["6"].dropdown_toggle("btop")),
        Key([mod], "F11", lazy.group["6"].dropdown_toggle("calendar")),
        Key([mod], "F12", lazy.group["6"].dropdown_toggle("whiteboard")),
    ]
)

# -----------------------
# Colors Configuration
# -----------------------

colors = os.path.expanduser("~/.cache/wal/colors.json")
colordict = json.load(open(colors))
Color0 = colordict["colors"]["color0"]
Color1 = colordict["colors"]["color1"]
Color2 = colordict["colors"]["color2"]
Color3 = colordict["colors"]["color3"]
Color4 = colordict["colors"]["color4"]
Color5 = colordict["colors"]["color5"]
Color6 = colordict["colors"]["color6"]
Color7 = colordict["colors"]["color7"]
Color8 = colordict["colors"]["color8"]
Color9 = colordict["colors"]["color9"]
Color10 = colordict["colors"]["color10"]
Color11 = colordict["colors"]["color11"]
Color12 = colordict["colors"]["color12"]
Color13 = colordict["colors"]["color13"]
Color14 = colordict["colors"]["color14"]
Color15 = colordict["colors"]["color15"]

# --------------------------
# Layout Configuration
# --------------------------


def window_sorter(win):
    patterns = (
        ("Zulip", "MESSAGING"),
        ("Microsoft Teams", "MESSAGING"),
        ("thunderbird", "MESSAGING"),
        ("LibreOffice", "OFFICE"),
        ("Thunderbird", "EMAIL"),
    )
    for k, v in patterns:
        if k in win.name:
            return v
    return "APPS"


keys.extend([Key([alt], "r", lazy.layout.sort_windows(window_sorter))])


layout_theme = {
    "border_width": 1,
    "margin": 3,
    "border_focus": Color2,
    "border_normal": Color3,
    "single_border_width": 1,
}

layouts = [
    layout.Max(**layout_theme),
    layout.MonadTall(**layout_theme),
    layout.MonadWide(**layout_theme),
    layout.TreeTab(
        font="FiraCode Nerd Font",
        fontsize=14,
        sections=["MESSAGING", "EMAIL", "OFFICE", "APPS"],
        section_fontsize=20,
        bg_color="000000",
        active_bg=Color1,
        active_fg="FFFFFF",
        inactive_bg=Color1,
        inactive_fg="AAAAAA",
        padding_y=3,
        section_top=10,
        panel_width=256,
        previous_on_rm=True,
    ),
    # layout.Columns(),
    # layout.Stack(num_stacks=2),
    # layout.Bsp(),
    # layout.Matrix(),
    # layout.RatioTile(),
    # layout.Tile(),
    # layout.VerticalTile(),
    # layout.Zoomy(),
    # layout.Floating()
]

# ------------------
# Widget Defaults
# ------------------

widget_defaults = dict(
    font="JetBrainsMono NFP",
    fontsize=14,
    padding=5,
)
extension_defaults = widget_defaults.copy()

# ----------------------
# Widgets
# ----------------------


widget_list = [
    widget.CurrentLayoutIcon(scale=0.75),
    widget.TextBox(text="|", foreground=Color4),
    widget.GroupBox(
        visible_groups=["1", "2", "3", "4", "5"],
        active="FFFFFF",
        block_highlight_text_color="000000",
        block_border="FFFFFFF",
        foreground="FFFFFF",
        highlight_method="block",
        highlight="FFFFFF",
        highlight_color=["FFFFFFF", "FFFFFF"],
        inactive="808080",
        rounded=False,
        this_current_screen_border="FFFFFF",
        this_screen_border=Color1,
    ),
    widget.TextBox(text="|", foreground=Color4),
    widget.OpenWeather(
        location="Winnipeg",
        format="{icon} {main_temp:.0f} °{units_temperature}",
        mouse_callbacks={
            "Button1": lambda: qtile.cmd_spawn(
                f"{terminal} -e \
                            firefox \
                           --new-tab \
                           'https://openweathermap.org/city/6183235'"
            )
        },
    ),
    widget.TextBox(text="|", foreground=Color4),
    widget.GenPollCommand(
        cmd="/home/stephen/pyproj/calimport/main.py",
        fmt=" {}",
        max_chars=25,
        update_interval=300,
        mouse_callbacks={
            "Button1": lazy.group["6"].dropdown_toggle("calendar"),
            "Button3": lazy.function(show_journal_ideas),
        },
    ),
    widget.TextBox(text="|", foreground=Color4),
    widget.GenPollCommand(
        update_interval=1,
        cmd=f"{home}/scripts/idleinhibit.sh",
        fmt="{}",
        mouse_callbacks={
            "Button1": lambda: qtile.cmd_spawn(
                f"{home}/scripts/idleinhibit.sh toggle",
            ),
        },
    ),
    widget.Spacer(),
    widget.Clock(
        format="%Y-%m-%d | %I:%M %p  ",  # Spacing required
        timezone="US/Central",
        mouse_callbacks={
            "Button1": lambda: qtile.spawn(f"{home}/scripts/controlcenter.sh"),
            "Button2": lazy.group["6"].dropdown_toggle("calendar"),
            "Button3": lazy.function(show_clocks),
        },
    ),
    widget.Spacer(),
    StatusNotifier(
        menu_font="JetBrainsMono Nerd Font Propo",
        menu_foreground="#FFFFFF",
        menu_border=Color1,
    ),
    widget.TextBox(text="|", foreground=Color4),
    widget.CheckUpdates(
        custom_command="checkupdates",
        display_format="󰣇 {updates}",
        update_interval=900,
        no_update_string="󰣇 0",
        mouse_callbacks={"Button1": lazy.spawn(f"{terminal} -e yay")},
    ),
    widget.TextBox(text="|", foreground=Color4),
    widget.Volume(
        fmt="󰕾 {}",
        mouse_callbacks={"Button3": lazy.spawn(f"{home}/scripts/sound-output.sh")},
    ),
    widget.TextBox(text="|", foreground=Color4),
    widget.Bluetooth(
        adapter_format="󰂳 {name} [{powered}{discovery}]",
        device="/dev_A4_C6_F0_C2_30_BD",
        default_text=" {num_connected_devices}",
        device_format="{symbol} {name}",
        symbol_connected="",
        symbol_discovery=("󰂱", ""),
        symbol_paired="󰂲",
        symbol_powered=("⏼", "⭘"),
        hide_unnamed_devices=True,
        mouse_callbacks={"Button1": lazy.spawn(f"{home}/scripts/bluetooth.sh")},
    ),
    widget.TextBox(text="|", foreground=Color4),
    widget.Wlan(
        format=" {percent:2.0%}",
        disconnected_message="󰖪 0%",
        update_interval=30,
        mouse_callbacks={"Button1": lazy.spawn(f"{terminal} -e nmtui")},
    ),
    widget.TextBox(text="|", foreground=Color4),
    widget.CPU(update_interval=15, format=" {load_percent}%"),
    widget.TextBox(text="|", foreground=Color4),
    widget.Memory(measure_mem="G", format=" {MemUsed:.0f}{mm}B"),
    widget.TextBox(text="|", foreground=Color4),
    widget.Battery(
        format="{char} {percent:2.0%}",
        charge_char="󰂄",
        discharge_char="󰂁",
        full_char="󰁹",
        empty_char="X",
        not_charging_char="󰁹",
        notify_below=0.1,
    ),
    widget.TextBox(text="|", foreground=Color4),
    widget.TextBox(
        text="⏻",
        mouse_callbacks={"Button1": lazy.spawn(f"{home}/scripts/powermenu.sh")},
    ),
    widget.TextBox(text="|", foreground=Color4),
]

widget_list_second = [
    widget.CurrentLayoutIcon(scale=0.75),
    widget.Spacer(),
    widget.Clock(format="%Y-%m-%d | %I:%M %p  "),
    widget.Spacer(),
    widget.GroupBox(
        visible_groups=["11", "12", "13"],
        active="FFFFFF",
        block_highlight_text_color="000000",
        block_border="FFFFFFF",
        foreground="FFFFFF",
        highlight_method="block",
        highlight="FFFFFF",
        highlight_color=["FFFFFFF", "FFFFFF"],
        inactive="808080",
        rounded=False,
        this_current_screen_border="FFFFFF",
        this_screen_border=Color1,
    ),
]

# --------------------
# Screen Configuration
# --------------------

screens = [
    Screen(
        top=bar.Bar(
            widget_list,
            24,
            background="#0000008f",
            opacity=0.7,
            border_width=[2, 0, 2, 0],
            margin=[0, 0, 0, 0],
        )
    ),
    Screen(
        top=bar.Bar(
            widget_list_second,
            24,
            opacity=0.7,
            border_width=[2, 0, 2, 0],
            margin=[0, 0, 0, 0],
        ),
    ),
]

# ----------------------
# Mouse Controls
# ----------------------
mouse = [
    Drag(
        [mod],
        "Button1",
        lazy.window.set_position_floating(),
        start=lazy.window.get_position(),
    ),
    Drag(
        [mod], "Button3", lazy.window.set_size_floating(), start=lazy.window.get_size()
    ),
    Click([mod], "Button2", lazy.window.move_to_bottom()),
]

# ------------------
# # General Setting
# ------------------
#
dgroups_key_binder = None
dgroups_app_rules = []  # type: list
follow_mouse_focus = False
bring_front_click = False
cursor_warp = False
auto_fullscreen = True
focus_on_window_activation = "smart"
reconfigure_screens = True

# ------------------------
# Floating Layout Ruleset
# ------------------------

floating_layout = layout.Floating(
    float_rules=[
        # Run the utility of `xprop` to see the wm class an X client.
        *layout.Floating.default_float_rules,
        Match(func=lambda c: c.is_transient_for()),
        Match(wm_class="confirmreset"),  # gitk
        Match(wm_class="makebranch"),  # gitk
        Match(wm_class="maketag"),  # gitk
        Match(wm_class="ssh-askpass"),  # ssh-askpass
        Match(title="branchdialog"),  # gitk
        Match(title="pinentry"),  # GPG key password entry
        Match(title="Picture-in-Picture"),  # Firefox Picture in Picture
        Match(func=base.Window.has_fixed_size),
        Match(func=base.Window.has_fixed_ratio),
        Match(func=lambda c: bool(c.is_transient_for())),
        Match(role="gimp-file-export"),
        Match(title="Bluetooth Devices"),
        Match(title="File Operation Progress", wm_class=re.compile("[Tt]hunar")),
        Match(title="Firefox — Sharing Indicator"),
        Match(title="KDE Connect Daemon"),
        Match(title="Open File"),
        Match(title="Unlock Database - KeePassXC"),
        Match(title="KeePassXC -  Access Request"),
        Match(title=re.compile("Presenting: .*"), wm_class="libreoffice-impress"),
        Match(wm_class="Arandr"),
        Match(wm_class="Dragon"),
        Match(wm_class="Dragon-drag-and-drop"),
        Match(wm_class="Pinentry-gtk-2"),
        Match(wm_class="Xephyr"),
        Match(wm_class="confirm"),
        Match(wm_class="dialog"),
        Match(wm_class="download"),
        Match(wm_class="eog"),
        Match(wm_class="error"),
        Match(wm_class="file_progress"),
        Match(wm_class="imv"),
        Match(wm_class="io.github.celluloid_player.Celluloid"),
        Match(wm_class="lxappearance"),
        Match(wm_class="matplotlib"),
        # Match(wm_class="mpv"),
        Match(wm_class="nm-connection-editor"),
        Match(wm_class="notification"),
        Match(wm_class="org.gnome.clocks"),
        Match(wm_class="org.kde.ark"),
        Match(wm_class="pavucontrol"),
        Match(wm_class="qt5ct"),
        Match(wm_class="ssh-askpass"),
        Match(wm_class="thunar"),
        Match(wm_class="toolbar"),
        Match(wm_class="tridactyl"),
        Match(wm_class="wdisplays"),
        Match(wm_class="wlroots"),
        Match(wm_class="zoom"),
        Match(title=re.compile("^zoom$"), wm_class="Zoom"),
        Match(wm_type="dialog"),
    ]
)

# If things like steam games want to auto-minimize themselves when losing
# focus, should we respect this or not?
auto_minimize = True

# When using the Wayland backend, this can be used to configure input devices.
# wl_input_rules = None
wl_input_rules = {
    "*": InputConfig(
        dwt=True, natural_scroll=True, tap=True, tap_button_map="lrm", drag=True
    ),
    "1133:16500:Logitech G305": InputConfig(
        dwt=False,
        natural_scroll=False,
        drag=True,
        drag_lock=True,
    ),
    "5426:120:Razer Razer Viper": InputConfig(
        dwt=False,
        natural_scroll=False,
        drag=True,
        drag_lock=False,
    ),
    "1578:16642:MOSART Semi. 2.4G Wireless Mouse": InputConfig(
        dwt=False,
        natural_scroll=False,
        drag=True,
        drag_lock=True,
        pointer_accel=-0.3,
    ),
}

wmname = "QTILE"

# HOOK Startup


@hook.subscribe.startup_once
def autostart():
    autorun = os.path.expanduser("~/.config/qtile/autostart.sh")
    subprocess.Popen([autorun])


@hook.subscribe.startup
def logon():
    refresh = os.path.expanduser("~/scripts/calcurseupdate.sh")
    subprocess.Popen([refresh])


# Settings that work, but we don't need anymore
#
# def task_list_fix(text):
#     browsers = ["Chromium", "Firefox"]
#     for browser in browsers:
#         if browser in text:
#             return browser
#     return text

# widget.WidgetBox(
#     text_closed="󱂬",
#     text_open="󱂬",
#     widgets=[
#         widget.TaskList(
#             border=Color3,
#             borderwidth=1,
#             font="JetBrainsMono Nerd Font Propo",
#             fontsize=10,
#             rounded=False,
#             theme_mode="preferred",
#             icon_size=12,
#             parse_text=task_list_fix,
#         ),
#     ],
# ),
