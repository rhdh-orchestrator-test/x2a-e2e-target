# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks to fully migrate all components to pure Ansible solutions. The primary focus will be on replacing Chef InSpec tests with Ansible-native testing solutions while preserving the existing Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with SSL/TLS setup and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Security fix for POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **https-compliance-tests**:
    - Description: InSpec tests to verify HTTPS configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening verification, HTTPS response validation, SSL/TLS protocol checks

- **ssh-security-compliance**:
    - Description: InSpec profile for SSH security compliance checking
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG-OS-000112)

- **chef-infrastructure-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for infrastructure testing
  - Option 2: Ansible Lint for static code analysis
  - Option 3: Integration with other testing frameworks like Serverspec or Testinfra

- **Test Kitchen**: Replace with Ansible-native testing orchestration:
  - Option 1: Ansible Molecule for test orchestration
  - Option 2: Simple Vagrant or Docker-based testing scripts

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks for:
  - Option 1: Migrate to Ansible Tower/AWX for enterprise automation
  - Option 2: Use GitLab CI/CD or Jenkins with Ansible for CI/CD pipelines

### Security Considerations

- **SSL/TLS Configuration**: Maintain the security hardening from poodle_fix.yml
  - Migration approach: Preserve the existing Ansible task for SSL configuration
  - Consider enhancing with more comprehensive TLS hardening based on current best practices

- **SSH Security**: Maintain compliance checks for SSH configuration
  - Migration approach: Convert InSpec tests to Ansible assert tasks or Molecule tests
  - Ensure continued compliance with security standards (SRG-OS-000112, etc.)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Use Ansible assert modules or Molecule verifiers to replicate InSpec tests
  - Example: Convert port checks to Ansible wait_for module with assert conditions

- **Compliance Reporting**: Replacing Chef InSpec compliance reporting
  - Mitigation: Implement custom reporting using Ansible callback plugins or integrate with tools like Prometheus/Grafana

- **Test Kitchen Workflow**: Replacing the Test Kitchen workflow
  - Mitigation: Implement similar workflow using Ansible Molecule or custom Vagrant/Docker scripts

### Migration Order

1. **Ansible Playbooks** (Low risk, already Ansible)
   - Minimal changes needed to website_https.yml and poodle_fix.yml
   - Focus on improving variable organization and security practices

2. **InSpec Tests** (Moderate complexity)
   - Convert website_https_verify.rb to Ansible/Molecule tests
   - Convert ssh_profile.rb to Ansible/Molecule tests

3. **Chef Deployment Scripts** (High complexity)
   - Create Ansible playbooks to replace deploy-automate.sh and deploy-chef-server.sh
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is for demonstration and educational purposes rather than production use
2. The InSpec tests are used for compliance verification rather than as part of a larger compliance framework
3. There are no external dependencies or integrations not visible in the repository
4. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
5. The deployment scripts are used for setting up test environments rather than production Chef infrastructure
6. No custom Chef cookbooks or resources are being used beyond what's visible in the repository