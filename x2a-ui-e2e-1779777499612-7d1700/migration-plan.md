# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The repository also contains Chef Automate and Chef Infra Server deployment scripts that will need to be replaced with Ansible equivalents.

Estimated timeline: 1-2 weeks for a single developer, with minimal complexity due to the limited scope of Chef components that need migration.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook for deploying a secure Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook for remediating SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 in Apache configuration

- **website-https-verify**:
    - Description: Chef InSpec test profile for validating HTTPS website deployment
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh-security**:
    - Description: Chef InSpec test profile for validating SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests. Will need to be replaced with Ansible Molecule or another Ansible-native testing framework.
- `index.html`: Sample HTML file used in the website deployment. Can be preserved as-is.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible's `assert` module for basic validation
  - Option 2: Molecule for more comprehensive testing
  - Option 3: Ansible Lint for static code analysis

- **Test Kitchen**: Replace with Ansible Molecule for infrastructure testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline automation
  - Ansible Vault for secrets management

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook that disables SSLv3 and enables only TLSv1.2.
- **SSH Security**: The SSH security controls tested by ssh_profile.rb must be implemented in Ansible.
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificate generation should use Ansible's crypto modules
  - Count of credentials detected: 3 (username, password, organization name in deployment scripts)

### Technical Challenges

- **Test Coverage**: Ensuring that Ansible-native testing provides the same level of validation as Chef InSpec, particularly for compliance-related checks.
  - Mitigation: Use a combination of Ansible assert, custom modules, and potentially third-party testing tools to achieve equivalent coverage.

- **Compliance Reporting**: Chef InSpec provides built-in compliance reporting that needs to be replicated.
  - Mitigation: Implement custom reporting using Ansible callback plugins or integrate with compliance tools like OpenSCAP.

### Migration Order

1. **website-https-verify** and **ssh-security** (InSpec tests): Convert to Ansible-native testing first to establish the validation framework.
2. **chef-automate-deployment** and **chef-server-deployment**: Replace with Ansible playbooks for infrastructure setup.
3. **kitchen.yml**: Replace with Molecule configuration after tests are migrated.

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) can be preserved as-is without modification.
2. The primary goal is to replace Chef InSpec testing with Ansible-native solutions while maintaining the same level of validation.
3. The deployment scripts for Chef Automate and Chef Infra Server need to be replaced with equivalent Ansible functionality.
4. The repository is primarily used for demonstration/example purposes rather than production deployment, based on the README description.
5. No external Chef cookbooks or complex Chef resources are in use beyond what's visible in the repository.
6. The security compliance requirements (referenced in ssh_profile.rb) need to be maintained in the Ansible implementation.