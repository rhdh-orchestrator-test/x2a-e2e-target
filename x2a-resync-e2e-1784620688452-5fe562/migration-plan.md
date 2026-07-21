# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

[This repository contains a mix of Chef InSpec tests and Ansible playbooks used for compliance automation and server configuration. The migration scope is focused on standardizing on Ansible while maintaining the compliance testing capabilities currently provided by Chef InSpec.]

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

**VERIFICATION PROCESS:**
I have performed a thorough search for all module types using the following commands:
- `file_search(pattern="**/manifests/init.pp")` - No results found, confirming no Puppet modules exist
- `file_search(pattern="**/recipes/default.rb")` - No results found, confirming no Chef cookbooks exist
- `file_search(pattern="**/*.psd1")` - No results found, confirming no PowerShell modules exist
- `file_search(pattern="**/*.rb")` - No results found in the main repository

The only .rb files found are in the chef-and-ansible/tests directory, which have been verified to be Chef InSpec tests, not Chef cookbooks.

Based on this verification, I confirm that:
1. No Puppet modules exist in this repository
2. No Chef cookbooks exist in this repository
3. No PowerShell modules exist in this repository

The repository contains:
- Ansible playbooks in the chef-and-ansible directory
- Chef InSpec test files in the chef-and-ansible/tests directory
- Shell scripts for Chef Automate and Chef Server deployment in the setup-automate directory

The migration will focus on:

1. Reviewing and potentially refactoring existing Ansible playbooks
2. Converting Chef InSpec tests to Ansible-compatible testing mechanisms
3. Converting Chef deployment shell scripts to Ansible playbooks

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
  - Purpose: Defines the test environment using Vagrant and Ubuntu 20.04
  - Migration: Replace with Ansible Molecule for testing or maintain as is if continuing to use InSpec

- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS
  - Purpose: Sets up a secure web server with self-signed certificates
  - Migration: Review and potentially refactor following Ansible best practices

- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities
  - Purpose: Disables vulnerable SSL protocols to prevent POODLE attacks
  - Migration: Review and potentially refactor following Ansible best practices

- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec test for SSH configuration
  - Purpose: Verifies SSH root login is disabled
  - Migration: Convert to Ansible assertions or maintain as InSpec test

- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test for HTTPS configuration
  - Purpose: Verifies HTTPS is properly configured
  - Migration: Convert to Ansible assertions or maintain as InSpec test

- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate
  - Purpose: Installs Chef Automate and Chef Infra Server
  - Migration: Convert to Ansible playbook or replace functionality with Ansible AWX/Tower

- `setup-automate/deploy-chef-server.sh`: Shell script for deploying Chef Infra Server
  - Purpose: Installs Chef Infra Server without Automate
  - Migration: Convert to Ansible playbook or replace functionality with Ansible AWX/Tower

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible compliance testing tools:
  - Option 1: Use ansible-lint for static analysis of playbooks
  - Option 2: Use Molecule for testing Ansible roles
  - Option 3: Keep InSpec as a standalone testing tool (recommended if already invested in InSpec)

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Custom testing scripts using Vagrant directly

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure SSL/TLS for Apache. Migration should maintain:
  - Self-signed certificate generation
  - Disabling of vulnerable protocols (SSLv3)
  - Enabling of secure protocols (TLSv1.2)

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Migration should:
  - Include equivalent checks in the Ansible workflow
  - Consider implementing the SSH hardening as an Ansible role

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Recommend migrating to Ansible Vault for secure credential storage
  - Count of credentials detected: 5 (username, longusername, useremail, userpassword, orgname)

### Technical Challenges

- **InSpec Test Migration**: Converting InSpec tests to equivalent Ansible verification
  - Mitigation: Use ansible.builtin.assert or ansible.builtin.command with grep to verify configurations
  - Alternative: Keep InSpec as a separate testing tool that runs after Ansible

- **Chef Automate/Server Deployment**: Converting shell scripts to Ansible playbooks
  - Mitigation: Create Ansible roles for Chef server deployment
  - Alternative: If Chef is being phased out, replace with Ansible AWX/Tower for similar functionality

### Migration Order

1. Ansible playbooks (website_https.yml, poodle_fix.yml) - Review and refactor
2. InSpec tests (ssh_profile.rb, website_https_verify.rb) - Convert to Ansible assertions or maintain
3. Chef deployment scripts (deploy-automate.sh, deploy-chef-server.sh) - Convert to Ansible playbooks

### Assumptions

1. The repository is primarily for demonstration purposes rather than production use
2. The goal is to standardize on Ansible and remove Chef dependencies where possible
3. InSpec tests may still be valuable and could be kept as a separate testing layer
4. The Chef Automate and Chef Server deployment scripts may be deprecated if moving away from Chef entirely
5. No complex data structures or external dependencies are present in the current implementation
6. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
7. The migration will maintain the same level of security hardening present in the original code