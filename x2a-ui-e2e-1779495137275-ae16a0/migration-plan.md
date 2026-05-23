# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. Additionally, there are Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer, including testing and documentation.
**Complexity**: Low to Medium - The repository contains a limited number of files with clear purposes.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS server configuration and accessibility
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **chef-server-deployment**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash with Chef CLI
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Simple HTML file used as a template for website deployment. Can be directly used in Ansible.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with Testinfra for infrastructure testing
  - Option 2: Use Ansible assert modules directly in playbooks for validation
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab CI/CD or Jenkins for pipeline automation
  - Ansible Semaphore as a lightweight alternative

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening that disables SSLv3 and enables only TLSv1.2 in the Apache configuration.
  - Migration approach: Convert the existing Ansible playbook (poodle_fix.yml) to use ansible.builtin.lineinfile or ansible.builtin.template instead of replace module.

- **SSH Security**: The SSH root login security check must be preserved.
  - Migration approach: Convert the InSpec test to an Ansible task that checks the SSH configuration and reports compliance status.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates are generated during deployment, no pre-existing secrets detected

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach.
  - Mitigation: Use Ansible's assert module with appropriate conditionals to achieve similar validation logic.

- **Compliance Reporting**: InSpec provides built-in compliance reporting that needs to be replicated.
  - Mitigation: Implement custom reporting using Ansible's debug, register, and custom callback plugins.

- **Chef Server Deployment**: The Chef server deployment scripts need to be completely rewritten as Ansible playbooks.
  - Mitigation: Create equivalent Ansible roles for configuration management server deployment, possibly using AWX/Tower.

### Migration Order

1. **website_https.yml** (already in Ansible, no migration needed)
2. **poodle_fix.yml** (already in Ansible, no migration needed)
3. **website_https_verify.rb** (convert InSpec test to Ansible assert tasks)
4. **ssh_profile.rb** (convert InSpec control to Ansible security role)
5. **deploy-automate.sh** and **deploy-chef-server.sh** (convert to Ansible playbooks for server deployment)

### Assumptions

1. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are working correctly and don't need modification beyond potential syntax updates.
2. The target environment will continue to be Ubuntu 20.04 or compatible systems.
3. The security compliance requirements (such as SRG-OS-000112) will remain the same after migration.
4. The Chef Automate and Chef Infra Server deployment will be replaced with equivalent Ansible-based solutions rather than continuing to deploy Chef infrastructure.
5. No external Chef cookbooks or dependencies are being used beyond what's visible in the repository.
6. The Test Kitchen setup is only used for development/testing and not for production deployments.