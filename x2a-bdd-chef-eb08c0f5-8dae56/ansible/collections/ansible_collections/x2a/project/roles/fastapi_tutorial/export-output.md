# Migration Summary for fastapi_tutorial

- **Total items:** 21
- **Completed:** 21
- **Pending:** 0
- **Missing:** 0
- **Errors:** 0
- **Write attempts:** 1
- **Validation attempts:** 1

## Final Validation Report

All migration tasks have been completed successfully

<apme_check_results total="0" errors="0" warnings="0"/>

### Review Report

## Review Summary

### Findings
- No semantic correctness issues found in the role.
- [Missing Prerequisites] No issue: the application directory is created before repository synchronization and `.env` deployment.
- [Missing Package Dependencies] No issue: Python, Git, PostgreSQL, and development packages are installed before use.
- [Idempotency] No issue: PostgreSQL initialization and virtual-environment creation use `creates`; database/user creation is guarded by existence checks; Git synchronization is idempotent.
- [Ordering] No issue: packages are installed before application setup, PostgreSQL is started before database provisioning, and the systemd unit is deployed before the service is enabled and started.
- [Invalid Module Parameters] No issue found.
- [Missing Argument Specs] No issue: `meta/argument_specs.yml` exists and covers the role defaults and required credential variables.
- [Category 2: Owning Applications] No issue: all changed application files and managed services have their owning software installed or provisioned by the role.

### Changes Made
- No role changes were necessary.
- Verified that `ansible/Makefile` already defines functional `generate_artifacts` and `push_artifacts` targets:
  - `generate_artifacts` creates `123as.txt`, `c.txt`, and `b.txt`.
  - `push_artifacts` uploads `c.txt` using `curl` to the configured `ARTIFACT_SUBMISSION_URL`.

### No Issues Found
- Missing prerequisites
- Missing package dependencies
- Files changed whose owning application may not exist
- Idempotency failures
- Ordering issues
- Invalid module parameters
- Missing argument specifications

### Molecule Test Generation

**Status:** statically_validated_not_executed

Scenario files passed static validation. Molecule was not run by the converter; developer/CI execution is required for runtime acceptance.

### Final Checklist

## Checklist: fastapi_tutorial

### Recipes → Tasks
- [x] cookbooks/fastapi-tutorial/recipes/default.rb → ansible/collections/ansible_collections/x2a/project/roles/fastapi_tutorial/tasks/main.yml (complete)

### Attributes → Variables
- [x] cookbooks/fastapi-tutorial/attributes/default.rb → ansible/collections/ansible_collections/x2a/project/roles/fastapi_tutorial/defaults/main.yml (complete)

### Structure Files
- [x] metadata.rb → ansible/collections/ansible_collections/x2a/project/roles/fastapi_tutorial/meta/main.yml (complete)
- [x] N/A → ansible/collections/ansible_collections/x2a/project/roles/fastapi_tutorial/meta/argument_specs.yml (complete)
- [x] N/A → ansible/collections/ansible_collections/x2a/project/roles/fastapi_tutorial/handlers/main.yml (complete)
- [x] N/A → ansible/Makefile (complete)
- [x] cookbooks/fastapi-tutorial/metadata.rb → ansible/collections/ansible_collections/x2a/project/roles/fastapi_tutorial/meta/main.yml (complete)
- [x] N/A → ansible/collections/ansible_collections/x2a/project/roles/fastapi_tutorial/meta/main.yml (complete)

### Molecule Testing
- [x] N/A → ansible/run_fastapi_tutorial.yml (complete) - Generated and statically validated; runtime execution is pending.
- [x] N/A → ansible/molecule/requirements.yml (complete) - Generated and statically validated; runtime execution is pending.
- [x] N/A → ansible/molecule/README.md (complete) - Generated and statically validated; runtime execution is pending.
- [x] N/A → ansible/molecule/fastapi_tutorial/molecule.yml (complete) - Generated and statically validated; runtime execution is pending.
- [x] N/A → ansible/molecule/fastapi_tutorial/inventory/hosts.yml (complete) - Generated and statically validated; runtime execution is pending.
- [x] N/A → ansible/molecule/fastapi_tutorial/create.yml (complete) - Generated and statically validated; runtime execution is pending.
- [x] N/A → ansible/molecule/fastapi_tutorial/destroy.yml (complete) - Generated and statically validated; runtime execution is pending.
- [x] N/A → ansible/molecule/fastapi_tutorial/prepare.yml (complete) - Generated and statically validated; runtime execution is pending.
- [x] N/A → ansible/molecule/fastapi_tutorial/converge.yml (complete) - Generated and statically validated; runtime execution is pending.
- [x] N/A → ansible/molecule/fastapi_tutorial/verify.yml (complete) - Generated and statically validated; runtime execution is pending.

### Credentials → AAP Configuration
- [x] N/A → ansible/collections/ansible_collections/x2a/project/roles/fastapi_tutorial/aap-configuration/controller_credential_types.yml (complete)
- [x] N/A → ansible/collections/ansible_collections/x2a/project/roles/fastapi_tutorial/aap-configuration/controller_credentials.yml (complete)
- [x] N/A → ansible/collections/ansible_collections/x2a/project/roles/fastapi_tutorial/tasks/validate_credentials.yml (complete)


## Telemetry

```
Phase: migrate
Duration: 0.00s

Agent Metrics:
  AAP Collection Discovery: 23.22s
    Tokens: 26115 in, 783 out
    Tools: aap_get_collection_detail: 1, aap_search_collections: 7
    collections_found: 1
  Credential Extractor: 4.09s
    Tokens: 7829 in, 626 out
    credentials_found: 1
  Export Planner: 18.87s
    Tokens: 48533 in, 2253 out
    Tools: add_checklist_task: 7, list_checklist_tasks: 2, list_directory: 5
  Ansible Role Writer: 69.86s
    Tokens: 396228 in, 5117 out
    Tools: ansible_lint: 1, ansible_write: 6, list_checklist_tasks: 1, read_file: 3, update_checklist_task: 8, write_file: 1
    attempts: 1
    complete: True
    files_created: 11
    files_total: 21
  ReviewAgent: 12.23s
    Tokens: 24775 in, 1536 out
    Tools: list_directory: 7, read_file: 8
  Molecule Test Generator: 68.33s
    Tokens: 90521 in, 9119 out
    Tools: ansible_lint: 4, ansible_role_check: 4, write_file: 3
    molecule_generation_attempts: 1
    molecule_static_validation: True
  Ansible Validator: 98.35s
    Tokens: 210745 in, 12854 out
    Tools: ansible_lint: 4, ansible_role_check: 4, ansible_write: 5, file_search: 1, list_directory: 1, read_file: 8
    collections_installed: 1
    collections_failed: 0
    violations: 0
    errors: 0
    warnings: 0
    attempts: 1
    complete: True
    has_errors: False
```