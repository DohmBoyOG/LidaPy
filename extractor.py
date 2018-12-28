from luabase import *


def get_lnspace(what: str, ln: int) -> str:
	return what + ' ' * (ln - len(what))


def safe_len(what: str, prev: int):
	if what and len(what) >= prev:
		slen = len(what) + 2
	else:
		slen = prev

	return slen


def extract_uv(uv: int, p: Proto) -> str:
	if len(p.upvalues) > uv:
		result = p.upvalues[uv].uid
	else:
		result = "u" + str(uv)

	return result


def extract_r(r: int, p: Proto) -> str:
	if len(p.locvars) > r:
		result = p.locvars[r].uid
	else:
		result = 'r' + str(r)

	return result


def easy_resolve_jmp(b: int, pc: int, lmtx: dict):
	land: int = b + pc + 1  # calculate the target
	mtx: list = lmtx.setdefault(land, [])
	mtx.append(pc)


def smart_resolve_jmp(cl: list, b: int, pc: int, lmtx: dict):
	sizecode: int = len(cl)
	land: int = b + pc + 1
	muted: dict = {}
	looped: bool = True

	while looped and 0 < land < sizecode:  # keep following JMPs until we hit a collision
		target: Instruction = cl[land]

		if target.data.name == "JMP":
			land = land + target.val_b() + 1

			if land in muted:
				looped = False
			else:
				muted[land] = True
		else:
			looped = False

	mtx: list = lmtx.setdefault(land, [])
	mtx.append(pc)


class DiFlags:
	has_comments = False
	has_lineinfo = False
	inl_consts = False
	jmp_optimize = False


class CodeDesc:
	def __init__(self, val: OpMode, args: list):
		self.val: OpMode = val
		self.args: list = args
		self.label: str = None


class CodeBuffer:
	def __init__(self):
		self.indent: int = 0
		self.buffer: list = []

	def f_indent(self):
		self.indent += 1

	def b_indent(self):
		self.indent -= 1

	def new_line(self):
		self.buffer.append('')

	def write_line(self, line: str):
		self.buffer.append((" " * 4 * self.indent) + line)

	def write_not_zero(self, t: str, n: int):
		if n != 0:
			self.write_line(f"{t} 0x{n:X}")

	def write_header(self, dis: LFuncRead):
		self.write_line('.header')
		self.f_indent()
		self.write_not_zero("version", dis.version)
		self.write_not_zero("format", dis.format)
		self.write_not_zero("endian", dis.rw.endian)
		self.write_not_zero("int", dis.rw.sz_int)
		self.write_not_zero("size_t", dis.rw.sz_size_t)
		self.write_not_zero("Instruction", dis.rw.sz_Instruction)
		self.write_not_zero("lua_Number", dis.rw.sz_lua_Number)
		self.write_not_zero("lua_Integer", dis.rw.sz_lua_Integer)
		self.write_not_zero("integral", dis.rw.integral)
		self.new_line()
		self.b_indent()

	def start_swrite(self, nm: str, segment: list):
		canw = len(segment) != 0

		if canw:
			self.write_line('.' + nm)
			self.f_indent()

		return canw

	def end_swrite(self):
		self.b_indent()

	def to_string(self) -> str:
		return '\n'.join(self.buffer)


