# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used for compliance automation and demonstration purposes. The migration scope is relatively small, focusing on:

1. Chef InSpec tests that need to be converted to Ansible-compatible testing frameworks
2. Chef Automate and Chef Infra Server deployment scripts that need to be replaced with Ansible automation
3. Existing Ansible playbooks that need to be reviewed and potentially refactored

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a single engineer to complete the migration, including testing and documentation.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
I have verified all paths exist using the `list_directory` tool. No Puppet modules (manifests/init.pp), Chef cookbooks (recipes/default.rb), or PowerShell modules (.psd1) were found in the repository.

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH root login is disabled
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance testing

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS is properly configured
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening verification, HTTPS response validation, SSL protocol testing

- **deploy-automate**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **deploy-chef-server**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration file for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `chef-and-ansible/index.html`: Likely a sample file used by the website_https playbook.
- `chef-and-ansible/README.md`: Documentation explaining the purpose of the examples.

## Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for simple tests
  - Option 2: Use Molecule with Testinfra for more complex testing
  - Option 3: Maintain InSpec as a standalone testing tool that runs after Ansible

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - Git repositories for playbook storage
  - Ansible Vault for secrets management

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL/TLS protocols are enforced in the migrated Ansible playbooks.
  - Migration approach: Maintain the same SSL configuration but update to use Ansible's `apache2_module` module instead of `replace`.

- **SSH Security**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Create an Ansible playbook that configures SSH properly and add assertions to verify the configuration.

- **Self-signed Certificates**: The playbooks generate self-signed certificates.
  - Migration approach: Use Ansible's `openssl_*` modules (already in use) but consider adding proper certificate management.

- **Vault/secrets management**:
  - Hardcoded credentials in the deployment scripts (username, password)
  - Migration approach: Move credentials to Ansible Vault

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks may require learning new testing approaches.
  - Mitigation: Use Molecule with Testinfra which has similar syntax to InSpec.

- **Chef Automate Replacement**: Finding an equivalent to Chef Automate's compliance reporting.
  - Mitigation: Consider using Ansible AWX/Tower with custom reporting or integrate with compliance tools like OpenSCAP.

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (low risk, already Ansible)
   - Review and refactor according to best practices
   - Add proper idempotency checks
   - Move variables to separate vars files

2. **InSpec Tests** (moderate complexity)
   - Convert to Ansible assertions or Molecule/Testinfra tests
   - Ensure they validate the same conditions as the original tests

3. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace the Chef Automate and Chef Infra Server deployment scripts
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The repository is primarily for demonstration purposes and not a production environment, based on the README content.
2. The InSpec tests are meant to validate the Ansible playbooks, not to be run independently.
3. The deployment scripts are examples and not used in production environments (they contain hardcoded credentials).
4. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file.
5. The migration will maintain the same functionality but improve security and follow Ansible best practices.
6. No external dependencies or integrations beyond what's visible in the repository need to be considered.