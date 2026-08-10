# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that need to be migrated to a unified Ansible approach. The repository primarily consists of:

1. Chef InSpec test profiles for compliance validation
2. Ansible playbooks for configuration management
3. Shell scripts for Chef Automate and Chef Infra Server deployment

The migration complexity is **MEDIUM** with an estimated timeline of 2-3 weeks. The primary focus will be on converting the Chef InSpec tests to Ansible-compatible testing frameworks while preserving the existing Ansible playbooks and adapting the Chef server deployment scripts to Ansible roles.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling older SSL protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **ssh_profile**:
    - Description: Chef InSpec profile that validates SSH configuration security (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH security compliance testing

- **website_https_verify**:
    - Description: Chef InSpec profile that validates HTTPS configuration (port 443 listening, TLS 1.2 enabled, SSL3 disabled)
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: HTTPS/TLS compliance testing

- **chef-automate-deploy**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Shell Script
    - Key Features: Chef Automate installation, user and organization setup

- **chef-server-deploy**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Shell Script
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec
- `chef-and-ansible/index.html`: Sample HTML file used for testing web server configuration

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule with Testinfra for testing
  - Option 2: Use ansible-lint for static analysis and compliance
  - Option 3: Integrate with ansible-test for validation

- **Test Kitchen (latest)**: Replace with:
  - Ansible Molecule for testing infrastructure
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open source upstream of Ansible Tower) for smaller deployments
  - GitLab CI/CD or GitHub Actions for pipeline-based automation

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the TLS 1.2 requirement and SSL3 disablement
  - Migration approach: Convert the Apache SSL configuration to an Ansible role with the same security parameters

- **SSH Hardening**: The migration must maintain SSH security controls
  - Migration approach: Create an Ansible role for SSH hardening that implements the same controls tested by the InSpec profile

- **Vault/secrets management**:
  - Hardcoded credentials in shell scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed through Ansible's crypto modules
  - Document count of credentials: 2 sets of credentials in shell scripts (username/password)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks
  - Mitigation: Use Ansible Molecule with Testinfra which provides similar testing capabilities to InSpec

- **Chef Server Deployment**: Replacing Chef Server deployment with Ansible management
  - Mitigation: Create Ansible roles for configuration management that replace the need for Chef Server, or deploy AWX/Ansible Tower

- **Compliance Validation**: Ensuring the same level of compliance validation in the new Ansible framework
  - Mitigation: Implement compliance-as-code using ansible-lint rules and custom Molecule scenarios

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Action: Review and optimize existing playbooks
   - Timeline: 1-2 days

2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Medium complexity
   - Action: Convert to Ansible Molecule with Testinfra
   - Timeline: 3-5 days

3. **Chef Server Deployment Scripts**: High complexity
   - Action: Create Ansible roles for deployment of Ansible Automation Platform or AWX
   - Timeline: 5-7 days

### Assumptions

1. The repository is primarily used for demonstration/educational purposes rather than production deployment, based on the README content
2. The InSpec profiles are used for validation of configurations rather than continuous compliance monitoring
3. The hardcoded credentials in the shell scripts are for demonstration purposes and would be replaced with secure credential management in production
4. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration
5. The Apache configuration is relatively simple and doesn't include complex custom modules or configurations
6. The self-signed certificates are acceptable for the use case and don't need to be replaced with CA-signed certificates
7. There are no external dependencies or integrations not visible in the repository