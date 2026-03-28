# .agent Notes

## Component Example Paths

Example components referenced by workflows or skills may exist in either enabled or disabled form:

- Enabled: `src/component/cmp_*`
- Disabled: `src/component/_cmp_*`

When a skill or workflow references a component example, use the variant that exists in the current repository state.

Examples:

- `src/component/cmp_6000_examplesign` or `src/component/_cmp_6000_examplesign`
- `src/component/cmp_7000_hellocomp` or `src/component/_cmp_7000_hellocomp`
