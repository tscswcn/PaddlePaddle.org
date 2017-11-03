import json
import os
import re
import codecs

from bs4 import BeautifulSoup
from django.template import Template, Context


OPERATOR_TEMPLATE = '<div class="section" id="{{ type }}"><h3>{{ type }}</h3>' + (
    '<dl class="function"><dd>{% for comment_line in comment %}<p>{{ comment_line }}</p>{% endfor %}') + (
    '<table class="docutils field-list"><colgroup><col class="field-name"><col class="field-body"></colgroup>') + (
    '<tbody valign="top">') + (
    '<tr class="field-odd field"><th class="field-name">Inputs:</th><td class="field-body">') + (
        '<ul class="first simple">{% for input in inputs %}<li><strong>{{ input.name }}</strong> {% if input.duplicable == 1 %}(<em>Duplicable</em>) {% endif %}{% if input.intermediate == 1 %}(<em>Intermediate</em>) {% endif %}: {{ input.comment }}</li>{% endfor %}</ul>') + (
    '</td></tr>') + (
    '<tr class="field-even field"><th class="field-name">Outputs:</th><td class="field-body">') + (
        '<ul class="first simple">{% for output in outputs %}<li><strong>{{ output.name }}</strong> {% if output.duplicable == 1 %}(<em>Duplicable</em>) {% endif %}{% if output.intermediate == 1 %}(<em>Intermediate</em>) {% endif %}: {{ output.comment }}</li>{% endfor %}</ul>') + (
    '</td></tr>') + (
    '{% if attrs|length_is:"0" %}{% else %}<tr class="field-odd field"><th class="field-name">Attributes:</th><td class="field-body">') + (
        '<ul class="first simple">{% for attr in attrs %}<li><strong>{{ attr.name }}</strong> (<em>Duplicable</em>){% if attr.generated == 1 %} (<em>Generated</em>) {% endif %}: {{ attr.comment }}</li>{% endfor %}</ul>') + (
    '</td></tr>{% endif %}') + (
    '</tbody></table></dd></dl></div>')


OPERATORS_WRAPPER = (
    '<div class="document"><h1>Operators</h1><div class="section" id="operators">',
    '</div></div>'
)


def generate_operators_page(operators_api_path, destination_dir):
    operators_output = ''

    try:
        # Open the operators API file.
        with open(operators_api_path) as raw_operators_api_file:
            raw_operators_api = raw_operators_api_file.read()

            operators = clean_json_string(raw_operators_api)

            # Go through all the operators and construct a new HTML object.
            operator_template = Template(OPERATOR_TEMPLATE)

            operators_output += OPERATORS_WRAPPER[0]

            for operator in operators:
                if 'comment' in operator:
                    operator_comment_lines = operator['comment'].split('\n')

                    operator_comment = []
                    for operator_comment_line in operator_comment_lines:
                        if len(operator_comment_line) > 0:
                            operator_comment.append(operator_comment_line)

                    operator['comment'] = operator_comment

                operators_output += operator_template.render(Context(operator))

            operators_output += OPERATORS_WRAPPER[1]

        for lang in ['en', 'zh']:
            operators_output_path = '%s/%s/operators.html' % (destination_dir, lang)

            if not os.path.exists(os.path.dirname(operators_output_path)):
                os.makedirs(os.path.dirname(operators_output_path))

            with codecs.open(operators_output_path, 'w', 'utf-8') as operators_output_file:
                operators_output_file.write(operators_output)

    except Exception, e:
        print 'Failed to build operator docs because: ', e


def clean_json_string(body):
    """
    Takes in a string meant to be interpreted as a JSON object, and removes
    faulty characters, recursively.
    """
    try:
        return json.loads(body)

    except ValueError, e:
        if str(e).startswith('Invalid control character'):
            faulty_character_index = int(re.search(
                'char (?P<column>\d+)', str(e)).group('column'))

            return clean_json_string(
                body[:faulty_character_index] + body[faulty_character_index+1:])
