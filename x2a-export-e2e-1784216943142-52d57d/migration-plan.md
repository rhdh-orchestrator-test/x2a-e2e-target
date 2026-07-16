# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Adapting the Chef Automate/Infra Server deployment scripts to Ansible playbooks

Estimated timeline: 1-2 weeks for a complete migration, with minimal complexity due to the limited scope of Chef components.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH configuration compliance checks

- **chef_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing. No migration needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider migrating to OpenSCAP or DISA STIG tools that integrate with Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure the migration maintains the security hardening:
  - Disabling vulnerable SSL/TLS protocols (as seen in poodle_fix.yml)
  - Proper certificate generation and management
  
- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. Ensure this compliance check is maintained in the Ansible-native solution.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbook - consider using Ansible Vault for storing private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require understanding the compliance requirements and implementing equivalent checks using Ansible's testing capabilities.
  - Mitigation: Use Ansible's assert module for basic tests and consider integrating with specialized security tools for more complex compliance requirements.

- **Chef Deployment Scripts**: Converting the Chef deployment bash scripts to Ansible playbooks will require understanding the Chef Automate and Infra Server installation process.
  - Mitigation: Create Ansible roles for Chef server deployment that replicate the functionality of the bash scripts.

### Migration Order

1. **website_https playbook** (already in Ansible, no migration needed)
2. **poodle_fix playbook** (already in Ansible, no migration needed)
3. **InSpec tests** (convert to Ansible-native testing)
4. **Chef deployment scripts** (convert to Ansible playbooks)

### Assumptions

1. The primary goal is to eliminate Chef dependencies while maintaining the same functionality.
2. The InSpec tests are used for compliance verification and not for broader infrastructure testing.
3. The deployment scripts are used for setting up Chef infrastructure, which may no longer be needed if fully migrating to Ansible.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The self-signed certificates approach is acceptable for the migrated solution (rather than integrating with a certificate authority).
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the migrated solution.