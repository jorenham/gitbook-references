import argparse
import os
import re

import sys
from collections import OrderedDict


def _is_valid_file(arg):
    if not os.path.exists(arg):
        raise argparse.ArgumentTypeError('The file {} does not exist!'.format(arg))
    elif not (arg.endswith('.md') or arg.endswith('.MD')):
        raise argparse.ArgumentTypeError('The file {} should end with .md'.format(arg))
    else:
        return arg


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='Path to the input .md file', type=_is_valid_file)
    parser.add_argument('output_file', help='Path to the output .md file')
    args = parser.parse_args()
    return args


def _extract_references(input_file_path):
    references = OrderedDict()

    with open(input_file_path, 'r') as input_file:
        for line in input_file:
            for reference_number, reference_anchor in re.findall('\[\[(\d+)\]\(#(.*?)\)\]', line):
                references[reference_number] = {'anchor': reference_anchor}

    with open(input_file_path, 'r') as input_file:
        for line in input_file:
            for reference_number, reference in re.findall('(\d+).*id=".*"\s*/>(.*)', line):
                if reference_number in references:
                    references[reference_number]['reference'] = reference
                else:
                    warn_msg = 'Warning: Reference {} ({}) not referenced in text'.format(reference_number, reference)
                    print(warn_msg, file=sys.stderr)

    return references


def _replace_references(input_file_path, output_file_path, references):
    with open(input_file_path, 'r') as input_file:
        body = input_file.read()

    reference_number_new = 1
    for reference_number, reference_dict in references.items():
        anchor = reference_dict['anchor']
        body = re.sub(
            '\[\[({})\]\(#({})\)\]'.format(reference_number, anchor),
            '[[{}]({})]'.format(reference_number_new, anchor),
            body
        )

        if 'reference' in reference_dict:
            reference = reference_dict['reference']
            body = re.sub(
                '{}.*id="{}"\s*/>{}'.format(reference_number, anchor, re.escape(reference)),
                '{}. <div id="{}" />{}'.format(reference_number_new, anchor, reference),
                body
            )

            reference_number_new += 1

    with open(output_file_path, 'w') as output_file:
        output_file.write(body)


def main():
    args = _parse_args()
    input_file_path = args.input_file
    output_file_path = args.output_file

    references = _extract_references(input_file_path)
    _replace_references(input_file_path, output_file_path, references)


if __name__ == '__main__':
    main()
