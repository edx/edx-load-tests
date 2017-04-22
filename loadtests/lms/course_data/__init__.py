import random


class CourseData(dict):
    """
    This object augments plain dictionaries with property accessors for
    use in locust tasks.

    This particular implementation returns random
    selections from pools of parameter values, though implementations
    with more deterministic behavior should be possible as well, without
    needing to change the tasks themselves.

    Tasks should not access the underlying dict directly, instead use or
    add property accessors as needed.
    """
    @staticmethod
    def _random_item(d):
        key = random.choice(d.keys())
        return (key, d[key])

    @property
    def capa_problem(self):
        """
        Return (id, path, inputs) from among capa problems known in this course.
        """
        problem_id, problem = self._random_item(self['capa_problems'])
        input = {}
        if 'inputs' in problem:
            for key, values in problem['inputs'].items():
                input[key] = random.choice(values)
        return (problem_id, problem, input)

one_question = CourseData(
    sequential_ids=(
        'c0a9d2ed32e145d3b131222ed5055e3a',
    ),
    capa_problems={
        '7a7da999efa04da2a1bf0e0a8e659af0': {
            'inputs': {
                '_2_1': ['choice_0', 'choice_1', 'choice_2'],
            },
        },
    }
)

devstack_efischer = CourseData(
    sequential_ids=(
        'd8a6192ade314473a78242dfeedfbf5b',
    ),
    capa_problems={
        '762c58d25dde42dfa1ce18bac56949e6': {
            'inputs': {
                '_2_1': ['choice_0', 'choice_1', 'choice_2'],
            },
        },
    }
)

parsed_data_small = CourseData(
	capa_problems={
		'0088bb2e1a6941e39f2ffa6392d5772d': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'0981d363d78f46de8b07c823b203c6cd': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', ],
			},
		},
		'143aa16524b94850b1258379ed37c251': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'51c52404223640b3b3c3f2b4355564ad': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'62b76118c1004d45af2532ab9ee4e98d': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad1Subsection1Vertical1Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad1Subsection1Vertical2Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad1Subsection1Vertical3Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad1Subsection1Vertical4Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad1Subsection1Vertical5Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad1Subsection1Vertical6Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad2Subsection1Vertical1Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad2Subsection1Vertical2Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad2Subsection1Vertical3Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad2Subsection1Vertical4Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad2Subsection2Vertical1Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad2Subsection3Vertical5Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad2Subsection3Vertical6Problems4': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad2Subsection4Vertical1Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad2Subsection4Vertical1Problems2': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad2Subsection4Vertical1Problems3': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad2Subsection4Vertical1Problems4': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad3Subsection1Vertical1Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', ],
			},
		},
		'Unidad3Subsection3Vertical1Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', ],
			},
		},
		'Unidad3Subsection3Vertical3Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', ],
			},
		},
		'Unidad3Subsection4Vertical1Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', ],
			},
		},
		'Unidad3Subsection4Vertical1Problems2': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', ],
			},
		},
		'Unidad3Subsection4Vertical1Problems3': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', ],
			},
		},
		'Unidad3Subsection4Vertical1Problems4': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', ],
			},
		},
		'Unidad3Subsection4Vertical1Problems5': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', ],
			},
		},
		'Unidad4Subsection1Vertical1Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad4Subsection1Vertical2Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad4Subsection2Vertical1Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad4Subsection2Vertical1Problems10': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad4Subsection2Vertical1Problems2': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad4Subsection2Vertical1Problems3': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad4Subsection2Vertical1Problems4': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad4Subsection2Vertical1Problems5': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad4Subsection2Vertical1Problems6': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad4Subsection2Vertical1Problems7': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad4Subsection2Vertical1Problems8': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad4Subsection2Vertical1Problems9': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad5Subsection1Vertical1Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad5Subsection1Vertical2Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad5Subsection2Vertical1Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad5Subsection3Vertical1Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad5Subsection3Vertical1Problems2': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad5Subsection3Vertical1Problems3': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad5Subsection3Vertical1Problems4': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', ],
			},
		},
		'Unidad5Subsection3Vertical1Problems5': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad6Subsection1Vertical1Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad6Subsection2Vertical1Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad6Subsection3Vertical1Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad6Subsection4Vertical1Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad6Subsection4Vertical1Problems2': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad6Subsection4Vertical1Problems3': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad8Subsection1Vertical1Problems1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad8Subsection1Vertical1Problems10': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad8Subsection1Vertical1Problems2': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad8Subsection1Vertical1Problems3': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', ],
			},
		},
		'Unidad8Subsection1Vertical1Problems4': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', ],
			},
		},
		'Unidad8Subsection1Vertical1Problems5': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad8Subsection1Vertical1Problems6': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad8Subsection1Vertical1Problems7': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad8Subsection1Vertical1Problems8': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'Unidad8Subsection1Vertical1Problems9': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'fc4e2cb94ef14ef59fce97d15851e66c': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
	}
)

parsed_data_medium = CourseData(
	capa_problems={
		'ex_bernoulli_binomial': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', ],
				'_3_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', ],
			},
		},
		'ex_bias_variance': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', ],
			},
		},
		'ex_expectation_multiple_rv': {
			'inputs': {
				'_2_1': ('p', ),
			},
		},
		'ex_gamblers_fallacy': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', ],
			},
		},
		'ex_geo_dist_exp': {
			'inputs': {
				'_2_1': ('p', ),
			},
		},
		'ex_graphical_models': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', 'choice_6', 'choice_7', 'choice_8', 'choice_9', 'choice_10', 'choice_11', ],
				'_3_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', 'choice_6', 'choice_7', 'choice_8', 'choice_9', 'choice_10', 'choice_11', ],
			},
		},
		'ex_info_divergence': {
			'inputs': {
				'_2_1': ('log(k)', ),
				'_3_1': ('log', ),
				'_4_1': ('X', 'U')
			},
		},
		'ex_max_product_complexity': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', 'choice_6', 'choice_7', 'choice_8', 'choice_9', 'choice_10', 'choice_11', 'choice_12', 'choice_13', 'choice_14', 'choice_15', 'choice_16', 'choice_17', ],
				'_3_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', 'choice_6', 'choice_7', 'choice_8', 'choice_9', 'choice_10', 'choice_11', ],
				'_4_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', 'choice_6', 'choice_7', 'choice_8', 'choice_9', 'choice_10', 'choice_11', 'choice_12', 'choice_13', 'choice_14', 'choice_15', 'choice_16', 'choice_17', 'choice_18', 'choice_19', 'choice_20', ],
				'_5_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', 'choice_6', 'choice_7', 'choice_8', 'choice_9', 'choice_10', 'choice_11', 'choice_12', 'choice_13', 'choice_14', 'choice_15', 'choice_16', 'choice_17', ],
			},
		},
		'ex_max_product_sum_product': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', ],
			},
		},
		'ex_modeling_uncertainty': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', ],
				'_3_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', ],
			},
		},
		'ex_shannon_entropy': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', ],
				'_3_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', ],
				'_4_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', ],
			},
		},
		'ex_var_std': {
			'inputs': {
				'_2_1': ('no', ),
			},
		},
		'hw_alien_leaders': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', 'choice_6', 'choice_7', 'choice_8', ],
			},
		},
		'hw_big_o': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', ],
				'_3_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', ],
			},
		},
		'hw_graphical_model_conditional_independence': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', ],
				'_3_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', ],
				'_4_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', ],
				'_5_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', ],
				'_6_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', ],
			},
		},
		'hw_ising_model': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', 'choice_4', 'choice_5', ],
			},
		},
	}
)
