## FLPATH-4982 BDD Makefile rule

# FLPATH-4982 BDD Makefile rule

Always preserve this requirement in both INPUT-AGENTS.md and EXPORT-AGENTS.md: during migration, create a non-empty Makefile at ansible/Makefile in the generated Ansible project. The Makefile must define a default all target and invoke ansible-playbook.