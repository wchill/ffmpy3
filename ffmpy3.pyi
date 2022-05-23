import subprocess
from asyncio.subprocess import Process
from typing import Optional, List, Dict, Union, IO, Tuple, AnyStr


class FFmpeg:
    executable: str
    cmd: str
    process: Optional[subprocess.Popen]
    def __init__(self, executable: str = ..., global_options: Optional[Union[str, List[str]]] = ..., inputs: Optional[Dict[str, Optional[str]]] = ..., outputs: Optional[Dict[str, Optional[str]]] = ...) -> None: ...
    def run(self, input_data: Optional[bytes] = ..., stdout: Optional[IO[AnyStr]] = ..., stderr: Optional[IO[AnyStr]] = ...) -> Tuple[bytes, bytes]: ...
    async def run_async(self, input_data: Optional[bytes] = ..., stdout: Optional[Union[int, IO[AnyStr]]] = ..., stderr: Optional[Union[int, IO[AnyStr]]] = ...) -> Process: ...
    async def wait(self) -> Optional[int]: ...

class FFprobe(FFmpeg):
    def __init__(self, executable: str = ..., global_options: Optional[Union[str, List[str]]] = ..., inputs: Optional[Dict[str, Optional[str]]] = ...) -> None: ...

class FFExecutableNotFoundError(Exception): ...

class FFRuntimeError(Exception):
    cmd: str
    exit_code: int
    stdout: bytes
    stderr: bytes
    def __init__(self, cmd: str, exit_code: int, stdout: Optional[bytes], stderr: Optional[bytes]) -> None: ...
