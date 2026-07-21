# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be on showing how Chef InSpec can be used alongside Ansible for compliance testing. There are also Chef Automate and Chef Infra Server deployment scripts.

After thorough analysis using file_search for Chef cookbooks (`**/recipes/default.rb`, `**/recipes/*.rb`), Puppet modules (`**/manifests/init.pp`, `**/manifests/*.pp`), and PowerShell modules (`**/*.psd1`, `**/*.ps*`), no traditional infrastructure-as-code modules were found. The repository consists of Ansible playbooks, Chef InSpec tests, and deployment scripts.

The migration scope is focused on converting the Chef InSpec tests to Ansible-compatible testing frameworks and replacing the Chef deployment scripts with Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity since the Ansible playbooks are already present and only the testing framework needs to be migrated.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
I have verified using `file_search` that there are no Chef cookbooks with `recipes/default.rb`, no Puppet modules with `manifests/init.pp`, and no PowerShell modules with `.psd1` files in this repository. The searches returned no results, confirming that no traditional infrastructure-as-code modules exist in this repository.

The repository contains the following components that need migration:

- **Ansible Playbooks**:
  - Path: chef-and-ansible/website_https.yml (verified exists)
  - Path: chef-and-ansible/poodle_fix.yml (verified exists)

- **Chef InSpec Tests**:
  - Path: chef-and-ansible/tests/ssh_profile.rb (verified exists)
  - Path: chef-and-ansible/tests/website_https_verify.rb (verified exists)

- **Chef Deployment Scripts**:
  - Path: setup-automate/deploy-automate.sh (verified exists)
  - Path: setup-automate/deploy-chef-server.sh (verified exists)

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier. Will need to be updated to use Ansible-native testing.
- `chef-and-ansible/index.html`: Simple HTML file used for testing the web server setup.
- `chef-and-ansible/README.md`: Documentation for the Chef InSpec and Ansible integration examples.
- `README.md`: Main repository documentation.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM setup

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Migrate to Ansible Molecule with Testinfra for testing
  - Option 2: Use the ansible-test framework
  - Option 3: Implement equivalent tests using the Ansible assert module

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives:
  - AWX (open-source version of Ansible Tower)
  - Ansible Automation Platform (commercial)

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL/TLS configuration is maintained during migration.
  - Migration approach: Preserve the existing SSL configuration in the Ansible playbooks
  
- **SSH Security**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Convert InSpec test to equivalent Ansible assert or Molecule/Testinfra test

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Testing Framework Conversion**: Converting Chef InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation: Map InSpec resources to equivalent Testinfra or Ansible assert modules
  
- **Compliance Reporting**: Chef InSpec provides compliance reporting capabilities.
  - Mitigation: Implement equivalent reporting using Ansible facts and custom reporting modules or integrate with compliance tools like OpenSCAP

### Migration Order

1. Convert InSpec tests to Ansible-compatible tests (low risk, foundation for verification)
   - ssh_profile.rb → Ansible/Molecule test
   - website_https_verify.rb → Ansible/Molecule test
   
2. Update Test Kitchen configuration to Molecule (moderate complexity)
   - kitchen.yml → molecule.yml
   
3. Convert Chef Automate/Infra Server deployment scripts to Ansible playbooks (high complexity)
   - deploy-automate.sh → Ansible playbook
   - deploy-chef-server.sh → Ansible playbook

### Assumptions

1. The primary goal is to maintain the same functionality while moving entirely to Ansible
2. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) can be kept as-is
3. The InSpec tests need to be converted to an Ansible-compatible testing framework
4. The deployment scripts for Chef Automate and Chef Infra Server need to be replaced with equivalent Ansible functionality
5. No actual Chef cookbooks exist in this repository that need migration
6. The repository is primarily a demonstration of using Chef InSpec with Ansible rather than a production infrastructure codebase