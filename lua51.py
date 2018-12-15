from luabase import *


def set_table_cmt(args: list):
	return f"{args[0]}[{args[1]}] := {args[2]}"


def self_cmt(args: list):
	return f"({args[0]} + 1) = {args[1]}; {args[0]} = {args[1]}[{args[2]}]"


def eq_cmt(args: list):
	if args[0] == '0':
		cmp = '!='
	else:
		cmp = '=='

	return f"if ({args[1]} {cmp} {args[2]}) -> jmp"


def lt_cmt(args: list):
	if args[0] == '0':
		cmp = '<'
	else:
		cmp = '>'

	return f"if not ({args[1]} {cmp} {args[2]}) -> jmp"


def le_cmt(args: list):
	if args[0] == '0':
		cmp = '<='
	else:
		cmp = '>='

	return f"if not ({args[1]} {cmp} {args[2]}) -> jmp"


def test_cmt(args: list):
	if args[1] == '0':
		cmp = 'not '
	else:
		cmp = ''

	return f"if ({cmp}{args[0]}) -> jmp"


def testset_cmt(args: list):
	if args[2] == '0':
		cmp = 'not '
	else:
		cmp = ''

	return f"if ({cmp}{args[1]}) -> {args[0]} = {args[1]}"


def call_cmt(args: list):
	call: str = ''
	a: str = args[0]
	b: int = int(args[1])
	c: int = int(args[2])

	if c != 1:
		if c == 0:
			call = f"{a}... = "
		elif c == 2:
			call = f"{a} = "
		else:
			call = f"{a}, +{c - 2} = "

	call = f"{call}{a}("

	if b != 1:
		if b == 0:
			call = f"{call}..."
		else:
			call = f"{call}+{b - 1}"

	return call + ")"


def ret_cmt(args: list):
	ret: str = ''
	b: int = int(args[1])

	if b != 1:
		if b == 0:
			ret = " ..."
		elif b == 2:
			ret = f" {args[0]}"
		else:
			ret = f" {args[0]}, +{b - 2}"

	return "return" + ret


def vararg_cmt(args: list):
	b: int = int(args[1])
	varg: str = ''

	if b == 0:
		varg = "..."
	elif b == 1:
		varg = "???"
	elif b != 2:
		varg = f", +{b - 2}"

	return f"{args[0]}{varg} = ..."


LUA51_OPMODE = [
	OpMode("MOVE", a="OpArgR", b="OpArgR"),
	OpMode("LOADK", a="OpArgR", b="OpArgK", o="iABx"),
	OpMode("LOADBOOL", a="OpArgR", b="OpArgU", c="OpArgU"),
	OpMode("LOADNIL", a="OpArgR", b="OpArgR"),
	OpMode("GETUPVAL", a="OpArgR", b="OpArgS"),
	OpMode("GETGLOBAL", a="OpArgR", b="OpArgK", o="iABx"),
	OpMode("GETTABLE", a="OpArgR", b="OpArgR", c="OpArgK"),
	OpMode("SETGLOBAL", a="OpArgR", b="OpArgK", o="iABx"),
	OpMode("SETUPVAL", a="OpArgR", b="OpArgS"),
	OpMode("SETTABLE", a="OpArgR", b="OpArgK", c="OpArgK", cb=set_table_cmt),
	OpMode("NEWTABLE", a="OpArgR", b="OpArgU",   c="OpArgU"),
	OpMode("SELF", a="OpArgR", b="OpArgR", c="OpArgK", cb=self_cmt),
	OpMode("ADD", a="OpArgR", b="OpArgK", c="OpArgK"),
	OpMode("SUB", a="OpArgR", b="OpArgK", c="OpArgK"),
	OpMode("MUL", a="OpArgR", b="OpArgK", c="OpArgK"),
	OpMode("DIV", a="OpArgR", b="OpArgK", c="OpArgK"),
	OpMode("MOD", a="OpArgR", b="OpArgK", c="OpArgK"),
	OpMode("POW", a="OpArgR", b="OpArgK", c="OpArgK"),
	OpMode("UNM", a="OpArgR", b="OpArgR"),
	OpMode("NOT", a="OpArgR", b="OpArgR"),
	OpMode("LEN", a="OpArgR", b="OpArgR"),
	OpMode("CONCAT", a="OpArgR", b="OpArgR", c="OpArgR"),
	OpMode("JMP", b="OpArgJ", o="iAsBx"),
	OpMode("EQ", a="OpArgU", b="OpArgK", c="OpArgK", cb=eq_cmt),
	OpMode("LT", a="OpArgU", b="OpArgK", c="OpArgK", cb=lt_cmt),
	OpMode("LE", a="OpArgU", b="OpArgK", c="OpArgK", cb=le_cmt),
	OpMode("TEST", a="OpArgR", b="OpArgN", c="OpArgU", cb=test_cmt),
	OpMode("TESTSET", a="OpArgR", b="OpArgR", c="OpArgU", cb=testset_cmt),
	OpMode("CALL", a="OpArgR", b="OpArgU", c="OpArgU", cb=call_cmt),
	OpMode("TAILCALL", a="OpArgR", b="OpArgU", c="OpArgU", cb=call_cmt),
	OpMode("RETURN", a="OpArgR", b="OpArgU", cb=ret_cmt),
	OpMode("FORLOOP",  a="OpArgR", b="OpArgJ", o="iAsBx"),
	OpMode("FORPREP", a="OpArgR", b="OpArgJ", o="iAsBx"),
	OpMode("TFORLOOP", a="OpArgR", c="OpArgU"),
	OpMode("SETLIST", a="OpArgR", b="OpArgU", c="OpArgU"),
	OpMode("CLOSE", a="OpArgR"),
	OpMode("CLOSURE", a="OpArgR", b="OpArgP", o="iABx"),
	OpMode("VARARG", a="OpArgR", b="OpArgU", cb=vararg_cmt),
	OpMode("EXTRAARG", a="OpArgU", o="iX")
]


