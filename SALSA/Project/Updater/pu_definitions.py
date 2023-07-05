from SALSA.Project.Updater.pu_constants import PP, UP

v2 = {
    PP.project: {
        1: {
            UP.callable: '_change_attribute_names',
            UP.arguments: [
                ('scripts', 'scts'),
            ]
        },
    },
    PP.script: {
        1: {
            UP.callable: '_change_attribute_names',
            UP.arguments: [
                ('sections', 'sects'),
                ('sections_grouped', 'sect_tree'),
                ('sections_ungrouped', 'sect_list'),
                ('folded_sections', 'folded_sects')
            ]
        },
        2: {
            UP.callable: '_modify_section_groups_v1',
        },
    },
    PP.section: {
        1: {
            UP.callable: '_change_attribute_names',
            UP.arguments: [
                ('instructions', 'insts'),
                ('instruction_ids_ungrouped', 'inst_list'),
                ('instruction_ids_grouped', 'inst_tree'),
                ('instructions_used', 'insts_used')
            ]
        },
    },
    PP.instruction: {
        1: {
            UP.callable: '_change_attribute_names',
            UP.arguments: [
                ('instruction_id', 'base_id'),
                ('parameters', 'params'),
                ('loop_parameters', 'l_params'),
                ('frame_delay_param', 'delay_param')
            ]
        },
    },
    PP.parameter: {
        1: {
            UP.callable: '_retype_link_v1'
        },
        2: {
            UP.callable: '_del_attr',
            UP.arguments: ['link_value']
        }
    }
}

update_tasks = {
    1: v2
}

p_max_depth = {
    1: PP.parameter
}