import functools
import re
import time

ASCII_ISO = 'iso-8859-1'


class LightTimer:
	def pretty(self) -> str:
		return f"{self.fetch():.3f}s"

	def fetch(self) -> float:
		return time.time() - self.start_time

	def restart(self):
		self.start_time = time.time()

	def __init__(self):
		self.start_time: float = 0.0
		self.restart()


@functools.lru_cache(maxsize=None)
def get_safe(val: str) -> str:
	res = val.encode('unicode-escape').replace(b"\"", b"\\\"")
	return f'"{res.decode(ASCII_ISO)}"'


@functools.lru_cache(maxsize=None)
def get_norm(val: str) -> str:
	name: str = get_safe(val)
	res: list = []

	for s in name.split():
		nstr = ' '.join(re.findall('(?!_)(\w+)', s))
		nstr = nstr.title().replace(' ', '')
		res.append(nstr)

	final: str = ''.join(res)

	if len(final) == 0:
		return "Unknown"
	else:
		return final[:0x10]


def sizeof_fmt(num, suffix='B'):  # https://stackoverflow.com/a/1094933/9419412
	for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
		if abs(num) < 1024.0:
			return f"{num:3.1f}{unit}{suffix}"

		num /= 1024.0

	return f"{num:.1f}Yi{suffix}"
