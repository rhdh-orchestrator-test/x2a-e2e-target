# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The repository appears to be a demonstration or example repository rather than a production infrastructure codebase. The migration scope is relatively small, focusing on:

1. Ansible playbooks for configuring web servers with HTTPS
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks to fully migrate all components to pure Ansible solutions. The main challenge will be replacing Chef InSpec tests with equivalent Ansible-native testing solutions.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

Based on thorough examination of the repository using file_search for patterns "**/manifests/init.pp", "**/recipes/default.rb", and "**/*.psd1", no traditional infrastructure-as-code modules (Puppet modules, Chef cookbooks, or PowerShell modules) were found in this repository.

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test that verifies HTTPS configuration on the web server.
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec test that verifies SSH security configuration (root login disabled).
- `chef-and-ansible/index.html`: Static HTML content for the web server.
- `setup-automate/deploy-automate.sh`: Bash script to deploy Chef Automate and Chef Infra Server.
- `setup-automate/deploy-chef-server.sh`: Bash script to deploy Chef Infra Server without Automate.

### Target Details

Based on the source repository:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that either:
  - Install and configure equivalent Ansible automation platform (AWX/Tower)
  - Or maintain Chef Automate/Server if still required, but managed via Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced
  - Consider adding modern cipher suite configurations
  - Implement proper certificate management

- **SSH Hardening**: The InSpec tests verify SSH security configurations. Migration should:
  - Maintain SSH hardening checks
  - Implement equivalent controls in Ansible

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible assertions or checks will require careful mapping of test logic.
  - Mitigation: Create a test mapping document and validate each converted test

- **Chef Server Deployment**: If Chef Server is still needed in the environment, managing it with Ansible will require careful consideration.
  - Mitigation: Create dedicated Ansible roles for Chef server management or consider migrating to AWX/Tower

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Add proper variable management and templating
   - Implement idempotency improvements if needed

2. **poodle_fix.yml** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Consider merging with website_https.yml as a single role

3. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions or Molecule tests
   - Convert ssh_profile.rb to Ansible assertions or Molecule tests

4. **Chef Server Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace the deployment shell scripts
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The repository is primarily for demonstration purposes and not a production codebase
2. The InSpec tests are used for validation but are not part of a larger compliance framework
3. The Chef Server deployment scripts are examples and not actively used in production
4. The target environment is Ubuntu 20.04 running on Vagrant VMs
5. There is no complex data or state management required
6. There are no external dependencies or integrations not visible in the codebase
7. The migration will be to pure Ansible without maintaining Chef components