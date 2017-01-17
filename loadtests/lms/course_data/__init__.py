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
