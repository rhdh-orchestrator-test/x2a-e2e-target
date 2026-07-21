# MIGRATION FROM ANSIBLE AND CHEF INSPEC TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also includes bash scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on converting the existing Ansible playbooks to a more structured Ansible format and replacing Chef InSpec tests with Ansible-native testing solutions.

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The existing Ansible playbooks are straightforward, but the InSpec tests will require conversion to Ansible-native testing frameworks.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

Note: After thorough examination using file_search for "**/manifests/init.pp", "**/recipes/default.rb", and "**/*.psd1", no traditional Puppet modules, Chef cookbooks, or PowerShell modules were found in this repository. The repository primarily contains Ansible playbooks and Chef InSpec tests.

The following components were identified:

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Simple HTML file used as a template for the website. Can be directly used in Ansible templates.
- `website_https_verify.rb`: Chef InSpec test that verifies HTTPS configuration on the web server.
- `ssh_profile.rb`: Chef InSpec profile that checks SSH configuration for security compliance.
- `deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server.
- `deploy-chef-server.sh`: Bash script for deploying Chef Infra Server without Automate.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - For infrastructure testing: Use Ansible Molecule with Testinfra or Goss
  - For compliance testing: Consider using OpenSCAP with Ansible or Ansible's assert module for simple checks

- **Test Kitchen**: Replace with Ansible Molecule for testing Ansible roles and playbooks

- **Chef Automate/Infra Server**: If these are used for actual infrastructure management, consider migrating to:
  - Ansible Tower/AWX for orchestration and management
  - Ansible Content Collections for organizing and distributing Ansible content

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL/TLS configuration is maintained during migration.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented in the existing playbooks.

- **SSH Security**: The InSpec tests check for SSH root login configuration. Ensure these security checks are maintained.
  - Migration approach: Convert InSpec tests to Ansible assert tasks or use Ansible's `lineinfile` module to enforce configuration.

- **Vault/secrets management**: 
  - Hardcoded credentials in setup scripts: The deploy-automate.sh and deploy-chef-server.sh scripts contain hardcoded usernames and passwords.
  - Migration approach: Replace with Ansible Vault for secure credential storage.

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks.
  - Mitigation strategy: Use Ansible's assert module for simple checks, and Molecule with Testinfra for more complex testing scenarios.

- **Chef Automate Deployment**: If Chef Automate is still needed for compliance reporting, determine how to integrate it with Ansible.
  - Mitigation strategy: Consider using Ansible to deploy and configure Chef Automate if it's still required, or migrate to Ansible Tower/AWX with compliance scanning capabilities.

### Migration Order

1. **website_https.yml** (Priority 1): Already in Ansible format, just needs reorganization into proper Ansible roles.
2. **poodle_fix.yml** (Priority 1): Simple playbook, easy to convert to a proper Ansible role.
3. **InSpec Tests** (Priority 2): Convert to Ansible-native testing solutions.
4. **Chef Deployment Scripts** (Priority 3): Convert to Ansible playbooks for deploying alternative solutions or maintaining Chef if required.

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, as indicated by the README.
2. The Chef InSpec tests are used for compliance verification of Ansible-managed systems.
3. The Chef Automate and Chef Infra Server deployment scripts may not be needed if moving entirely to Ansible.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs for testing purposes.
5. No external dependencies or complex infrastructure are involved beyond what's visible in the repository.
6. The migration is focused on standardizing on Ansible rather than maintaining a hybrid Chef/Ansible environment.