# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible's native testing capabilities while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that will need to be replaced with Ansible-based deployment solutions.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope of the repository.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates the HTTPS website deployment
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that validates SSH security configurations
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests. Will need to be replaced with Ansible Molecule or another Ansible-native testing framework.
- `index.html`: Sample HTML content for the web server. Can be preserved as-is.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for comprehensive testing
  - Option 2: Ansible assert module for basic validation
  - Option 3: Ansible Lint for static analysis

- **Test Kitchen**: Replace with Ansible Molecule for infrastructure testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for CI/CD pipeline integration

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening that disables SSLv3 and enables only TLSv1.2
  - Migration approach: Convert the existing Ansible playbook (poodle_fix.yml) to an Ansible role with proper documentation

- **SSH Security**: The SSH security checks must be preserved
  - Migration approach: Convert the InSpec SSH profile to Ansible assertions or Molecule tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using Ansible Vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural testing approach
  - Mitigation: Create a library of reusable Ansible test modules that mimic InSpec's behavior

- **Compliance Metadata**: InSpec tests contain rich compliance metadata (STIG IDs, CCI references) that needs to be preserved
  - Mitigation: Use Ansible role metadata or documentation to maintain compliance information

- **Chef Automate Replacement**: Finding equivalent functionality in Ansible ecosystem
  - Mitigation: Implement AWX/Tower with custom dashboards and reporting

### Migration Order

1. Convert InSpec tests to Ansible tests (low risk, preserves validation capability)
   - website_https_verify.rb → Ansible Molecule scenario
   - ssh_profile.rb → Ansible Molecule scenario

2. Refactor existing Ansible playbooks into roles (moderate complexity)
   - website_https.yml → apache_https role
   - poodle_fix.yml → apache_security role

3. Replace Chef Automate/Server deployment scripts (high complexity)
   - Create Ansible playbooks for AWX/Tower deployment

### Assumptions

1. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are working correctly and don't need functional changes
2. The target environment will continue to be Ubuntu 20.04 or compatible
3. The security requirements (TLS 1.2, SSH hardening) will remain the same
4. The deployment scripts for Chef Automate/Server are used for setting up test environments and not production systems
5. There are no external dependencies or integrations not visible in the repository
6. The InSpec tests are used primarily for validation and not as part of a larger compliance reporting framework