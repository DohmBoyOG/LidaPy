import sutil
import asmlexer
import asmparser


def assemble_code(code: str) -> list:  # returns a "list" of protos
	source: asmlexer.SourceCode = asmlexer.SourceCode()
	lexer: asmlexer.AsmLexer = asmlexer.AsmLexer()
	collapser: asmlexer.AsmLexCollapser = asmlexer.AsmLexCollapser()
	parser: asmparser.AsmParser = asmparser.AsmParser()

	source.set_source(code)
	lexer.set_source(source)
	collapser.set_source(source)
	parser.set_source(source)

	lexer.simple_lex()

	collapser.set_tokens(lexer.output)
	collapser.collapse_lex()

	parser.set_tokens(collapser.output)
	parser.parse_protos()

	return parser.protos


def finish_write(output, funcs: list):
	pass  # TODO: Pass through list and write to binary


def process_query(output, args):
	timer: sutil.LightTimer = sutil.LightTimer()
	funcs: list = []  # pile up funcs for final assembling

	for name in args.files:
		with open(name, 'r', encoding=sutil.ASCII_ISO) as file:
			asm: str = file.read()
			timer.restart()

			funcs.append(assemble_code(asm))

			if args.verbose:
				off: str = timer.pretty()
				pad: str = len(file.name) * ' '
				sz: str = sutil.sizeof_fmt(len(asm), 'B')

				dbgp = f'{file.name}: size {sz}\n{pad}: time {off}'
				print(dbgp)

	finish_write(output, funcs)