class ProtoPrint:
	def __init__(self):
		self.c: CodeBuffer = CodeBuffer()
		self.naming: dict = {}
		self.flags: DiFlags = DiFlags()

	def reset(self):
		self.__init__()

	def get_name_d(self, abbr: str, name: str) -> str:
		fl: str = abbr + sutil.get_norm(name)
		att: int = self.naming.get(fl, -1)

		if att != -1:
			samp = f"{fl}_{att}"
		else:
			samp = fl

		self.naming[fl] = att + 1
		return samp

	def extract_k(self, k: int, p: Proto) -> str:
		ik = p.get_k(k)

		if self.flags.inl_consts:
			result = ik.get_fmt()
		else:
			result = ik.uid

		return result

	def extract_rk(self, rk: int, p: Proto) -> str:
		if rk & BITRK:
			result = self.extract_k(rk & ~BITRK, p)
		else:
			result = extract_r(rk, p)

		return result

	def extract_a(self, mode: str, val: int, p: Proto) -> str:
		if mode == "OpArgU":
			result = str(val)
		elif mode == "OpArgR":
			result = extract_r(val, p)
		else:
			raise NotImplementedError(mode)

		return result

	def extract_abc(self, mode: str, val: int, p: Proto) -> str:
		if mode == "OpArgU":
			result = str(val)
		elif mode == "OpArgR":
			result = extract_r(val, p)
		elif mode == "OpArgK":
			result = self.extract_rk(val, p)
		elif mode == "OpArgS":
			result = extract_uv(val, p)
		else:
			raise NotImplementedError(mode)

		return result

	def extract_bx(self, mode: str, val: int, p: Proto) -> str:
		if mode == "OpArgK":
			result = self.extract_k(val, p)
		elif mode == "OpArgP":
			result = p.get_p(val).uid
		else:
			raise NotImplementedError(mode)

		return result

	def get_seg_uids(self, pref: str, segment: list):
		for s in segment:
			s.uid = self.get_name_d(pref, s.get_fmt())

	def extract_codesegment(self, p: Proto) -> list:
		labels_mtx: dict = {}
		pcode: list = p.code
		codelist: list = [None] * p.sizecode
		smartj: bool = self.flags.jmp_optimize

		for pc in range(p.sizecode):
			i: Instruction = pcode[pc]
			mds: OpMode = i.data
			arg_a: str = None
			arg_b: str = None
			arg_c: str = None

			if mds.a != "OpArgN":
				arg_a = self.extract_a(mds.a, i.val_a(), p)

			if mds.b != "OpArgN":
				if mds.b == "OpArgJ":
					if smartj:
						smart_resolve_jmp(pcode, i.val_b(), pc, labels_mtx)
					else:
						easy_resolve_jmp(i.val_b(), pc, labels_mtx)
				elif mds.o == "iABC":
					arg_b = self.extract_abc(mds.b, i.val_b(), p)
				else:
					arg_b = self.extract_bx(mds.b, i.val_b(), p)

			if mds.c != "OpArgN":
				arg_c = self.extract_abc(mds.c, i.val_c(), p)

			args = []

			if arg_a is not None:
				args.append(arg_a)

			if arg_b is not None:
				args.append(arg_b)

			if arg_c is not None:
				args.append(arg_c)

			codelist[pc] = CodeDesc(mds, args)

		for x in sorted(labels_mtx.keys()):
			if 0 < x < p.sizecode:
				name: str = self.get_name_d('j', 'Label')
				cddesc: CodeDesc = codelist[x]
				pclist: list = labels_mtx[x]

				cddesc.label = name
				for j in pclist:
					cddesc = codelist[j]
					cddesc.args.append(name)

		return codelist

	def write_codesegment(self, p: Proto):
		segment = p.code
		if self.c.start_swrite("code", segment):
			pc: int = 0
			longest_line: int = 0
			longest_op: int = 0
			longest_args: int = 0

			is_commented: bool = self.flags.has_comments
			is_lined: bool = self.flags.has_lineinfo \
				and len(p.lineinfo) == len(segment)

			codeinfo = self.extract_codesegment(p)

			for i in codeinfo:  # run over code
				mds: OpMode = i.val
				fmtd: str = mds.name

				longest_op = safe_len(fmtd, longest_op)
				fmtd = get_lnspace(fmtd, longest_op)

				if is_lined:
					ln = '#' + str(p.lineinfo[pc])
					longest_line = safe_len(ln, longest_line)

					fmtd = get_lnspace(ln, longest_line) + fmtd

				argstr = ', '.join(i.args)

				if is_commented and mds.cmt:
					longest_args = safe_len(argstr, longest_args)
					lnsp = get_lnspace(argstr, longest_args)
					cmt = mds.cmt(i.args)

					fmtd = fmtd + lnsp + '; ' + cmt
				else:
					fmtd += argstr

				if i.label:
					self.c.b_indent()
					self.c.write_line(i.label + ':')
					self.c.f_indent()

				self.c.write_line(fmtd)
				pc += 1

			self.c.end_swrite()

	def write_psegment(self, segment: list):
		if self.c.start_swrite("proto", segment):
			for s in segment:
				self.write_proto(s)

			self.c.end_swrite()

	def write_refsegment(self, nm: str, segment: list):
		if self.c.start_swrite(nm, segment):
			namelen = 0
			refs = []

			for s in segment:
				sname = s.get_fmt()
				info = s.get_info()
				uid = s.uid
				namelen = safe_len(uid, namelen)

				if info:
					sname = f"{sname} {info}"

				refs.append({"lid": namelen - len(uid), "sname": sname, "uid": uid})

			for ref in refs:
				fillid = ' ' * ref['lid']
				self.c.write_line(f"{ref['uid']}{fillid}{ref['sname']}")

			self.c.end_swrite()

	def write_metadata(self, p: Proto):
		if p.nups != 0 or p.numparams != 0:
			self.c.write_line(".meta")
			self.c.f_indent()
			self.c.write_line("nups " + str(p.nups))
			self.c.write_line("numparams " + str(p.numparams))
			self.c.b_indent()

	def write_proto(self, p: Proto):
		self.get_seg_uids('v', p.locvars)
		self.get_seg_uids('u', p.upvalues)
		self.get_seg_uids('p', p.p)

		if p.uid:
			self.c.write_line(f".function \"{p.uid}\"")
		else:
			self.c.write_line(".function")

		self.write_metadata(p)
		self.write_refsegment("local", p.locvars)
		self.write_refsegment("upvalue", p.upvalues)

		if not self.flags.inl_consts:
			self.get_seg_uids('k', p.k)
			self.write_refsegment("const", p.k)

		self.write_codesegment(p)
		self.write_psegment(p.p)
		self.c.write_line(".end")
		self.c.new_line()

	def get_assembly(self, dis: LFuncRead):
		self.c.write_header(dis)
		self.write_proto(dis.proto)
		return self.c.to_string()
