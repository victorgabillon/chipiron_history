import argparse
import yaml
from chipiron.utils.small_tools import dict_alphabetic_str
from datetime import datetime


class MyParser:

    def __init__(self, parser):
        self.parser = parser  # TODO not clear what it is, it always argparse?

        # attributes to be set and saved at runtime
        self.args_command_line = None
        self.args_config_file = None
        self.merged_args = None

    def parse_command_line_arguments(self):
        args_obj, unknown = self.parser.parse_known_args()
        args_command_line = vars(args_obj)  # converting into dictionary format
        self.args_command_line = {key: value for key, value in args_command_line.items() if value is not None}
        print('Here are the command line arguments of the script', self.args_command_line)

    def parse_config_file_arguments(self, config_file_path: str) -> None:

        try:

            with open(config_file_path, "r") as exp_options_file:
                try:
                    args_config_file = yaml.safe_load(exp_options_file)
                    args_config_file = {} if args_config_file is None else args_config_file
                    print('Here are the yaml file arguments of the script', args_config_file)
                except yaml.YAMLError as exc:
                    print(exc)
        except IOError:
            raise Exception("Could not read file:", config_file_path)
        self.args_config_file = args_config_file

    def parse_arguments(self,
                        default_param_dict: dict,
                        base_experiment_output_folder,
                        gui_args=None,
                        ):
        for key, value in default_param_dict.items():
            self.parser.add_argument('--' + key, type=type(value), default=None,
                                     help='type of nn to learn')  # TODO help seems wrong

        if gui_args is None:
            gui_args = {}

        self.parse_command_line_arguments()

        config_file_path = None
        if 'config_file_name' in self.args_command_line:
            config_file_path = self.args_command_line['config_file_name']
        elif 'config_file_name' in default_param_dict:
            config_file_path = default_param_dict['config_file_name']

        if config_file_path is None:
            self.args_config_file = {}
        else:
            self.parse_config_file_arguments(config_file_path)

        #  the gui input  overwrite  the command line arguments
        #  that overwrite the config file arguments that overwrite the default arguments
        self.merged_args = default_param_dict | self.args_config_file | self.args_command_line | gui_args
        print('Here are the merged arguments of the script', self.merged_args)

        try:
            assert (set(default_param_dict.keys()) == set(self.merged_args.keys()))
        except AssertionError as error:
            raise Exception(
                'Please have the set of defaults arguments equals the set of given arguments: {} and {}  || diffs {} {}'.format(
                    default_param_dict.keys(), self.merged_args.keys(),
                    set(default_param_dict.keys()).difference(set(self.merged_args.keys())),
                    set(self.merged_args.keys()).difference(set(default_param_dict.keys()))
                )
            ) from error

        if 'output_folder' not in self.merged_args:
            now = datetime.now()  # current date and time
            self.merged_args['experiment_output_folder'] = base_experiment_output_folder + now.strftime(
                "%A-%m-%d-%Y--%H:%M:%S:%f")
        else:
            self.merged_args['experiment_output_folder'] = base_experiment_output_folder + self.merged_args[
                'output_folder']

        return self.merged_args

    def log_parser_info(self, output_folder):
        with open(output_folder + '/parser_output.txt', 'w') as parser_output:
            parser_output.write('This are the logs of the parsing.\n\n')
            parser_output.write(
                f'Command line parameters are:\n{dict_alphabetic_str(self.args_command_line)}\n\n'
            )
            parser_output.write(
                f'Config file parameters are:\n{dict_alphabetic_str(self.args_config_file)}\n\n'
            )
            parser_output.write(f'Merged parameters are:\n{dict_alphabetic_str(self.merged_args)}\n\n')


def create_parser() -> MyParser:
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    return MyParser(parser)
