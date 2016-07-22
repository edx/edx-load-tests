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
    def courseware_path(self):
        """
        Get a path that can be used to exercise the courseware index page.
        """
        return random.choice(self['courseware_paths'])

    @property
    def video_module_id(self):
        """
        Randomly select an id from among video modules known in this course.
        """
        return random.choice(self['video_module_ids'])

    @property
    def video_id(self):
        """
        Randomly select an id from among video assets known in this course.
        """
        return random.choice(self['video_ids'])

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

    @property
    def sequential_id(self):
        """
        Randomly select an id from among sequentials known in this course.
        """
        return random.choice(self['sequential_ids'])

    @property
    def html_usage_id(self):
        """
        randomly choose the usage_id of an HTML module
        """
        return random.choice(self['html_usage_ids'])


# data extracted from edX/DemoX/Demo_Course as of Feb. 2015
demo_course = CourseData(
    sequential_ids=(
        "edx_introduction",
        "basic_questions",
        "175e76c4951144a29d46211361266e0e",
        "dbe8fc027bcb4fe9afb744d2e8415855",
        "6ab9c442501d472c8ed200e367b4edfa",
        "workflow",
        "48ecb924d7fe4b66a230137626bfa93e",
        "19a30717eff543078a5d94ae9d6c18a5",
        "simulations",
        "graded_simulations",
    ),
    capa_problems={
        'd1b84dcd39b0423d9e288f27f0f7f242': {
            'inputs': {
                '_2_1': ['choice_0'],
            },
        },
        '303034da25524878a2e66fb57c91cf85': {
            'inputs': {
                '_2_1': ['choice_0'],
            },
        },
        '75f9562c77bc4858b61f907bb810d974': {
            'inputs': {
                '_2_1': ['3.1415'],
                '_3_1': ['4518'],
                '_4_1': ['5'],
            },
            'showanswer': 'always',
        },
        'free_form_simulation': {
            'inputs': {
                '_2_1': ['[["o",[32,608,0],{"A":"30000","_json_":0},["6","5","4","3"]],["i",[-152,1240,0],{"value":"dc(1)","_json_":1},["2","1"]],["view",-464.425048828125,-14.073486328125,0.5242880000000001,"50","10","1G",null,"100","1","1000"]]'],
            },
            'showanswer': 'always',
        },
        'python_grader': {
        },
        '9cee77a606ea4c1aa5440e0ea5d0f618': {
            'inputs': {
                '_2_1[]': ['choice_1', 'choice_2', 'choice_3'],
            },
            'showanswer': 'always',
        },
        '651e0945b77f42e0a4c89b8c3e6f5b3b': {
            'inputs': {
                '_2_1': ['3.1415'],
            },
            'showanswer': 'always',
        },
        'ex_practice_limited_checks': {
            'inputs': {
                '_2_1': ('1', '2', '3', '4'),
            },
            'showanswer': 'always',
        },
        'Sample_ChemFormula_Problem': {
            'inputs': {
                '_2_1': ['H2SO4 -> H^+ + HSO4^-'],
            },  # TODO handle input_ajax
            'showanswer': 'always',
        },
        'Sample_Algebraic_Problem': {
            'inputs': {
                '_2_1': ['A*x^2 + sqrt(y)'],
                '_2_1_dynamath': ['<math xmlns="http://www.w3.org/1998/Math/MathML">\r\n  <mstyle displaystyle="true">\r\n    <mi>A</mi>\r\n    <mo>&#x22C5;</mo>\r\n    <msup>\r\n      <mi>x</mi>\r\n      <mn>2</mn>\r\n    </msup>\r\n    <mo>+</mo>\r\n    <msqrt>\r\n      <mrow>\r\n        <mi>y</mi>\r\n      </mrow>\r\n    </msqrt>\r\n  </mstyle>\r\n</math>'],
            },
            'showanswer': 'always',
        },
        '0d759dee4f9d459c8956136dbde55f02': {
            'inputs': {
                '_2_1': ('germany', 'france'),
            },
            'showanswer': 'always',
        },
        '45d46192272c4f6db6b63586520bbdf4': {
            'inputs': {
                '_2_1': ('0', '1'),
            },
            'showanswer': 'always',
        },
        'd2e35c1d294b4ba0b3b1048615605d2a': {
            'inputs': {
                '_2_1': ['[{"1":[69.51666259765625,163.16668701171875]},{"2":[301.51666259765625,155.16668701171875]},{"3":[541.5166625976562,145.16668701171875]},{"4":[442.51666259765625,166.16668701171875]},{"5":[537.5166625976562,176.16668701171875]},{"6":[174.51666259765625,141.16668701171875]},{"7":[437.51666259765625,152.16668701171875]},{"8":[188.51666259765625,154.16668701171875]},{"9":[298.51666259765625,152.16668701171875]},{"10":[553.5166625976562,151.16668701171875]}]'],
            },
            'showanswer': 'always',
        },
        'ex_practice_3': {
            'inputs': {
                '_2_1': ('100', '200', '299', 'x'),
            },
            'showanswer': 'always',
        },
        '932e6f2ce8274072a355a94560216d1a': {
            'inputs': {
                '_2_1': ('choice_1', 'choice_2'),
            },
            'showanswer': 'always',
        },
        '700x_proteinmake': {
        },
        'c554538a57664fac80783b99d9d6da7c': {
            'inputs': {
                '_2_1': ['[443,210]'],
            },
            'showanswer': 'always',
        },
        'a0effb954cca4759994f1ac9e9434bf4': {
            'inputs': {
                '_2_1': ['blue'],
                '_3_1': ['choice_2'],
                '_4_1[]': ['choice_2'],
            },
            'showanswer': 'always',
        },
        'ex_practice_2': {
            'inputs': {'_2_1': ['24']},
            'showanswer': 'always',
        },
        'logic_gate_problem': {
            'inputs': {'_2_1': ['[["w",[128,192,112,192]],["w",[104,192,112,192]],["s",[112,192,0],{"color":"blue","offset":"5","plot offset":"0","_json_":2},["C"]],["w",[128,144,112,144]],["w",[104,144,112,144]],["s",[112,144,0],{"color":"green","offset":"10","plot offset":"0","_json_":5},["B"]],["w",[104,96,112,96]],["s",[112,96,0],{"color":"red","offset":"15","plot offset":"0","_json_":7},["A"]],["w",[192,96,192,112]],["w",[96,192,104,192]],["L",[96,192,2],{"label":"C","_json_":10},["C"]],["w",[96,144,104,144]],["L",[96,144,2],{"label":"B","_json_":12},["B"]],["w",[96,96,104,96]],["L",[96,96,2],{"label":"A","_json_":14},["A"]],["v",[96,48,1],{"name":"Vpwr","value":"dc(3)","_json_":15},["1","0"]],["v",[96,96,1],{"name":"VA","value":"square(3,0,1000K)","_json_":16},["A","0"]],["v",[96,144,1],{"name":"VB","value":"square(3,0,500K)","_json_":17},["B","0"]],["v",[96,192,1],{"name":"VC","value":"square(3,0,250K)","_json_":18},["C","0"]],["g",[32,224,0],{"_json_":19},["0"]],["w",[32,48,48,48]],["w",[48,96,32,96]],["w",[32,48,32,96]],["w",[48,144,32,144]],["w",[32,96,32,144]],["w",[48,192,32,192]],["w",[32,224,32,192]],["w",[32,144,32,192]],["r",[192,48,0],{"name":"Rpullup","r":"10K","_json_":28},["1","Z"]],["L",[256,96,3],{"label":"Z","_json_":29},["Z"]],["w",[96,48,192,48]],["w",[32,224,192,224]],["s",[240,96,0],{"color":"cyan","offset":"","plot offset":"0","_json_":32},["Z"]],["w",[192,96,240,96]],["w",[256,96,240,96]],["w",[112,96,128,96]],["view",-7.099999999999994,6,1.953125,null,"10","10MEG",null,"100","4us",null]]']},
            'showanswer': 'always',
        },
        '700x_editmolB': {
            'inputs': {'_2_1': ['{"mol":"NCCc1ccc(O)c(O)c1\\nJME 2013.01 Mon Dec 22 16:55:14 GMT-500 2014\\n \\n 11 11  0  0  0  0  0  0  0  0999 V2000\\n    7.2746    0.0000    0.0000 N   0  0  0  0  0  0  0  0  0  0  0  0\\n    0.0000    2.8000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0\\n    0.0000    0.0000    0.0000 O   0  0  0  0  0  0  0  0  0  0  0  0\\n    2.4250    2.8000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\\n    3.6373    2.1000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\\n    2.4250    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\\n    6.0621    0.7000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\\n    4.8498    0.0000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\\n    1.2125    2.1000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\\n    1.2125    0.7000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\\n    3.6373    0.7000    0.0000 C   0  0  0  0  0  0  0  0  0  0  0  0\\n  1  7  1  0  0  0  0\\n  2  9  1  0  0  0  0\\n  3 10  1  0  0  0  0\\n  4  5  1  0  0  0  0\\n  4  9  2  0  0  0  0\\n  5 11  2  0  0  0  0\\n  6 10  2  0  0  0  0\\n  6 11  1  0  0  0  0\\n  7  8  1  0  0  0  0\\n  8 11  1  0  0  0  0\\n  9 10  1  0  0  0  0\\nM  END\\n","info":["Hydrophobicity index = 0.490","Can Make Strong Hydrogen Bonds","Can not Make Ionic Bonds"],"error":""}']},
            'showanswer': 'always',
        },
    },
    video_module_ids=(
        "5c90cffecd9b48b188cbfea176bf7fe9",
        "636541acbae448d98ab484b028c9a7f6",
        "7e9b434e6de3435ab99bd3fb25bde807",
        "edX_Introduction",
    ),
    video_ids=(
        "CCxmtcICYNc",
        "o2pLltkrhGM",
        "OEoXaMPEzfM",
        "oX46YqHWgyw",
        "qWxm7CA2v24",
    ),
    courseware_paths=(
        '',
        '/d8a6192ade314473a78242dfeedfbf5b/edx_introduction/',
        '/interactive_demonstrations/19a30717eff543078a5d94ae9d6c18a5/',
        '/interactive_demonstrations/basic_questions/',
        '/graded_interactions/simulations/',
        '/graded_interactions/graded_simulations/',
        '/graded_interactions/175e76c4951144a29d46211361266e0e/',
        '/social_integration/48ecb924d7fe4b66a230137626bfa93e/',
        '/social_integration/dbe8fc027bcb4fe9afb744d2e8415855/',
        '/social_integration/6ab9c442501d472c8ed200e367b4edfa/',
        '/1414ffd5143b4b508f739b563ab468b7/workflow/',
        '/interactive_demonstrations/basic_questions/4',
    ),
    html_usage_ids=(  # Note that this is not currently an exhaustive list.
        'i4x://edX/DemoX/html/030e35c4756a4ddc8d40b95fbbfff4d4',
    ),
)
