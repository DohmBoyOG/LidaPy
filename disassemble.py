import extractor
import lua51
import sutil


def match_bytes(bytecode: bytes, test: str) -> bool:
	ok: bool = True

	if len(bytecode) >= len(test):
		for x in range(len(test)):
			if bytecode[x] != ord(test[x]):
				ok = False
				break
	else:
		ok = False

	return ok


def get_proto(bytecode: bytes) -> extractor.LFuncRead:
	if not match_bytes(bytecode, "\x1BLua"):
		raise RuntimeError("File is not Lua bytecode")

	if match_bytes(bytecode, "\x1BLua\x51"):
		result = lua51.L51FuncRead(bytecode[5:])
	else:
		raise NotImplementedError("Lua version not supported")

	return result


def disassemble_bytecode(bytecode: bytes, args) -> str:
	pp: extractor.ProtoPrint = extractor.ProtoPrint()
	lf: extractor.LFuncRead = get_proto(bytecode)

	pp.flags.has_comments = args.comments
	pp.flags.has_lineinfo = not args.nolines
	pp.flags.inl_consts = args.inlconsts
	pp.flags.jmp_optimize = args.smartjumps

	lf.read_function()

	return pp.get_assembly(lf)


def process_query(output, args):
	timer: sutil.LightTimer = sutil.LightTimer()

	for name in args.files:
		with open(name, 'rb') as file:
			code: bytes = file.read()
			timer.restart()

			dis: str = disassemble_bytecode(code, args)

			if args.verbose:
				off: str = timer.pretty()
				pad: str = len(file.name) * ' '
				sz: str = sutil.sizeof_fmt(len(code), 'B')

				dbgp = f'{file.name}: size {sz}\n{pad}: time {off}'
				print(dbgp)

			output.write(dis)
