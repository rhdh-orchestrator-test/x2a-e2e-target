# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting the existing InSpec tests to Ansible-compatible testing frameworks while maintaining the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server setup scripts that will need to be converted to Ansible playbooks.

Estimated timeline: 1-2 weeks for a single developer, considering the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS website functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-setup**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-setup**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests in a Vagrant environment
- `index.html`: Simple HTML file used as a template for the website

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, but the setup scripts mention they can be used for on-prem or cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Replace with Ansible Molecule for infrastructure testing
  - Use ansible-lint for static code analysis
  - Consider pytest-ansible for Python-based testing where more complex validation is needed

- **Test Kitchen**: Replace with Ansible Molecule for test orchestration
  - Molecule can handle the provisioning, converge, verify, and destroy workflow

- **Chef Automate/Infra Server**: Replace with Ansible Tower/AWX or other Ansible management platform
  - Consider migrating to Ansible Tower/AWX for web UI, role-based access control, and job scheduling
  - Alternatively, use GitLab CI/CD or Jenkins for Ansible playbook execution

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains the minimum protocol version
  - Consider updating to also include TLSv1.3 support

- **SSH Hardening**: The SSH security controls tested by the InSpec profile must be implemented in Ansible
  - Create an equivalent Ansible role for SSH hardening that disables root login
  - Implement the STIG compliance requirements from the InSpec profile

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks
  - Challenge: InSpec has specific testing syntax and resources that may not have direct equivalents
  - Mitigation: Use Ansible assert modules and custom modules where needed; consider Python-based testing for complex validations

- **Compliance Metadata**: Preserving compliance metadata from InSpec tests
  - Challenge: InSpec tests contain rich compliance metadata (STIG IDs, CCI references) that needs to be preserved
  - Mitigation: Document compliance mappings in Ansible roles using YAML comments or separate documentation files

- **Chef Server Functionality**: Replacing Chef Server user and organization management
  - Challenge: The setup scripts create Chef users and organizations that need equivalent functionality
  - Mitigation: Implement Ansible Tower/AWX teams and organizations, or use a custom solution with a database backend

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - No migration needed, but review for best practices and potential improvements

2. **poodle_fix.yml** (low risk, already Ansible)
   - No migration needed, but review for best practices and potential improvements

3. **website_https_verify.rb** (moderate complexity)
   - Convert to Ansible Molecule tests or pytest-ansible tests

4. **ssh_profile.rb** (moderate complexity)
   - Convert to Ansible role with built-in tests that implement the same security checks

5. **deploy-automate.sh and deploy-chef-server.sh** (high complexity)
   - Convert to Ansible playbooks for infrastructure setup
   - Replace Chef-specific functionality with Ansible Tower/AWX or alternative

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the existing Ansible playbooks
2. The target environment will continue to be Ubuntu 20.04 or compatible
3. Vagrant will continue to be used for development/testing environments
4. The security requirements and compliance standards (STIG, CCI) must be maintained
5. The Chef Automate and Chef Infra Server setup needs to be replaced with an equivalent Ansible-based solution
6. No specific CI/CD integration is mentioned, so we assume a basic Git workflow
7. No specific requirements for secrets management beyond what's in the current scripts
8. The migration will maintain the same level of documentation and testing coverage