# =====================================================================
# 1. Scope Variables
# =====================================================================
name = 'quadratic_solver'
main_src = 'quadratic_solver.s'
gpu_arch = 'sm_61'

target_id = meson.current_source_dir().replace(meson.project_source_root() + '/', '').replace('/', '_')
main_base = main_src.split('.')[0]

# =====================================================================
# 2. Compile PTX kernel to .cubin
# =====================================================================
gen_cubin = custom_target(
  target_id + '_cubin',
  input: '../../kernels/quadratic_solver_kernel.ptx',
  output: name + '.cubin',
  command: [ptxas, '-v', '-arch=' + gpu_arch, '@INPUT@', '-o', '@OUTPUT@']
)

# =====================================================================
# 3. Assemble main.s (with listing files if buildtype == debug)
# =====================================================================
if get_option('buildtype') == 'debug'
  gen_main_obj = custom_target(
    target_id + '_main_obj',
    input: main_src,
    output: [main_base + '.o', main_base + '.lst'],
    command: [
      as, as_flags,
      '-I', meson.current_build_dir(),
      '-al=@OUTPUT1@', '@INPUT@',
      '-o', '@OUTPUT0@'
    ],
    depends: [gen_cubin]
  )
else
  gen_main_obj = custom_target(
    target_id + '_main_obj',
    input: main_src,
    output: [main_base + '.o'],
    command: [
      as, as_flags,
      '-I', meson.current_build_dir(),
      '@INPUT@',
      '-o', '@OUTPUT0@'
    ],
    depends: [gen_cubin]
  )
endif

# =====================================================================
# 4. Process internal assembly libraries (if applicable)
# =====================================================================
objs_targets = [gen_main_obj]
has_extra_libs = false

if has_extra_libs
  foreach l : libs
    objs_targets += custom_target(
      target_id + '_' + l + '_obj',
      input: asm_libs[l],
      output: [l + '.o', l + '.lst'],
      command: [as, as_flags, '-al=@OUTPUT1@', '@INPUT@', '-o', '@OUTPUT0@']
    )
  endforeach
endif

# Extract just the first output (.o file) from each target for linking
link_inputs = []
foreach t : objs_targets
  link_inputs += t[0]
endforeach

# =====================================================================
# 5. Link host executable with System V ABI constraints
# =====================================================================
executable_bin = custom_target(
  target_id,
  input: link_inputs,
  output: name,
  command: [
    ld, ld_flags,
    '-o', '@OUTPUT@',
    '@INPUT@',
    '-lcuda', '-lc'
  ],
  build_by_default: true
)

# =====================================================================
# 6. Extra Debug Extraction Rules
# =====================================================================
if get_option('buildtype') == 'debug'
  custom_target(target_id + '_sass',
    input: gen_cubin,
    output: name + '.sass',
    command: ['cuobjdump', '-sass', '@INPUT@'],
    capture: true,
    build_by_default: true
  )

  custom_target(target_id + '_res',
    input: gen_cubin,
    output: name + '.res',
    command: ['cuobjdump', '-res-usage', '@INPUT@'],
    capture: true,
    build_by_default: true
  )
endif

# =====================================================================
# 7. Execution Runner Target
# =====================================================================
run_target('run-' + target_id, command: [executable_bin])