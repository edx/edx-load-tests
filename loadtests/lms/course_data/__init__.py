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

parsed_data = CourseData(
	sequential_ids=(
		'0a0a18ba9db441c5a19208f13a021beb',
		'58aff1584cf5469a86e901eb46f63f38',
		'705f2eee6eee4657bd1a3dcc29c197a3',
		'e1c1cbd4a4f94b0aa0f3746ae0c13837',
	),
	capa_problems={
		'37aa2bde29204ed6980dd9fd0e400da1': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'4928eed5716747c1b6384452b0c1f92a': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'67fd6fe0f9b7442ea6471fe7e02a4391': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'752df0d013c84489b0f09dc5fcd91180': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'7a7da999efa04da2a1bf0e0a8e659af0': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'881382d4c1f34250b8a120674fbb5195': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
		'a40b30b5b7f14abcafee4022c392fd15': {
			'inputs': {
				'_2_1': ['choice_0', 'choice_1', 'choice_2', 'choice_3', ],
			},
		},
	}
)
