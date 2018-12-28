import argparse
import sys

# import assemble
import disassemble
import sutil


def get_out_file(args):
	if args.echo:
		file = sys.stdout
	else:
		file = open(args.output, 'w', encoding=sutil.ASCII_ISO)

	return file


parser = argparse.ArgumentParser(
	description='The Lida assembler service for Lua',
	allow_abbrev=True
)

# Argument groups
action = parser.add_mutually_exclusive_group()
g_assembler = parser.add_argument_group('assembler')
g_disassembler = parser.add_argument_group('disassembler')
output = parser.add_argument_group('output')
where = output.add_mutually_exclusive_group()

action.add_argument(
	'-a', '--assemble',
	action='store_true',
	help='assemble a file into bytecode'
)

action.add_argument(
	'-d', '--disassemble',
	action='store_true',
	help='disassemble a file into listing'
)

parser.add_argument(
	'-v', '--verbose',
	action='store_true',
	help='show debug information'
)

# Disassembler
g_disassembler.add_argument(
	'-C', '--comments',
	action='store_true',
	help='show comments on complex instructions'
)

g_disassembler.add_argument(
	'-L', '--nolines',
	action='store_true',
	help='hide line info behind instructions'
)

g_disassembler.add_argument(
	'-I', '--inlconsts',
	action='store_true',
	help='inlines use of constants in instructions'
)

g_disassembler.add_argument(
	'-J', '--smartjumps',
	action='store_true',
	help='simplify labels for unoptimized JMPs'
)

# Output stuff
where.add_argument(
	'-o', '--output',
	type=str,
	metavar='file',
	default='lida.out',
	help='set the output file for assembly and disassembly (default: lida.out)'
)

where.add_argument(
	'-e', '--echo',
	action='store_true',
	help='outputs to stdout instead of a file'
)

output.add_argument(
	'files',
	type=str,
	nargs='+',
	help='file names to load'
)

arg_list = parser.parse_args()

if arg_list.assemble:
	raise NotImplementedError("Assembler is not yet implemented")
	# process = assemble.process_query
elif arg_list.disassemble:
	process = disassemble.process_query
else:
	process = None  # silence warning
	parser.error('expected a mode')

output = get_out_file(arg_list)
timer = sutil.LightTimer()
process(output, arg_list)

if output != sys.stdout:
	output.close()

if arg_list.verbose:
	print(f"Finished in {timer.pretty()}")
