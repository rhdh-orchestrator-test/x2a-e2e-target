# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response verification, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that ensures SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration verification, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing web server functionality. Migration consideration: Keep as-is for testing.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but deployment scripts suggest on-premises or generic cloud VM usage

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec as a testing tool but invoke it from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing

### Security Considerations

- **SSL Configuration**: The poodle_fix.yml playbook addresses SSL security by enforcing TLSv1.2. This security practice should be maintained in the migrated solution.
  - Migration approach: Incorporate the SSL hardening into the main Apache configuration playbook.

- **SSH Security**: The ssh_profile.rb InSpec test verifies SSH root login is disabled. This security check should be maintained.
  - Migration approach: Create an Ansible task to verify and enforce SSH root login settings.

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing mechanisms may require additional logic.
  - Mitigation strategy: Consider using Ansible's assert module combined with command/shell modules to perform similar checks, or maintain InSpec as a separate testing tool invoked by Ansible.

- **Chef Automate Deployment**: The Chef Automate deployment scripts need to be converted to Ansible playbooks.
  - Mitigation strategy: Create equivalent Ansible roles for Chef Automate and Chef Infra Server deployment, or consider if these components are still needed in the new architecture.

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **InSpec tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef deployment scripts** (high complexity, requires complete rewrite as Ansible playbooks)

### Assumptions

1. The primary goal is to migrate all functionality to pure Ansible without relying on Chef components.
2. The InSpec tests need to be converted to Ansible-native testing mechanisms rather than keeping InSpec as a separate tool.
3. The deployment scripts for Chef Automate and Chef Infra Server may not be needed if the goal is to move away from Chef entirely.
4. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs.
5. The security requirements (SSL configuration, SSH settings) must be maintained in the migrated solution.
6. No external data sources or complex state management is involved in the current implementation.
7. The migration will maintain the same level of functionality and security as the original implementation.