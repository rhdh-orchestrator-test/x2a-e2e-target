## MIGRATION FAILED for cache

**Failure Reason:** Failed to create 1 files after 10 attempts. Missing files: ansible/roles/cache/molecule/default/molecule.yml

### Migration Summary

- **Total items:** 13
- **Completed:** 8
- **Pending:** 4
- **Missing:** 1
- **Errors:** 0
- **Write attempts:** 10
- **Validation attempts:** 0

### Partial Validation Report

_Not run_

### Partial Checklist

## Checklist: cache

### Recipes → Tasks
- [x] cookbooks/cache/recipes/default.rb → ansible/roles/cache/tasks/main.yml (complete)

### Structure Files
- [x] N/A → ansible/roles/cache/meta/main.yml (complete) - Created standard meta/main.yml
- [x] N/A → ansible/roles/cache/meta/argument_specs.yml (complete)
- [x] N/A → ansible/roles/cache/handlers/main.yml (complete)
- [x] N/A → ansible/roles/cache/defaults/main.yml (complete)
- [ ] N/A → ansible/roles/cache/molecule/default/molecule.yml (missing)

### Molecule Testing
- [ ] N/A → ansible/roles/cache/molecule/default/converge.yml (pending)
- [ ] N/A → ansible/roles/cache/molecule/default/verify.yml (pending)
- [ ] N/A → ansible/roles/cache/molecule/default/create.yml (pending)
- [ ] N/A → ansible/roles/cache/molecule/default/destroy.yml (pending)

### Credentials → AAP Configuration
- [x] N/A → ansible/roles/cache/aap-configuration/controller_credential_types.yml (complete)
- [x] N/A → ansible/roles/cache/aap-configuration/controller_credentials.yml (complete)
- [x] N/A → ansible/roles/cache/tasks/validate_credentials.yml (complete)


### Telemetry

```
Phase: migrate
Duration: 0.00s

Agent Metrics:
  AAP Collection Discovery: 15.94s
    Tokens: 14089 in, 379 out
    Tools: aap_list_collections: 1, aap_search_collections: 1
    collections_found: 0
  Credential Extractor: 8.13s
    Tokens: 4149 in, 183 out
    credentials_found: 1
  Export Planner: 58.22s
    Tokens: 83324 in, 1775 out
    Tools: add_checklist_task: 10, list_checklist_tasks: 2
  Ansible Role Writer: 1335.57s
    Tokens: 2775533 in, 29870 out
    Tools: ansible_lint: 34, ansible_write: 12, file_search: 6, get_checklist_summary: 4, list_checklist_tasks: 19, list_directory: 54, read_file: 29, update_checklist_task: 4, write_file: 1
    attempts: 10
    complete: False
    missing_files: 1
    files_created: 8
    files_total: 13
```