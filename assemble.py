import sutil


def assemble_code(code: str) -> list:  # returns a "list" of protos
	pass


def finish_write(output, funcs: list):
	pass  # TODO: Pass through list and write to binary


def process_query(output, args):
	timer: sutil.LightTimer = sutil.LightTimer()
	funcs: list = []  # pile up funcs for final assembling

	for name in args.files:
		with open(name, 'r', sutil.ASCII_ISO) as file:
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
