# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The repository also includes Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, with most components already in Ansible format. The estimated timeline for complete migration is 1-2 weeks, with low complexity for the Ansible playbooks and moderate complexity for replacing the Chef InSpec tests with Ansible-native solutions.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability in Apache by disabling older SSL protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security compliance
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration security check, CCI compliance mapping, STIG validation

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Sample HTML file used for testing. Migration consideration: Keep as-is or include as a template in Ansible.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Implement Ansible Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks
  - Option 4: Consider OpenSCAP integration for STIG compliance checks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower for centralized management
  - Consider migrating user/organization data to AWX/Tower teams and organizations

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL/TLS configuration is maintained in the migrated Ansible playbooks.
  - Migration approach: Maintain the same SSL hardening but use Ansible's crypto modules

- **SSH Security**: The InSpec tests verify SSH root login is disabled. Ensure this security check is maintained.
  - Migration approach: Create equivalent Ansible assert tasks or use ansible-lint rules

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using Ansible Vault for private keys
  - Document the count and type of credentials detected per module:
    - chef-automate-deployment: 1 password (hardcoded)
    - chef-server-deployment: 1 password (hardcoded)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or other testing frameworks.
  - Mitigation strategy: Use Ansible's assert module for basic tests, and consider ansible-lint or Molecule for more complex compliance testing.

- **Chef Server Functionality**: Replacing Chef Server management functionality with Ansible AWX/Tower.
  - Mitigation strategy: Map Chef Server roles and functionality to AWX/Tower, and create migration scripts for any data that needs to be preserved.

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (low risk, already in Ansible format)
   - Review and optimize existing Ansible playbooks
   - Ensure idempotence and best practices

2. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions or Molecule tests
   - Convert ssh_profile.rb to Ansible security checks

3. **Chef Deployment Scripts** (high complexity)
   - Replace with Ansible playbooks for AWX/Tower deployment
   - Create data migration scripts if needed

### Assumptions

1. The primary purpose of this repository is demonstration and education rather than production use, based on the README content.
2. The Chef InSpec tests are used alongside Ansible for compliance verification, not for actual configuration management.
3. The deployment scripts are examples and may contain simplified security practices (hardcoded passwords).
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. There is no complex data migration required from Chef to Ansible since most configuration is already in Ansible format.
6. The SSL certificates are self-signed for demonstration purposes and not production-grade.
7. There are no external dependencies or integrations beyond what's visible in the repository.
8. The migration is primarily focused on replacing Chef InSpec testing with Ansible-native solutions.