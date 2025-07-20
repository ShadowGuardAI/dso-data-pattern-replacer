#!/usr/bin/env python3

import argparse
import re
import logging
import os
import chardet
from faker import Faker

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def setup_argparse():
    """
    Sets up the argument parser for the command-line interface.
    """
    parser = argparse.ArgumentParser(description="Finds and replaces data matching a regular expression pattern with a specified replacement string.")

    parser.add_argument("input_file", help="The input file to process.")
    parser.add_argument("pattern", help="The regular expression pattern to search for.")
    parser.add_argument("replacement", help="The replacement string. Use 'faker.name', 'faker.email', etc. for dynamic faker values.")
    parser.add_argument("-o", "--output_file", help="The output file to write to. If not specified, overwrites the input file.", default=None)
    parser.add_argument("-e", "--encoding", help="The encoding of the input file. If not specified, attempts to detect it.", default=None)
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose logging.")
    parser.add_argument("-n", "--dry_run", action="store_true", help="Perform a dry run without writing changes.")


    return parser

def detect_encoding(file_path):
    """
    Detects the encoding of a file.
    """
    try:
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
        return result['encoding']
    except Exception as e:
        logging.error(f"Error detecting encoding: {e}")
        return None

def process_file(input_file, pattern, replacement, output_file=None, encoding=None, dry_run=False):
    """
    Processes the input file, replaces data matching the pattern, and writes the output.
    """
    try:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")

        if encoding is None:
            encoding = detect_encoding(input_file)
            if encoding is None:
                encoding = 'utf-8' # Default to utf-8 if detection fails
                logging.warning("Could not detect encoding, defaulting to utf-8.")

        try:
            with open(input_file, 'r', encoding=encoding) as f:
                data = f.read()
        except UnicodeDecodeError as e:
            raise ValueError(f"Error decoding file with encoding {encoding}: {e}")

        # Use faker to dynamically generate replacement values
        fake = Faker()
        replacement_string = ""
        if replacement.startswith("faker."):
            try:
                replacement_string = eval(f"fake.{replacement[6:]}")
            except AttributeError:
                logging.error(f"Invalid faker attribute: {replacement[6:]}. Using literal replacement.")
                replacement_string = replacement
            except Exception as e:
                logging.error(f"Error while executing faker call. Using literal replacement. Error: {e}")
                replacement_string = replacement

        else:
            replacement_string = replacement


        # Validate pattern
        try:
            re.compile(pattern)  # Attempt to compile the regex
        except re.error as e:
            raise ValueError(f"Invalid regular expression pattern: {e}")

        new_data = re.sub(pattern, str(replacement_string), data)

        if dry_run:
            logging.info("Dry run: No changes will be written.")
            num_replacements = len(re.findall(pattern, data))
            logging.info(f"Dry run complete.  Would have made {num_replacements} replacements.")
            return

        if output_file is None:
            output_file = input_file

        try:
            with open(output_file, 'w', encoding=encoding) as f:
                f.write(new_data)
            logging.info(f"Successfully processed file: {input_file}. Output written to: {output_file}")

        except Exception as e:
            raise IOError(f"Error writing to output file: {e}")

    except FileNotFoundError as e:
        logging.error(e)
    except ValueError as e:
        logging.error(e)
    except IOError as e:
        logging.error(e)
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


def main():
    """
    Main function to execute the data pattern replacer.
    """
    parser = setup_argparse()
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)  # Set logging level to DEBUG

    logging.debug(f"Input file: {args.input_file}")
    logging.debug(f"Pattern: {args.pattern}")
    logging.debug(f"Replacement: {args.replacement}")
    logging.debug(f"Output file: {args.output_file}")
    logging.debug(f"Encoding: {args.encoding}")
    logging.debug(f"Dry run: {args.dry_run}")


    process_file(args.input_file, args.pattern, args.replacement, args.output_file, args.encoding, args.dry_run)

if __name__ == "__main__":
    main()