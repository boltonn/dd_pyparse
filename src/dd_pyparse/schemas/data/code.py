from typing import Literal, Optional

from pydantic import ConfigDict, Field, computed_field

from dd_pyparse.schemas.data.parents.file import File
from dd_pyparse.schemas.enums import DataType, CodingScript


def map_language(mime_type: str) -> CodingScript:
    mapper = {
        "text/x-asm": CodingScript.assembly,
        "text/x-awk": CodingScript.awk,
        "text/x-bat": CodingScript.batch,
        "text/x-batch": CodingScript.batch,
        "text/x-bash": CodingScript.bash,
        "text/x-c": CodingScript.c,
        "text/x-clojure": CodingScript.clojure,
        "text/x-coffeescript": CodingScript.coffeescript,
        "text/x-common-lisp": CodingScript.lisp,
        "text/x-csharp": CodingScript.c_sharp,
        "text/x-csrc": CodingScript.c,
        "text/x-c++": CodingScript.c_plus_plus,
        "text/x-c++src": CodingScript.c_plus_plus,
        "text/x-dart": CodingScript.dart,
        "text/x-erlang": CodingScript.erlang,
        "text/x-fortran": CodingScript.fortran,
        "text/x-go": CodingScript.go,
        "text/x-haskell": CodingScript.haskell,
        "text/x-haxe": CodingScript.haxe,
        "text/x-java": CodingScript.java,
        "text/x-javascript": CodingScript.javascript,
        "text/x-julia": CodingScript.julia,
        "text/x-kotlin": CodingScript.kotlin,
        "text/x-lua": CodingScript.lua,
        "text/x-objectivec": CodingScript.objective_c,
        "text/x-perl": CodingScript.perl,
        "text/x-php": CodingScript.php,
        "text/x-python": CodingScript.python,
        "text/x-ruby": CodingScript.ruby,
        "text/x-rustsrc": CodingScript.rust,
        "text/x-scala": CodingScript.scala,
        "text/x-swift": CodingScript.swift,
        "text/x-typescript": CodingScript.typescript,
        "text/x-vbnet": CodingScript.visual_basic,
        "text/x-yaml": CodingScript.yaml,
        "text/x-ocaml": CodingScript.ocaml,
        "text/x-nim": CodingScript.nim,
        "text/x-matlab": CodingScript.matlab,
        "text/x-lisp": CodingScript.lisp,
        "text/x-msdos-batch": CodingScript.batch,
        "text/x-pascal": CodingScript.pascal,
        "text/x-prolog": CodingScript.prolog,
        "text/x-powershell": CodingScript.powershell,
        "text/x-r": CodingScript.r,
        "text/x-scheme": CodingScript.scheme,
        "text/x-shellscript": CodingScript.shell,
        "text/x-sql": CodingScript.sql,
    }
    return mapper.get(mime_type, None)


class Code(File):
    data_type: Literal["code"] = Field(DataType.code)
    created_by: Optional[str] = Field(None, description="Author of the script")
    modified_by: Optional[str] = Field(None, description="Last user to modify the script")
    
    model_config: ConfigDict(use_enum_values=True)

    @computed_field
    @property
    def language(self) -> CodingScript|None:
        return map_language(self.mime_type)