class L51Function(LFunction):
	def read_header(self):
		self.version = 0x51
		self.format = self.read_byte()
		self.endian = self.read_byte()
		self.int = self.read_byte()
		self.size_t = self.read_byte()
		self.Instruction = self.read_byte()
		self.lua_Number = self.read_byte()
		self.integral = self.read_byte()

	def read_lstring(self) -> str:
		size = self.read_size_t()
		result: str = None

		if size == 1:
			result = ''
			self.read_byte()
		elif size > 1:
			result = self.read_string(size - 1)
			self.read_byte()

		return result

	def read_code(self) -> list:
		size: int = self.read_int()
		codelist: list = [None] * size
		is_fake: bool = False

		for x in range(size):
			i = self.read_Instruction()
			ki: Instruction = Instruction(i, LUA51_OPMODE)

			if is_fake:
				ki.data = LUA51_OPMODE[-1]
				is_fake = False
			elif ki.data.name == "SETLIST" and ki.val_c() == 0:
				is_fake = True

			codelist[x] = ki

		return codelist

	def read_consts(self) -> list:
		size: int = self.read_int()
		consts: list = [None] * size

		for x in range(size):
			tt: int = self.read_byte()
			tv: TValue = TValue()
			tv.tt = tt

			if tt != LuaKTypes.TNIL:
				if tt == LuaKTypes.TBOOLEAN:
					tv.vbool = self.read_byte() != 0
				elif tt == LuaKTypes.TNUMBER:
					tv.vflt = self.read_lua_Number()
				elif tt == LuaKTypes.TSTRING:
					tv.vstr = self.read_lstring()

			consts[x] = tv

		return consts

	def read_protos(self) -> list:
		size: int = self.read_int()
		protos: list = [None] * size

		for x in range(size):
			protos[x] = self.read_proto()

		return protos

	def read_lineinfo(self) -> list:
		size: int = self.read_int()
		lineinfo: list = [None] * size

		for x in range(size):
			lineinfo[x] = self.read_int()

		return lineinfo

	def read_locals(self) -> list:
		size: int = self.read_int()
		locvars: list = [None] * size

		for x in range(size):
			lv: LocVar = LocVar()
			lv.varname = self.read_lstring()
			lv.startpc = self.read_int()
			lv.endpc = self.read_int()
			locvars[x] = lv

		return locvars

	def read_upvalues(self) -> list:
		size: int = self.read_int()
		upvals: list = [None] * size

		for x in range(size):
			uv: Upvalue = Upvalue()
			uv.name = self.read_lstring()
			upvals[x] = uv

		return upvals

	def read_proto(self) -> Proto:
		p: Proto = Proto()
		p.source = self.read_lstring()
		p.linedefined = self.read_int()
		p.lastlinedefined = self.read_int()

		p.nups = self.read_byte()
		p.numparams = self.read_byte()
		self.read_byte()  # is_vararg
		self.read_byte()  # maxstacksize

		p.code = self.read_code()
		p.k = self.read_consts()
		p.p = self.read_protos()
		p.lineinfo = self.read_lineinfo()
		p.locvars = self.read_locals()
		p.upvalues = self.read_upvalues()

		return p
