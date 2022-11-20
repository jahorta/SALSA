inst_defaults = {
    0: {
        "Location": "0x801f6044",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00000000,
        "Link": 1,
        "Link Type": "Jump",
        "Parameters": {
            0: {
                "Name": "CompareResult",
                "Type": "scpt-float",
                "Signed": False,
            },
            1: {
                "Name": "Offset",
                "Type": "int",
                "Signed": True,
            }
        }
    },
    1: {
        "Location": "0x801f60f0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00000000,
        "Parameters": {}
    },
    2: {
        "Location": "0x801f60f0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00000000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {}
    },
    3: {
        "Location": "0x801f5f50",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00000000,
        "Link": 3,
        "Link Type": "Switch",
        "Loop": [2, 3],
        "Loop Iterations": 1,
        "Switch Entry": [2, 3],
        "Parameters": {
            0: {
                "Name": "Choice",
                "Type": "scpt-float",
                "Signed": False,
            },
            1: {
                "Name": "ChoiceNum",
                "Type": "int",
                "Signed": False,
            },
            2: {
                "Name": "Switch Case",
                "Type": "int",
                "Signed": False
            },
            3: {
                "Name": "Switch Offset",
                "Type": "int",
                "Signed": False
            }
        }
    },
    4: {
        "Location": "0x801f60f0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00000000,
        "Parameters": {}
    },
    5: {
        "Location": "0x801f5eb4",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00000000,
        "Parameters": {
            0: {
                "Name": "Offset",
                "Type": "int",
                "Mask": 0x0000ffff,
                "Signed": False,
            },
            1: {
                "Name": "Value",
                "Type": "scpt-byte",
                "Signed": False,
            }
        }
    },
    6: {
        "Location": "0x801f5d7c",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00000000,
        "Parameters": {
            0: {
                "Name": "Offset",
                "Type": "int",
                "Mask": 0x0000ffff,
                "Signed": False,
            },
            1: {
                "Name": "Value",
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    7: {
        "Location": "0x801f5d08",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00000000,
        "Parameters": {
            0: {
                "Name": "Offset",
                "Type": "int",
                "Mask": 0x0000ffff,
                "Signed": False,
            },
            1: {
                "Name": "Value",
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    8: {
        "Location": "0x801f60f0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00000000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {}
    },
    9: {
        "Location": "0x801f60c4",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00000000,
        "Parameters": {
            0: {
                "Type": "scpt-skip",
                "Signed": False,
            }
        }
    },
    10: {
        "Name": "Jump",
        "Link": 0,
        "Link Type": "Jump",
        "Location": "0x801f5ccc",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00000000,
        "Parameters": {
            0: {
                "Name": "Offset",
                "Type": "int",
                "Mask": 0x0000ffff,
                "Signed": True,
            }
        }
    },
    11: {
        "Name": "Load Subscript",
        "Location": "0x801f5c30",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00000000,
        "Link": 0,
        "Link Type": "Jump",
        "Parameters": {
            0: {
                "Name": "Offset",
                "Type": "int",
                "Signed": True,
            }
        }
    },
    12: {
        "Name": "Return",
        "Location": "0x801f5bd0",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00000000,
        "Parameters": {}
    },
    13: {
        "Name": "code_error",
        "Description": "s_scptSTUB:_code_error!_802d4758\n\nThis is never used as an instruction. It is used to set a flag to try to prevent a frame refresh after the next instruction",
        "Location": "0x801f60f0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00000000,
        "Parameters": {}
      },
    14: {
        "Name": "code_error",
        "Description": "s_scptSTUB:_code_error!_802d4758\n\nThis should not be an instruction call\n\n***Not used in the game***",
        "Location": "0x801f60f0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00000000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {}
    },
    15: {
        "Name": "Force next frame",
        "Description": "***Not used in the game***\n\nThis instruction will set the 0x4 field in the current instruction buffer to zero. This forces the instruction interpreter function to exit allow for the next frame to be drawn. On next frame, any pending instruction buffers will be read.",
        "Location": "0x801f5bb4",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": True,
        "Hard parameter two": 0x00000000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {}
    },
    16: {
        "Name": "Sleep",
        "Location": "0x801f570c",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00000000,
        "Parameters": {
            0: {
                "Name": "Duration",
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    17: {
        "Name": "Set Bit",
        "Location": "0x801f5b14",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00000000,
        "Parameters": {
            0: {
                "Name": "Offset",
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    18: {
        "Name": "Unset Bit",
        "Description": "Unsets a bit in the bit field at 0x80310b3c\nBit: *add[<Offset>,0]*\n\n(Sets the bit to 0)",
        "Location": "0x801f5a74",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00000000,
        "Parameters": {
            0: {
                "Name": "Offset",
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    19: {
        "Name": "Invert Bit",
        "Description": "Inverts a bit in the bit field at 0x80310b3c\nBit: *add[<Offset>,0]*\n\n***Not used in the game***",
        "Location": "0x801f59c0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00000000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
            0: {
                "Name": "Offset",
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    20: {
        "Instruction ID": "20",
        "Name": "Give Item",
        "Description": "Gives an item with item ID: <ItemID>",
        "Location": "0x801f593c",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00000000,
        "Parameters": {
            0: {
                "Name": "ItemID",
                "Type": "scpt-short",
                "Signed": False
            }
        }
    },
    21: {
        "Name": "Take Item",
        "Description": "Takes item with itemID: <ItemID>",
        "Location": "0x801f58b8",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00000000,
        "Parameters": {
            0: {
                "Name": "ItemID",
                "Type": "scpt-short",
                "Signed": False
            }
        }
    },
    22: {
        "Name": "Return 1",
        "Description": "Returns a 1. Does not advance the pointer, so possibly infinite loop...\n\n***Not used in the game***",
        "Location": "0x801f58b0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00000000,
        "Warning": "May cause infinite loop in script system, Instruction not used in the game, may be buggy",
        "Parameters": {}
    },
    23: {
        "Name": "Load *.mld file",
        "Location": "0x801ff13c",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00000000,
        "Link": 0,
        "Link Type": "String",
        "Parameters": {
            0: {
                "Name": "Offset",
                "Type": "int",
                "Signed": True,
            }
        }
    },
    24: {
        "Location": "0x8020a938",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Link": 0,
        "Link Type": "String",
        "Parameters": {
            0: {
                "Name": "Offset",
                "Type": "int",
                "Signed": True
            }
        }
    },
    25: {
        "Location": "0x8020a580",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Link": 1,
        "Link Type": "String",
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Name": "Offset",
                "Type": "int",
                "Signed": False,
            }
        }
    },
    26: {
        "Location": "0x802088d8",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    27: {
        "Location": "0x80208774",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            }
        }
    },
    28: {
        "Location": "0x801fbba8",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00020000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-int",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    29: {
        "Location": "0x801fbf90",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00020000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-int",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    30: {
        "Location": "0x802085cc",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x0002000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    31: {
        "Location": "0x80208234",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00050000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-float",
                "Signed": False,
            },
            7: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    32: {
        "Location": "0x80208044",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00050000,
        "Parameters": {
          0: {
            "Type": "scpt-short",
            "Signed": False,
          },
          1: {
            "Type": "scpt-float",
            "Signed": False,
          },
          2: {
            "Type": "scpt-float",
            "Signed": False,
          },
          3: {
            "Type": "scpt-float",
            "Signed": False,
          },
          4: {
            "Type": "scpt-float",
            "Signed": False,
          },
          5: {
            "Type": "scpt-float",
            "Signed": False,
          },
          6: {
            "Type": "scpt-float",
            "Signed": False,
          },
          7: {
            "Type": "scpt-int",
            "Signed": False,
          }
        }
      },
    33: {
        "Location": "0x80203ffc",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0xfffe0000,
        "Loop": [1, 2, 3, 4, 5, 6, 7],
        "Loop Iterations": 0,
        "Parameters": {
            0: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-float",
                "Signed": False,
            },
            7: {
                "Type": "scpt-int",
                "Signed": False,
            },
        }
    },
    34: {
        "Location": "0x801fc68c",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00050000,
        "Loop": [2, 3, 4, 5, 6, 7, 8, 9, 10],
        "Loop Iterations": 1,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-int",
                "Signed": False,
            },
            7: {
                "Type": "scpt-int",
                "Signed": False,
            },
            8: {
                "Type": "scpt-float",
                "Signed": False,
            },
            9: {
                "Type": "scpt-int",
                "Signed": False,
            },
            10: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    35: {
        "Location": "0x801fcaac",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00050000,
        "Loop": [2, 3, 4, 5, 6, 7, 8, 9, 10],
        "Loop Iterations": 1,
        "Parameters": {
          0: {
                "Type": "scpt-short",
                "Signed": False,
          },
          1: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
          },
          2: {
                "Type": "scpt-float",
                "Signed": False,
          },
          3: {
                "Type": "scpt-float",
                "Signed": False,
          },
          4: {
                "Type": "scpt-float",
                "Signed": False,
          },
          5: {
                "Type": "scpt-float",
                "Signed": False,
          },
          6: {
                "Type": "scpt-int",
                "Signed": False,
          },
          7: {
                "Type": "scpt-int",
                "Signed": False,
          },
          8: {
                "Type": "scpt-float",
                "Signed": False,
          },
          9: {
                "Type": "scpt-int",
                "Signed": False,
          },
          10: {
                "Type": "scpt-int",
                "Signed": False,
          }
        }
    },
    36: {
        "Location": "0x801fc408",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00050000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-int",
                "Signed": False,
            },
            5: {
                "Type": "scpt-int",
                "Signed": False,
            },
            6: {
                "Type": "scpt-int",
                "Signed": False,
            },
            7: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    37: {
        "Location": "0x801fc184",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00050000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-int",
                "Signed": False,
            },
            5: {
                "Type": "scpt-int",
                "Signed": False,
            },
            6: {
                "Type": "scpt-int",
                "Signed": False,
            },
            7: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    38: {
        "Location": "0x80207cd0",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00020000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-short",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    39: {
        "Location": "0x80207ed0",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00020000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    40: {
        "Location": "0x80206ea8",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-short",
                "Signed": False,
            }
        }
    },
    41: {
        "Location": "0x80207a40",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    42: {
        "Location": "0x80207830",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Loop": [2],
        "Loop Iterations": 1,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False
            },
            1: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False
            },
            2: {
                "Type": "scpt-short",
                "Signed": False,
            }
        }
    },
    43: {
        "Location": "0x802073b4",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00000000,
        "Link": 0,
        "Link Type": 'String',
        "Warning": "This instruction will exit the current script and load a new one",
        "Parameters": {
            0: {
                "Name": "Offset",
                "Type": "int",
                "Signed": False,
            }
        }
    },
    44: {
        "Name": "Return 1",
        "Description": "Returns a 1. Does not change the script pointer, so may lead to an infinite loop",
        "Location": "0x801fedc8",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00060000,
        "Warning": "May lead to an infinite loop, Instruction not used in the game, may be buggy",
        "Parameters": {}
    },
    45: {
        "Location": "0x8020726c",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {}
    },
    46: {
        "Location": "0x8020549c",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0xfffe0000,
        "Parameters": {
            0: {
                "Type": "scpt-float",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    47: {
        "Location": "0x80204f8c",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0xfffe0000,
        "Parameters": {
            0: {
                "Type": "scpt-float",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    48: {
        "Location": "0x802051d0",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
            0: {
                "Name": "Value",
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    49: {
        "Location": "0x80204f04",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0xfffe0000,
        "Parameters": {
            0: {
                "Name": "Compare",
                "Type": "scpt-float",
                "Default": 60.0,
                "Signed": False,
            }
        }
    },
    50: {
        "Location": "0x80204cd0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0xfffe0000,
        "Parameters": {
            0: {
                "Type": "scpt-float",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    51: {
        "Location": "0x801fa060",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            2: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    52: {
        "Location": "0x80204be8",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0xfffe0000,
        "Parameters": {
            0: {
                "Type": "scpt-float",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    53: {
        "Location": "0x801fa630",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00050000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-int",
                "Signed": False,
            },
            6: {
                "Type": "scpt-int",
                "Signed": False,
            },
            7: {
                "Type": "scpt-float",
                "Signed": False,
            },
            8: {
                "Type": "scpt-int",
                "Signed": False,
            },
            9: {
                "Type": "scpt-float",
                "Signed": False,
            },
            10: {
                "Type": "scpt-int",
                "Signed": False,
            },
            11: {
                "Type": "scpt-int",
                "Signed": False,
            },
            12: {
                "Type": "scpt-float",
                "Signed": False,
            },
            13: {
                "Type": "scpt-float",
                "Signed": False,
            },
            14: {
                "Type": "scpt-float",
                "Signed": False,
            },
            15: {
                "Type": "scpt-float",
                "Signed": False,
            },
            16: {
                "Type": "scpt-int",
                "Signed": False,
            },
            17: {
                "Type": "scpt-int",
                "Signed": False,
            },
            18: {
                "Type": "scpt-float",
                "Signed": False,
            },
            19: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    54: {
        "Location": "0x801fa4c0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Link": 1,
        "Link Type": "String",
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Name": "Offset",
                "Type": "int",
                "Signed": True,
            }
        }
      },
    55: {
        "Location": "0x801fa398",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            1: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            2: {
                "Type": "scpt-int",
                "Signed": False
            }
        }
    },
    56: {
        "Location": "0x801fa290",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            }
        }
    },
    57: {
        "Name": "INS_BG Syntax Error",
        "Description": "Just prints: scptINS BG: SYNTAX ERROR!!!",
        "Location": "0x801fef18",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {}
    },
    58: {
        "Name": "DELL_BG Syntax Error",
        "Description": "Just prints: scptDELL BG: SYNTAX ERROR!!!",
        "Location": "0x801feee8",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {}
    },
    59: {
        "Location": "0x8020170c",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    60: {
        "Location": "0x802015ac",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    61: {
        "Location": "0x802021b8",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00040000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    62: {
        "Location": "0x80202004",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00040000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    63: {
        "Location": "0x80201e54",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00040000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    64: {
        "Location": "0x80201ce0",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00040000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    65: {
        "Location": "0x802019f8",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00040000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    66: {
        "Location": "0x801f9708",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            2: {
                "Type": "scpt-byte",
                "Signed": False,
            }
        }
    },
    67: {
        "Name": "Kill Syntax Error",
        "Description": "scptKill: SYNTAX ERROR!!!",
        "Location": "0x801ff1e0",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {}
    },
    68: {
        "Location": "0x8020a2c8",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {}
    },
    69: {
        "Location": "0x801fa1d0",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Link": 0,
        "Link Type": "String",
        "Parameters": {
            0: {
                "Name": "Offset",
                "Type": "int",
                "Signed": True,
            }
        }
    },
    70: {
        "Location": "0x80207130",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-float",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    71: {
        "Location": "0x80206ff4",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-float",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    72: {
        "Location": "0x80206cbc",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-float",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-float",
                "Signed": False,
            },
            7: {
                "Type": "scpt-float",
                "Signed": False,
            },
            8: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    73: {
        "Location": "0x80206ab0",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-float",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-float",
                "Signed": False,
            },
            7: {
                "Type": "scpt-float",
                "Signed": False,
            },
            8: {
                "Type": "scpt-int",
                "Signed": False,
            },
            9: {
                "Type": "scpt-short",
                "Signed": False,
            }
        }
    },
    74: {
        "Location": "0x80206904",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-float",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    75: {
        "Location": "0x8020660c",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-float",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-float",
                "Signed": False,
            },
            7: {
                "Type": "scpt-float",
                "Signed": False,
            },
            8: {
                "Type": "scpt-int",
                "Signed": False,
            },
            9: {
                "Type": "scpt-float",
                "Signed": False,
            },
            10: {
                "Type": "scpt-float",
                "Signed": False,
            },
            11: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    76: {
        "Location": "0x802056a8",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": True,
        "Force Frame Refresh Condition": "If 0x80346c3c == 2 and 80302f18 == 2, force frame refresh",
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    77: {
        "Location": "0x8020a048",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    78: {
        "Location": "0x801fbd9c",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00020000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-int",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    79: {
        "Location": "0x80201228",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-int",
                "Signed": False,
            },
            3: {
                "Type": "scpt-int",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    80: {
        "Name": "Reset 80305ba9",
        "Description": "Sets global variable at 80305ba9 to zero",
        "Location": "0x80200f88",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {}
    },
    81: {
        "Location": "0x80200df4",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-float",
                "Signed": False,
            },
            7: {
                "Type": "scpt-float",
                "Signed": False,
            },
            8: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    82: {
        "Location": "0x80200ce4",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    83: {
        "Location": "0x80200b90",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    84: {
        "Location": "0x802009c4",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-float",
                "Signed": False,
            },
            7: {
                "Type": "scpt-float",
                "Signed": False,
            },
            8: {
                "Type": "scpt-float",
                "Signed": False,
            },
            9: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    85: {
        "Location": "0x8020d848",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Loop": [2],
        "Loop Iterations": 1,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-short",
                "Signed": False,
            }
        }
    },
    86: {
        "Location": "0x8020d668",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Loop": [2],
        "Loop Iterations": 1,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-short",
                "Signed": False,
            }
        }
    },
    87: {
        "Location": "0x8020d488",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Loop": [2],
        "Loop Iterations": 1,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-short",
                "Signed": False,
            }
        }
    },
    88: {
        "Location": "0x8020d2a8",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Loop": [2],
        "Loop Iterations": 1,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-short",
                "Signed": False,
            }
        }
    },
    89: {
        "Location": "0x801fb664",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00050000,
        "Loop": [2, 3, 4, 5, 6, 7, 8, 9, 10],
        "Loop Iterations": 1,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-int",
                "Signed": False,
            },
            7: {
                "Type": "scpt-int",
                "Signed": False,
            },
            8: {
                "Type": "scpt-float",
                "Signed": False,
            },
            9: {
                "Type": "scpt-int",
                "Signed": False,
            },
            10: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    90: {
        "Location": "0x801fb120",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00050000,
        "Loop": [2, 3, 4, 5, 6, 7, 8, 9, 10],
        "Loop Iterations": 1,
        "Implement": True,
        "Parameter num": 13,
        "Notes": "Only runs if param1 & 1 == 1:\n\n1: scpt-short\n2: int\n\nloop ((2)) iterations):\n\n3: scpt-float\n4: scpt-float\n5: scpt-float\n6: scpt-float\n7: scpt-int\n8: scpt-int\n9: scpt-float\n10: scpt-int\n11: scpt-int",
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-int",
                "Signed": False,
            },
            7: {
                "Type": "scpt-int",
                "Signed": False,
            },
            8: {
                "Type": "scpt-float",
                "Signed": False,
            },
            9: {
                "Type": "scpt-int",
                "Signed": False,
            },
            10: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    91: {
        "Location": "0x8020d1c0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    92: {
        "Location": "0x801ffef0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    93: {
        "Location": "0x801ffe3c",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    94: {
        "Location": "0x801ffdb4",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    95: {
        "Location": "0x80206424",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
            0: {
                "Type": "scpt-float",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    96: {
        "Location": "0x8020623c",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-float",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    97: {
        "Location": "0x80208a20",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    98: {
        "Location": "0x801ffc20",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Loop": [1],
        "Loop Iterations": 0,
        "Parameters": {
            0: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-short",
                "Signed": False,
            }
        }
    },
    99: {
        "Location": "0x801ffa60",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Loop": [1],
        "Loop Iterations": 0,
        "Parameters": {
            0: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-short",
                "Signed": False,
            }
        }
    },
    100: {
        "Location": "0x80208c08",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    101: {
        "Location": "0x801f984c",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    102: {
        "Location": "0x801f9668",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    103: {
        "Location": "0x801f9614",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {}
    },
    104: {
        "Location": "0x801f9454",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0xfffe0000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    105: {
        "Location": "0x801f934c",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0xfffe0000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    106: {
        "Location": "0x801f9120",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-short",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-float",
                "Signed": False,
            },
            7: {
                "Type": "scpt-float",
                "Signed": False,
            },
            8: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    107: {
        "Location": "0x801f8f7c",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-short",
                "Signed": False,
            }
        }
    },
    108: {
        "Location": "0x801fabdc",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00050000,
        "Loop": [2, 3, 4, 5, 6, 7, 8, 9, 10],
        "Loop Iterations": 1,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-int",
                "Signed": False,
            },
            7: {
                "Type": "scpt-int",
                "Signed": False,
            },
            8: {
                "Type": "scpt-float",
                "Signed": False,
            },
            9: {
                "Type": "scpt-int",
                "Signed": False,
            },
            10: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    109: {
        "Location": "0x80200fc4",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            1: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            2: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            3: {
                "Type": "scpt-int",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-int",
                "Signed": False,
            },
            7: {
                "Type": "scpt-float",
                "Signed": False,
            },
            8: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    110: {
        "Location": "0x801ff0f8",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Link": 0,
        "Link Type": "String",
        "Parameters": {
            0: {
                "Name": "Offset",
                "Type": "int",
                "Signed": False,
            }
        }
    },
    111: {
        "Location": "0x802060d4",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0xfffe0000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    112: {
        "Name": "Trigger Battle",
        "Location": "0x801ff210",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-int",
                "Signed": False,
            },
            3: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    113: {
        "Location": "0x801ff05c",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": True,
        "Hard parameter two": 0x00010000,
        "Link": 0,
        "Link Type": "String",
        "Parameters": {
            0: {
                "Name": "Offset",
                "Type": "int",
                "Signed": False,
            }
        }
    },
    114: {
        "Location": "0x801fef80",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-short",
                "Signed": False,
            }
        }
    },
    115: {
        "Location": "0x801fef48",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {}
    },
    116: {
        "Location": "0x801f9ea8",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            2: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            3: {
                "Type": "scpt-int",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    117: {
        "Location": "0x80208d9c",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    118: {
        "Location": "0x80209330",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Loop": [2],
        "Loop Iterations": 1,
        "Loop Break Condition": {
            "Parameter": 1,
            "Test": "==",
            "Value": 0x10000,
            "Location": 'External'
        },
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-short",
                "Signed": False,
            }
        }
    },
    119: {
        "Location": "0x80209028",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Loop": [2],
        "Loop Iterations": 1,
        "Loop Break Condition": {
            "Parameter": 1,
            "Test": "==",
            "Value": 0x10000,
            "Location": 'External'
        },
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-short",
                "Signed": False,
            }
        }
    },
    120: {
        "Location": "0x801f8608",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00020000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-int",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-int",
                "Signed": False,
            },
            6: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    121: {
        "Location": "0x802034b0",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0xfffe0000,
        "Loop": [1, 2, 3, 4, 5, 6, 7],
        "Loop Iterations": 0,
        "Parameters": {
            0: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-float",
                "Signed": False,
            },
            7: {
                "Type": "scpt-int",
                "Signed": False,
            },
        }
    },
    122: {
        "Location": "0x80205f14",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-float",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    123: {
        "Location": "0x8020527c",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0xfffe0000,
        "Parameters": {
            0: {
                "Type": "scpt-float",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    124: {
        "Location": "0x80204e28",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0xfffe0000,
        "Parameters": {
            0: {
                "Type": "scpt-float",
                "Default": 60.0,
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    125: {
        "Location": "0x8020731c",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0xfffe0000,
        "Parameters": {}
    },
    126: {
        "Location": "0x80207554",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Loop": [1],
        "Loop Iterations": 0,
        "Parameters": {
            0: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    127: {
        "Location": "0x80207630",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Loop": [1],
        "Loop Iterations": 0,
        "Parameters": {
            0: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    128: {
        "Location": "0x801f8d0c",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00020000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-int",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    129: {
        "Name": "Schedule Inst",
        "Location": "0x801f57f8",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Name": "Frames",
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Name": "Length",
                "Type": "int",
                "Signed": False,
            }
        }
    },
    130: {
        "Location": "0x801f88d4",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00050000,
        "Loop": [2, 3, 4, 5, 6, 7, 8],
        "Loop Iterations": 1,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-float",
                "Signed": False,
            },
            7: {
                "Type": "scpt-float",
                "Signed": False,
            },
            8: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    131: {
        "Location": "0x80200634",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Loop": [1, 2, 3, 4],
        "Loop Iterations": 0,
        "Parameters": {
            0: {
                "Name": "Iterations",
                "Type": "int",
                "Mask": 0x0000ffff,
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    132: {
        "Location": "0x80200460",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Loop": [1, 2, 3, 4, 5, 6, 7],
        "Loop Iterations": 0,
        "Parameters": {
            0: {
                "Name": "Iterations",
                "Type": "int",
                "Mask": 0x0000ffff,
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-float",
                "Signed": False,
            },
            7: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    133: {
        "Location": "0x802001f8",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Loop": [2, 3, 4, 5, 6, 7, 8, 9, 10],
        "Loop Iterations": 0,
        "Parameters": {
            0: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-float",
                "Signed": False,
            },
            7: {
                "Type": "scpt-float",
                "Signed": False,
            },
            8: {
                "Type": "scpt-float",
                "Signed": False,
            },
            9: {
                "Type": "scpt-float",
                "Signed": False,
            },
            10: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    134: {
        "Location": "0x80209548",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00020000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-int",
                "Signed": False,
            },
            6: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    135: {
        "Location": "0x80201458",
        "Skip Frame Refresh": "0x00000000",
        "Force Frame Refresh": False,
        "Hard parameter two": "0x00010000",
        "Loop": [2],
        "Loop Iterations": 1,
        "Parameters": {
          0: {
            "Type": "scpt-int",
            "Signed": False,
          },
          1: {
            "Name": "Iterations",
            "Type": "int",
            "Signed": False,
          },
          2: {
            "Type": "scpt-short",
            "Signed": False,
          }
        }
    },
    136: {
        "Location": "0x80209b94",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00050000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    137: {
        "Location": "0x80207c2c",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00050000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    138: {
        "Name": "Display Save Menu",
        "Description": "Sets 803473b4 to 1, activating the save menu on the next available frame",
        "Location": "0x801fed58",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {}
    },
    139: {
        "Location": "0x80202dec",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0xfffe0000,
        "Loop": [1, 2, 3, 4, 5, 6, 7],
        "Loop Iterations": 0,
        "Parameters": {
            0: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-float",
                "Signed": False,
            },
            7: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    140: {
        "Location": "0x801fe960",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    141: {
        "Location": "0x801fe7a0",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    142: {
        "Location": "0x801fe560",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            1: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            2: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    143: {
        "Name": "Return 0",
        "Description": "This only returns a zero.",
        "Location": "0x8020a72c",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Warning": "May cause an infinite loop. Instruction not used in the game, may be buggy",
        "Parameters": {}
    },
    144: {
        "Name": "Display Message",
        "Location": "0x8020a734",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Link": 0,
        "Link Type": "String",
        "Parameters": {
            0: {
                "Name": "Offset",
                "Type": "int",
                "Signed": True,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    145: {
        "Name": "Roll Rand",
        "Location": "0x801fe21c",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    146: {
        "Location": "0x801fe06c",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
          0: {
                "Type": "scpt-int",
                "Signed": False,
          }
        }
    },
    147: {
        "Location": "0x801f9c18",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-int",
                "Signed": False,
            },
            7: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            8: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            9: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    148: {
        "Location": "0x802007c0",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Loop": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "Loop Iterations": 0,
        "Parameters": {
            0: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-float",
                "Signed": False,
            },
            7: {
                "Type": "scpt-float",
                "Signed": False,
            },
            8: {
                "Type": "scpt-float",
                "Signed": False,
            },
            9: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    149: {
        "Location": "0x801ff604",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    150: {
        "Location": "0x801ff470",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    151: {
        "Location": "0x801ff380",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    152: {
        "Location": "0x8020ceb4",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Loop": [1],
        "Loop Iterations": 0,
        "Parameters": {
            0: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    153: {
        "Location": "0x801fd264",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Loop": [1, 2, 3],
        "Loop Iterations": 0,
        "Loop Break Condition": {
            "Parameter": 3,
            "Test": "==",
            "Value": 0,
            "Location": 'Internal'
        },
        "Parameters": {
          0: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
          },
          1: {
                "Type": "scpt-byte",
                "Signed": False,
          },
          2: {
                "Type": "scpt-byte",
                "Signed": False,
          },
          3: {
                "Type": "scpt-short",
                "Signed": False,
          }
        }
    },
    154: {
        "Location": "0x8020c390",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    155: {
        "Name": "Select Choice",
        "Location": "0x8020a338",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Link": 1,
        "Link Type": "String",
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Name": "Offset",
                "Type": "int",
                "Signed": True,
            },
            2: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    156: {
        "Location": "0x801fed04",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {}
    },
    157: {
        "Name": "Add Party Member",
        "Location": "0x801fec80",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Name": "PC_ID",
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    158: {
        "Name": "Remove Party Member",
        "Location": "0x801febfc",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Name": "PC_ID",
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    159: {
        "Location": "0x802023bc",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0xfffe0000,
        "Loop": [1, 2, 3, 4, 5, 6, 7, 8],
        "Loop Iterations": 0,
        "Parameters": {
            0: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-float",
                "Signed": False,
            },
            7: {
                "Type": "scpt-int",
                "Signed": False,
            },
            8: {
                "Type": "scpt-byte",
                "Signed": False,
            }
        }
    },
    160: {
        "Location": "0x8020a168",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
          0: {
                "Type": "scpt-int",
                "Signed": False,
          },
          1: {
                "Type": "scpt-float",
                "Signed": False,
          },
          2: {
                "Type": "scpt-float",
                "Signed": False,
          },
          3: {
                "Type": "scpt-float",
                "Signed": False,
          },
          4: {
                "Type": "scpt-float",
                "Signed": False,
          },
          5: {
                "Type": "scpt-float",
                "Signed": False,
          },
          6: {
                "Type": "scpt-float",
                "Signed": False,
          }
        }
    },
    161: {
        "Location": "0x801f8158",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00050000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Loop": [2, 3, 4, 5, 6, 7, 8, 9, 10],
        "Loop Iterations": 1,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-float",
                "Signed": False,
            },
            7: {
                "Type": "scpt-float",
                "Signed": False,
            },
            8: {
                "Type": "scpt-float",
                "Signed": False,
            },
            9: {
                "Type": "scpt-int",
                "Signed": False,
            },
            10: {
                "Type": "scpt-int",
                "Signed": False,
            },
        }
    },
    162: {
        "Location": "0x80205e48",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    163: {
        "Location": "0x80205c24",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-float",
                "Signed": False,
            },
            7: {
                "Type": "scpt-float",
                "Signed": False,
            },
            8: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    164: {
        "Location": "0x8020184c",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
          0: {
                "Type": "scpt-short",
                "Signed": False,
          },
          1: {
                "Type": "scpt-int",
                "Signed": False,
          }
        }
    },
    165: {
        "Location": "0x80215590",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-int",
                "Signed": False,
            },
            3: {
                "Type": "scpt-int",
                "Signed": False,
            },
            4: {
                "Type": "scpt-int",
                "Signed": False,
            },
            5: {
                "Type": "scpt-int",
                "Signed": False,
            },
            6: {
                "Type": "scpt-int",
                "Signed": False,
            },
            7: {
                "Type": "scpt-int",
                "Signed": False,
            },
            8: {
                "Type": "scpt-int",
                "Signed": False,
            },
            9: {
                "Type": "scpt-int",
                "Signed": False,
            },
            10: {
                "Type": "scpt-int",
                "Signed": False,
            },
            11: {
                "Type": "scpt-int",
                "Signed": False,
            },
            12: {
                "Type": "scpt-int",
                "Signed": False,
            },
            13: {
                "Type": "scpt-float",
                "Signed": False,
            },
            14: {
                "Type": "scpt-float",
                "Signed": False,
            },
            15: {
                "Type": "scpt-float",
                "Signed": False,
            },
            16: {
                "Type": "scpt-float",
                "Signed": False,
            },
            17: {
                "Type": "scpt-int",
                "Signed": False,
            },
            18: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    166: {
        "Location": "0x80215368",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    167: {
        "Location": "0x802150bc",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {}
    },
    168: {
        "Location": "0x801fdf0c",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    169: {
        "Location": "0x801fde70",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-float",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    170: {
        "Location": "0x8021507c",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {}
    },
    171: {
        "Location": "0x8021503c",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {}
    },
    172: {
        "Location": "0x80214fac",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    173: {
        "Location": "0x80214f1c",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    174: {
        "Location": "0x80214e8c",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    175: {
        "Location": "0x801f5468",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
          0: {
            "Type": "scpt-short",
            "Signed": False,
          },
          1: {
            "Type": "scpt-float",
            "Signed": False,
          }
        }
    },
    176: {
        "Location": "0x80209974",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-short",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    177: {
        "Location": "0x8020dd1c",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": True,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-float",
                "Signed": False,
            },
            7: {
                "Type": "scpt-float",
                "Signed": False,
            },
            8: {
                "Type": "scpt-float",
                "Signed": False,
            },
            9: {
                "Type": "scpt-float",
                "Signed": False,
            },
            10: {
                "Type": "scpt-float",
                "Signed": False,
            },
            11: {
                "Type": "scpt-float",
                "Signed": False,
            },
            12: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    178: {
        "Location": "0x802049bc",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-float",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-int",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-float",
                "Signed": False,
            },
            7: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    179: {
        "Location": "0x802058f8",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-float",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    180: {
        "Location": "0x80201b6c",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    181: {
        "Location": "0x801fddb0",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    182: {
        "Location": "0x801f60f0",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Warning": "This instruction does nothing. Instruction not used in the game, may be buggy",
        "Parameters": {}
    },
    183: {
        "Location": "0x801fdfb8",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
          0: {
            "Type": "scpt-short",
            "Signed": False,
          }
        }
    },
    184: {
        "Location": "0x802057e0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    185: {
        "Location": "0x8020bcf4",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    186: {
        "Location": "0x8020bc38",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    187: {
        "Location": "0x8020bb8c",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    188: {
        "Location": "0x8020bae0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    189: {
        "Location": "0x801f60f0",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {}
    },
    190: {
        "Location": "0x802097c0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    191: {
        "Location": "0x80214dfc",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    192: {
        "Location": "0x80214d6c",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    193: {
        "Location": "0x80214cdc",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    194: {
        "Location": "0x80214c04",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    195: {
        "Location": "0x801fdab8",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    196: {
        "Location": "0x80207368",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {}
    },
    197: {
        "Location": "0x8021528c",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    198: {
        "Location": "0x80209ed8",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    199: {
        "Location": "0x80209d74",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            }
        }
    },
    200: {
        "Location": "0x801f60f0",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {}
    },
    201: {
        "Name": "Restore Health All",
        "Description": "Restores everyone's health to max",
        "Location": "0x801fd9b0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {}
    },
    202: {
        "Name": "Restore Magic All",
        "Description": "Restores all of the party members' magic to full",
        "Location": "0x801fd8f0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {}
    },
    203: {
        "Location": "0x801f98e8",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    204: {
        "Location": "0x80214b28",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    205: {
        "Location": "0x80214aa0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    206: {
        "Location": "0x80214a60",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {}
    },
    207: {
        "Location": "0x8020bdb0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            2: {
                "Type": "scpt-short",
                "Signed": False,
            }
        }
    },
    208: {
        "Location": "0x80214a20",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {}
    },
    209: {
        "Location": "0x802149e0",
        "Skip Frame Refresh": "0x00000001",
        "Hard parameter two": "0x00010000",
        "Parameters": {}
    },
    210: {
        "Location": "0x80214994",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Link": 0,
        "Link Type": "String",
        "Parameters": {
            0: {
                "Name": "Offset",
                "Type": "int",
                "Signed": False,
            }
        }
    },
    211: {
        "Name": "Return to Overworld",
        "Location": "0x80214954",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {}
    },
    212: {
        "Location": "0x802150fc",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-int",
                "Signed": False,
            },
            3: {
                "Type": "scpt-int",
                "Signed": False,
            },
            4: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    213: {
        "Location": "0x80215444",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            2: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            3: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            4: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            5: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            6: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            7: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            8: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            9: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            10: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            11: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            12: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            13: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            14: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            15: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            16: {
                "Type": "scpt-byte",
                "Signed": False,
            }
        }
    },
    214: {
        "Location": "0x80207428",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Link": 0,
        "Link Type": "String",
        "Parameters": {
            0: {
                "Name": "Offset",
                "Type": "int",
                "Signed": False,
            }
        }
    },
    215: {
        "Location": "0x801fee54",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Link": 1,
        "Link Type": "String",
        "Parameters": {
          0: {
                "Type": "scpt-int",
                "Signed": False,
          },
          1: {
                "Name": "Offset",
                "Type": "int",
                "Signed": False,
          }
        }
    },
    216: {
        "Location": "0x801fedd0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    217: {
        "Location": "0x8020b9ec",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
          0: {
            "Type": "scpt-int",
            "Signed": False,
          }
        }
    },
    218: {
        "Location": "0x8020b94c",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    219: {
        "Location": "0x801fd850",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    220: {
        "Location": "0x801fd668",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-short",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-float",
                "Signed": False,
            },
            7: {
                "Type": "scpt-float",
                "Signed": False,
            },
            8: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    221: {
        "Location": "0x801fd584",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
            0: {
                "Type": "scpt-float",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    222: {
        "Location": "0x8020b8ac",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    223: {
        "Location": "0x80214270",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
          0: {
                "Type": "scpt-int",
                "Signed": False,
          },
          1: {
                "Type": "scpt-int",
                "Signed": False,
          },
          2: {
                "Type": "scpt-int",
                "Signed": False,
          },
          3: {
                "Type": "scpt-int",
                "Signed": False,
          },
          4: {
                "Type": "scpt-int",
                "Signed": False,
          },
          5: {
                "Type": "scpt-int",
                "Signed": False,
          },
          6: {
                "Type": "scpt-int",
                "Signed": False,
          },
          7: {
                "Type": "scpt-int",
                "Signed": False,
          },
          8: {
                "Type": "scpt-int",
                "Signed": False,
          },
          9: {
                "Type": "scpt-int",
                "Signed": False,
          },
          10: {
                "Type": "scpt-int",
                "Signed": False,
          },
          11: {
                "Type": "scpt-int",
                "Signed": False,
          },
          12: {
                "Type": "scpt-int",
                "Signed": False,
          },
          13: {
                "Type": "scpt-int",
                "Signed": False,
          },
          14: {
                "Type": "scpt-int",
                "Signed": False,
          },
          15: {
                "Type": "scpt-int",
                "Signed": False,
          },
          16: {
                "Type": "scpt-int",
                "Signed": False,
          },
          17: {
                "Type": "scpt-int",
                "Signed": False,
          },
          18: {
                "Type": "scpt-int",
                "Signed": False,
          },
          19: {
                "Type": "scpt-int",
                "Signed": False,
          },
          20: {
                "Type": "scpt-int",
                "Signed": False,
          },
          21: {
                "Type": "scpt-int",
                "Signed": False,
          },
          22: {
                "Type": "scpt-int",
                "Signed": False,
          },
          23: {
                "Type": "scpt-int",
                "Signed": False,
          },
          24: {
                "Type": "scpt-int",
                "Signed": False,
          }
        }
    },
    224: {
        "Location": "0x80213fe8",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-int",
                "Signed": False,
            },
            3: {
                "Type": "scpt-int",
                "Signed": False,
            },
            4: {
                "Type": "scpt-int",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-float",
                "Signed": False,
            },
            7: {
                "Type": "scpt-float",
                "Signed": False,
            },
            8: {
                "Type": "scpt-float",
                "Signed": False,
            },
            9: {
                "Type": "scpt-float",
                "Signed": False,
            },
            10: {
                "Type": "scpt-float",
                "Signed": False,
            },
            11: {
                "Type": "scpt-float",
                "Signed": False,
            },
            12: {
                "Type": "scpt-float",
                "Signed": False,
            },
            13: {
                "Type": "scpt-float",
                "Signed": False,
            },
            14: {
                "Type": "scpt-float",
                "Signed": False,
            },
            15: {
                "Type": "scpt-float",
                "Signed": False,
            },
            16: {
                "Type": "scpt-float",
                "Signed": False,
            },
            17: {
                "Type": "scpt-float",
                "Signed": False,
            },
            18: {
                "Type": "scpt-float",
                "Signed": False,
            },
            19: {
                "Type": "scpt-float",
                "Signed": False,
            },
            20: {
                "Type": "scpt-float",
                "Signed": False,
            },
            21: {
                "Type": "scpt-float",
                "Signed": False,
            },
            22: {
                "Type": "scpt-float",
                "Signed": False,
            },
            23: {
                "Type": "scpt-float",
                "Signed": False,
            },
            24: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    225: {
        "Location": "0x80213dd0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-int",
                "Signed": False,
            },
            3: {
                "Type": "scpt-int",
                "Signed": False,
            },
            4: {
                "Type": "scpt-int",
                "Signed": False,
            },
            5: {
                "Type": "scpt-int",
                "Signed": False,
            },
            6: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    226: {
        "Location": "0x80213920",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    227: {
        "Location": "0x801feb78",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Name": "PC_ID",
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    228: {
        "Name": "Swap player group",
        "Description": "If the player characters have been split into two groups, this switches the active group.",
        "Location": "0x801feb40",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {}
    },
    229: {
        "Name": "Unify player groups",
        "Description": "If the player characters have been split into two groups, this recombines the two groups into one. Only seems to be used at Daccat's isle, so not sure if it is specific to Aika/Fina and Vyse/Gilder groups, or if it can be used for other groups as well.",
        "Location": "0x801feb08",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {}
    },
    230: {
        "Location": "0x80205a3c",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-float",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    231: {
        "Location": "0x801fdcdc",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    232: {
        "Location": "0x802139f8",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-int",
                "Signed": False,
            },
            3: {
                "Type": "scpt-int",
                "Signed": False,
            },
            4: {
                "Type": "scpt-int",
                "Signed": False,
            },
            5: {
                "Type": "scpt-int",
                "Signed": False,
            },
            6: {
                "Type": "scpt-int",
                "Signed": False,
            },
            7: {
                "Type": "scpt-int",
                "Signed": False,
            },
            8: {
                "Type": "scpt-int",
                "Signed": False,
            },
            9: {
                "Type": "scpt-int",
                "Signed": False,
            },
            10: {
                "Type": "scpt-int",
                "Signed": False,
            },
            11: {
                "Type": "scpt-int",
                "Signed": False,
            },
            12: {
                "Type": "scpt-int",
                "Signed": False,
            },
            13: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    233: {
        "Location": "0x8020cba4",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    234: {
        "Location": "0x801fed3c",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Warning": "This instruction does nothing and returns zero. Instruction not used in the game, may be buggy",
        "Parameters": {}
    },
    235: {
        "Location": "0x8020b80c",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    236: {
        "Location": "0x8020b670",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
            0: {
                "Type": "scpt-float",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-int",
                "Signed": False,
            },
            4: {
                "Type": "scpt-int",
                "Signed": False,
            },
            5: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    237: {
        "Location": "0x801fd54c",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {}
    },
    238: {
        "Location": "0x802074b0",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-float",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    239: {
        "Location": "0x801fd1d0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    240: {
        "Location": "0x801f7d2c",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-int",
                "Signed": False,
            },
            5: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    241: {
        "Location": "0x801f7cd8",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {}
    },
    242: {
        "Location": "0x801fcff0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            2: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    243: {
        "Location": "0x801f9988",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-int",
                "Signed": False,
            },
            7: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            8: {
                "Type": "scpt-byte",
                "Signed": False,
            },
            9: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    244: {
        "Location": "0x8020bee8",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    245: {
        "Location": "0x801ff8d4",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Loop": [1],
        "Loop Iterations": 0,
        "Parameters": {
            0: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-short",
                "Signed": False,
            }
        }
    },
    246: {
        "Location": "0x801ff714",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Loop": [1],
        "Loop Iterations": 0,
        "Parameters": {
            0: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-short",
                "Signed": False,
            }
        }
    },
    247: {
        "Location": "0x801f95c0",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {}
    },
    248: {
        "Location": "0x801f7c18",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Link": 0,
        "Link Type": "String",
        "Parameters": {
            0: {
                "Name": "Offset",
                "Type": "int",
                "Signed": False,
            }
        }
    },
    249: {
        "Location": "0x80208424",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    250: {
        "Location": "0x801f7b14",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": True,
        "Hard parameter two": 0x00010000,
        "Link": 0,
        "Link Type": "String",
        "Parameters": {
            0: {
                "Name": "Offset",
                "Type": "int",
                "Signed": False,
            }
        }
    },
    251: {
        "Location": "0x8020014c",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    252: {
        "Location": "0x802000a0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    253: {
        "Location": "0x801fffa4",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
          0: {
            "Type": "scpt-int",
            "Signed": False,
          },
          1: {
            "Type": "scpt-int",
            "Signed": False,
          }
        }
    },
    254: {
        "Location": "0x802138e0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {}
    },
    255: {
        "Location": "0x802138a0",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Parameters": {}
    },
    256: {
        "Location": "0x801fdc70",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Warning": "Instruction not used in the game, may be buggy",
        "Parameters": {
          0: {
            "Type": "scpt-int",
            "Signed": False,
          }
        }
    },
    257: {
        "Location": "0x80214908",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Link": 0,
        "Link Type": "String",
        "Parameters": {
          0: {
            "Name": "Offset",
            "Type": "int",
            "Signed": False,
          }
        }
    },
    258: {
        "Location": "0x801fd44c",
        "Skip Frame Refresh": 0x00000001,
        "Hard parameter two": 0x00010000,
        "Loop": [1],
        "Loop Iterations": 0,
        "Parameters": {
            0: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    259: {
        "Name": "Hamachou Hermit Stat Dialog",
        "Description": "Helper instruction for Hamachou Hermit. Displays a text box containing current stats of a certain type.\n\nDialog display index: <DISP_ID>\n\nBattles - (0, 1, 10, 2)\nRuns - (3, 4)\nKnocked Unconscious - (5, 6)\nTreasure Chests - (7, 8)\nFish - (9)\n\nTechnically, Domingo's discovery text can also be displayed using this instruction using 100 as the parameter.",
        "Location": "0x8020b4ac",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Name": "DISP_ID",
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    260: {
        "Name": "Restore Ship Health All",
        "Location": "0x801fda70",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {}
    },
    261: {
        "Name": "Domingo Discovery Dialog",
        "Description": "Instruction to display a textbox from Domingo with the current number of discoveries. Uses the same function as INST_259 but with a 100 as the parameter to force Domingo's text.",
        "Location": "0x8020ae04",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {}
    },
    262: {
        "Name": "Activate Screen Overlay",
        "Description": "Fades out into a color as defined below:\n\nRed (0-255): <Red>\nGreen (0-255): <Green>\nBlue (0-255): <Blue>\nDistance from Camera: <Distance>\nTransition Time: <Transition_Time>\n\nDistance in direction camera is pointing is negative, and reverse is positive. Textboxes appear at -1, so distance should be less than -1 to show text boxes.",
        "Location": "0x801fe310",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Parameters": {
            0: {
                "Name": "Red",
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Name": "Green",
                "Type": "scpt-short",
                "Signed": False,
            },
            2: {
                "Name": "Blue",
                "Type": "scpt-short",
                "Signed": False,
            },
            3: {
                "Name": "Distance",
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Name": "Transition_Time",
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    263: {
        "Location": "0x802137d0",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Loop": [1],
        "Loop Iterations": 0,
        "Parameters": {
            0: {
                "Name": "Iterations",
                "Type": "int",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            }
        }
    },
    264: {
        "Location": "0x801f7f98",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00050000,
        "Parameters": {
            0: {
                "Type": "scpt-short",
                "Signed": False,
            },
            1: {
                "Type": "scpt-float",
                "Signed": False,
            },
            2: {
                "Type": "scpt-float",
                "Signed": False,
            },
            3: {
                "Type": "scpt-float",
                "Signed": False,
            },
            4: {
                "Type": "scpt-float",
                "Signed": False,
            },
            5: {
                "Type": "scpt-float",
                "Signed": False,
            },
            6: {
                "Type": "scpt-float",
                "Signed": False,
            },
            7: {
                "Type": "scpt-int",
                "Signed": False,
            }
        }
    },
    265: {
        "Name": "Valuan Piracy List Dialog",
        "Location": "0x8020aaa8",
        "Skip Frame Refresh": 0x00000000,
        "Force Frame Refresh": False,
        "Hard parameter two": 0x00010000,
        "Link": 1,
        "Link Type": "String",
        "Parameters": {
            0: {
                "Type": "scpt-int",
                "Signed": False,
            },
            1: {
                "Type": "int",
                "Signed": True,
            }
        }
    }
}
