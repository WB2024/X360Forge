def get_translations():
    """ Dictionary of UI strings for the GUI. """
    return {
        "English": {
            "title": "X360Forge",
            "author": "by WB2024",
            "extract": "Extract Game Folders from ISOs",
            "create": "Create ISOs from Game Folders",
            "extract_delete": "Extract  +  Delete ISO Files  \u26a0  PERMANENT",
            "delete": "Delete Game Folders  \u26a0  PERMANENT",
            "fix_iso": "Fix ISO  \u2014  abgx360",
            "iso2god": "ISO  \u2192  GOD  (Games on Demand)",
            "god2iso": "GOD  \u2192  ISO  (Games on Demand)",
            "help": "Help / README",
            'help_text': (
                "X360Forge\n"
                "Xbox 360 & Original Xbox ISO Utility\n"
                "by WB2024\n\n"
                "══════════════════════════════════════════════\n\n"
                "1.  Batch Extract ISOs → Game Folders\n\n"
                "    Place ISO files into the x_ISO folder.\n"
                "    Click 'Extract Game Folders from ISOs'.\n"
                "    Game folders are created next to x_ISO/, each containing .xex or .xbe files.\n\n"
                "    Use 'Extract + Delete' to remove source ISOs automatically after extraction.\n\n"
                "══════════════════════════════════════════════\n\n"
                "2.  Batch Create ISOs from Game Folders\n\n"
                "    Place game folders next to x_ISO/ (not inside it).\n"
                "    Each folder must contain .xex or .xbe files.\n"
                "    Click 'Create ISOs from Game Folders'.\n"
                "    ISO files are created next to x_ISO/.\n\n"
                "    Tip: Run Fix ISO on newly created ISOs to correct headers.\n\n"
                "══════════════════════════════════════════════\n\n"
                "3.  Fix ISO  (abgx360)\n\n"
                "    Click 'Fix ISO', select an ISO file.\n"
                "    abgx360 verifies and auto-fixes the ISO:\n"
                "      --af3  AutoFix level 3 (always fix)\n"
                "      -p     Fix video padding\n"
                "      -s     No colour codes\n"
                "      -o     Offline mode (no internet needed)\n"
                "    Output streams live into the status window.\n\n"
                "══════════════════════════════════════════════\n\n"
                "4.  ISO → GOD  (Games on Demand)\n\n"
                "    Click 'ISO → GOD', select an ISO file and output folder.\n"
                "    Converts Xbox 360 and Original Xbox ISOs to GOD format.\n\n"
                "══════════════════════════════════════════════\n\n"
                "5.  GOD → ISO  (Games on Demand)\n\n"
                "    Click 'GOD → ISO', select the GOD package header file\n"
                "    (the file without an extension — not the .data folder),\n"
                "    then select an output folder.\n"
                "    The ISO is reconstructed in the output folder.\n\n"
                "══════════════════════════════════════════════\n\n"
                "6.  Delete Game Folders\n\n"
                "    Permanently deletes all game folders next to x_ISO/ that contain .xex/.xbe files.\n"
                "    This action cannot be undone.\n\n"
                "══════════════════════════════════════════════\n\n"
                "Credits\n\n"
                "  BLAHPR            Original utility\n"
                "  XboxDev           extract-xiso\n"
                "  iliazeus          iso2god-rs\n"
                "  raburton          god2iso (original C#)\n"
                "  Seacrest/Bakasura abgx360 / abgx360-reloaded\n"
                "  <in@fishtank.com> XISO format work\n\n"
                "  Contact: geebob273@gmail.com\n"
            ),
        },
    }

