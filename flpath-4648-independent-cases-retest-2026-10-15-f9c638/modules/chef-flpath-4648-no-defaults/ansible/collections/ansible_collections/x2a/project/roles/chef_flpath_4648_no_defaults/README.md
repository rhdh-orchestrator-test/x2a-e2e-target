# FLPATH-4648 no-defaults fixture

This minimal role intentionally has no `defaults/main.yml`. It is
used to verify that the exporter creates a valid argument-specification file
with a description but does not invent an `options` block or defaults.

# FLPATH-3351-TC-07-RULE