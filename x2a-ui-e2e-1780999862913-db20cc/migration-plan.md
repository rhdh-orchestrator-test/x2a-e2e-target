# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, with only a few Ansible playbooks and InSpec test files to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most of the content is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
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
    - Key Features: HTTPS verification, SSL protocol testing, SSH root login security check

- **chef_automate_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing web server functionality. Can be directly used in Ansible content.

### Target Details

Analyzing the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the ansible.builtin.uri module to replace HTTP tests

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with specific security settings:
  - Migration approach: Maintain the same SSL hardening configurations in Ansible roles
  - Consider using the `community.crypto` collection for certificate management

- **SSH Security**: InSpec tests verify SSH root login is disabled:
  - Migration approach: Create equivalent Ansible assertions or use ansible-lint security rules

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password): 2 instances
  - Self-signed certificates generated in playbooks: 1 instance
  - Migration approach: Replace with Ansible Vault for credential storage

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing:
  - Description: InSpec provides specialized testing capabilities that may not have direct equivalents in Ansible
  - Mitigation strategy: Use a combination of Ansible assert module, custom modules, and external testing tools like Molecule

- **Chef Automate Deployment**: Replacing Chef Automate deployment scripts:
  - Description: The deployment scripts install Chef Automate and Chef Infra Server, which won't be needed in an Ansible-only environment
  - Mitigation strategy: Replace with Ansible AWX or Ansible Automation Platform deployment, or implement alternative compliance tooling

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **InSpec tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef Automate deployment scripts** (high complexity, requires replacement with Ansible automation platform)

### Assumptions

1. The primary goal is to consolidate on Ansible and remove Chef dependencies, including InSpec for testing.
2. The current setup uses Test Kitchen to orchestrate Ansible playbook execution and InSpec testing.
3. The target environment will continue to be Ubuntu 20.04 or compatible systems.
4. The security requirements implemented in the InSpec tests need to be maintained in the Ansible-only solution.
5. The Chef Automate and Chef Server deployment scripts will be replaced with equivalent Ansible Automation Platform setup.
6. No external data sources or integrations beyond what's visible in the repository are required.
7. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be properly secured in the migrated solution.