# CSE302Compilers

Team - Antonia Baies, Aarrya Saraf, and Jonas Treplin.
Labs and project for CSE302 compilers 


## How to run

The compiler functionality is in `main.py` a basic compile command would be:

```
python main.py examples/benchmark.bx -o examples/benchmark
```

Command syntax is `python main.py file`. An optional `-o path` determines the names of the outputs `path.o` and `path.S`. 
If not specified this is defaults to `out`.  

Additionally we provide different optimisation levels that can be specified with `-O[level]` like in GCC. The default Level is `O0` These levels include:

O0: No optimisation is done we go straight SRC -> AST -> TAC -> ASM. Every variable is spilled by default. This is seen as the most reliable compilation to see if the compiler is correct.   
O1: In this case the compilation procedure goes SRC ->AST -> TAC -> CFG -> TAC -> ASM. In the CFG stage we only perform block coalescing and unconditional jump threading. Also we run liveness analysis, but it is used for nothing in this optimisation step.  
O2:  This optimisation level introduces SSA and SSA minimization the pipeline goes SRC ->AST -> TAC -> CFG -> SSA -> TAC -> ASM. In SSA form we perform rename and null choice elimination but no copy propagation (thus the more complex SSA deserialization is not needed). Also we add conditional jump threading in the CFG step.   
O3: In this optimisation level we add register allocation (SRC ->AST -> TAC -> CFG -> SSA -> TAC -> ETAC -> ASM).  The register allocation is run on the deconstructed TAC.  
O4: This level only adds only two final optimisations: copy propagation in the SSA phase and register coalescing in the allocation step. 

Overall we observe about a 40% gain in runtime when moving from O0 to O4 on our benchmark.bx file.

## Liveness Analysis and SSA construction

The code to compute liveness information on a TAC CFG can be found in `lib/liveness.py`. It is implemented in the `LivenessAnalyzer` class and follows the procedure outlined in the lecture in a straightforward way.

All the code related to SSA construction is found in `lib/ssa.py`. The class `SSACrudeGenerator` implements the procedure outlined in the lecture:

1. For each block insert phony definitions for all live in instructions
2. Append a version to each variable which is increased each time it is written to 
3. Convert the phony definitions into proper phi instructions using the last version of each predecessor block.

Since we use a different datastructure for SSA than TAC we also need to replace the predecessor and successor blocks in the meantime.

## SSA Optimization

All optimization in SSA Form is done in `SSAOptimizer` in `lib/ssa.py`. We have 3 optimizations:

1. Copy Propagation: A copy in SSA form `%1.n = copy %0.m` can be replaced by gloablly renaming `%1.n` as `%0.m`. THis is rather straight forward to do. An requires only one single pass
2. Null choice elimination and rename simplification. These are used im union each time we perform all possible rename simplifications we follow up by eliminating all null choice phis. This goes on until we can't find any renames any more.