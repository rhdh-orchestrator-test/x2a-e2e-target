# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with only a few components to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS website functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS content verification, SSL protocol verification, SSH root login verification

- **chef_automate_deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

- **chef_server_deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used as a test page. Migration consideration: Keep as-is or update as needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with tools like Ansible Lint for static analysis
  - Option 3: Use Molecule for testing Ansible roles with testinfra for compliance checks
  - Option 4: Keep InSpec as a standalone tool and call it from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL/TLS. Ensure proper TLS versions and cipher suites are used in the migrated Ansible roles.
  - Migration approach: Create an Ansible role for Apache with SSL hardening based on current best practices.

- **SSH Security**: InSpec tests verify SSH root login is disabled. Ensure this security check is maintained.
  - Migration approach: Create an Ansible role for SSH hardening that includes disabling root login.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms.
  - Mitigation: Use Ansible's assert module for basic tests, or consider keeping InSpec as a separate tool called from Ansible.

- **Chef Automate Deployment**: Replacing Chef Automate with equivalent Ansible functionality.
  - Mitigation: Consider using AWX/Ansible Tower as a replacement for Chef Automate's functionality, or keep Chef Automate if it's still needed for specific use cases.

### Migration Order

1. **website_https playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to a proper Ansible role structure

2. **poodle_fix playbook** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Merge into the Apache/web server role

3. **InSpec tests** (moderate complexity)
   - Convert to Ansible assertions or keep as InSpec and integrate with Ansible

4. **Chef deployment scripts** (high complexity)
   - Replace with Ansible playbooks for deploying AWX/Ansible Tower or other CI/CD tools

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance testing.
2. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are already in the target format and may only need optimization.
3. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a Chef environment, which may be replaced with an Ansible-based solution.
4. The repository is primarily used for demonstration/educational purposes rather than production deployments.
5. There are no external dependencies or complex integrations beyond what is visible in the repository.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in a production environment.