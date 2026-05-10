project('asm-cuda-quad-ml', ['c'],
  version: '0.1.0',
  default_options: ['warning_level=3']
)

# Hardcode the target architecture directly inside the script
target_arch = 'x86_64'

# Locate system assembler and linker
as = find_program('as', required: true)
ld = find_program('ld', required: true)

# Locate optional CUDA utilities
ptxas = find_program('ptxas', required: true)

# Global project includes and flags
inc_dirs = include_directories('src/x86_64/include')

as_flags = [
  '--64', 
  '--noexecstack', 
  '-I' + (meson.project_source_root() / 'src/x86_64/include')
]

ld_flags = [
  '-m', 'elf_x86_64', 
  '-pie', 
  '-z', 'noexecstack',
  '--dynamic-linker', '/lib64/ld-linux-x86-64.so.2'
]

# Descend directly into the source directory
subdir('src')