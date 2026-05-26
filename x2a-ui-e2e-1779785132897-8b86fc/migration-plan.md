# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing rather than containing Chef cookbooks that need migration. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the content is already in Ansible format or consists of InSpec tests that can be replaced with Ansible-native solutions. The estimated timeline for migration would be 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains the following technologies that need individual migration planning:

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
    - Key Features: SSL protocol configuration, service restart

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS website functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTP response validation, SSL protocol verification, SSH configuration validation

- **chef_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `README.md`: Documentation files that explain the purpose of the examples. Migration consideration: Update to reflect new Ansible-only approach.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment (based on setup-automate scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with ansible-lint for static analysis
  - Option 3: Use Ansible's built-in `stat`, `command`, and `shell` modules to perform the same checks as InSpec

- **Test Kitchen with Vagrant**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality but is designed specifically for Ansible

- **Chef Automate/Infra Server**: Consider alternatives:
  - Option 1: Ansible AWX/Tower for centralized management
  - Option 2: GitLab CI/CD for pipeline-based automation
  - Option 3: Jenkins with Ansible plugins

### Security Considerations

- **SSL Configuration**: The current implementation fixes POODLE vulnerability by enforcing TLSv1.2. Migration approach: Maintain this security practice using Ansible's `lineinfile` or `template` modules.

- **SSH Security**: The InSpec test checks for disabled root SSH login. Migration approach: Implement this check using Ansible's `assert` module or include it in an Ansible role that configures SSH.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates are generated during deployment, no pre-existing secrets detected
  - No encrypted data bags or Chef Vault usage detected

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or checks may require additional logic. Mitigation: Create custom Ansible modules or use community modules that provide similar functionality.

- **Chef Server Deployment**: If Chef Server is still needed in the environment, the deployment scripts need to be converted to Ansible playbooks. Mitigation: Create an Ansible role for Chef Server deployment or consider migrating completely to Ansible AWX/Tower.

### Migration Order

1. **website_https.yml** (already in Ansible format, low risk)
2. **poodle_fix.yml** (already in Ansible format, low risk)
3. **InSpec tests** (moderate complexity, requires conversion to Ansible testing framework)
4. **Chef deployment scripts** (high complexity, requires decision on whether to maintain Chef Server or migrate completely to Ansible)

### Assumptions

1. The primary goal is to consolidate on Ansible and remove Chef dependencies where possible.
2. InSpec tests need to be replaced with equivalent Ansible-based testing.
3. The Chef Automate and Chef Infra Server deployment scripts may still be needed if the organization continues to use Chef alongside Ansible.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The current security practices (TLS configuration, SSH hardening) need to be maintained in the migrated solution.
6. Test Kitchen will be replaced with an Ansible-native testing framework.
7. No complex Chef cookbooks or recipes are present that would require significant refactoring.