# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Replacing Chef Automate/Infra Server deployment scripts with Ansible playbooks

**Estimated Timeline**: 1-2 weeks for a complete migration, with minimal complexity due to the small codebase and limited dependencies.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH configuration compliance checks

- **chef_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash
    - Key Features: Chef server installation, user and organization creation, system configuration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing the web server. No migration needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment (based on comments in deployment scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider migrating to OpenSCAP or DISA STIG tools that integrate with Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols. This security hardening should be preserved in the migrated solution.
  - Migration approach: Maintain the same SSL configuration parameters in the Ansible tasks

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled.
  - Migration approach: Create equivalent Ansible tasks to verify and enforce this configuration

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated during deployment; consider using Ansible Vault for storing pre-generated certificates or sensitive parameters

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions may require different approaches for different test types:
  - For port checking: Use Ansible's `wait_for` module
  - For HTTP/HTTPS verification: Use Ansible's `uri` module
  - For SSL protocol verification: May require custom modules or external commands
  - For SSH configuration checks: Use Ansible's `lineinfile` or `template` modules with `assert`

- **Chef Server Deployment**: Replacing the Chef server deployment scripts with Ansible will require:
  - Creating equivalent Ansible roles for system configuration
  - Developing a strategy for managing Chef server artifacts if they're still needed

### Migration Order

1. **website_https playbook** (already in Ansible, no migration needed)
2. **poodle_fix playbook** (already in Ansible, no migration needed)
3. **InSpec tests** (convert to Ansible-native testing)
4. **Chef deployment scripts** (convert to Ansible playbooks)

### Assumptions

1. The primary purpose of this repository is demonstrating Chef InSpec with Ansible rather than production deployment.
2. The Chef Automate and Chef Infra Server deployment scripts are examples and not critical production components.
3. There are no external dependencies or integrations beyond what's visible in the repository.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. No complex state management or data persistence is required beyond what's in the playbooks.
6. The hardcoded credentials in the deployment scripts are examples and not actual production credentials.
7. The self-signed certificates are acceptable for the use case and don't need to be replaced with CA-signed certificates.