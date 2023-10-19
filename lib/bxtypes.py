from typing import List
from .bxast import *

class Type:
    pass

class VoidType(Type):
    pass

class FunctionType(Type):
    def __init__(self, input_types : List[Type], out_type: Type) -> None:
        super().__init__()
        self.input_type = input_types
        self.out_type = out_type

class PrimiType(Type):
    
    def __init__(self, name:str) -> None:
        super().__init__()
        self.name = name
    
    def __eq__(self, __value: object) -> bool:
        return self.name == __value.name
    
    def __str__(self) -> str:
        return self.name
    
