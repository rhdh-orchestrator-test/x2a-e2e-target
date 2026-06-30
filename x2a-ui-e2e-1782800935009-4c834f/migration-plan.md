# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. The repository also contains scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Replacing Chef Automate/Infra Server deployment scripts with Ansible equivalents
3. Ensuring all compliance requirements are maintained during migration

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL configuration, virtual host setup, self-signed certificate generation

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on a web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security requirements (SRG-OS-000112)

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for testing web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis
  - Option 4: Consider using Ansible's built-in `--check` mode with custom modules

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Or continue using Test Kitchen with the `kitchen-ansible` plugin

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for enterprise automation platform
  - Ansible Automation Platform for compliance reporting

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain self-signed certificate generation process

- **SSH Security**: Maintain SSH hardening checks from ssh_profile.rb
  - Ensure root login remains disabled
  - Consider expanding SSH hardening based on CIS benchmarks

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts (username, password)
  - Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use custom Ansible modules or Jinja2 templates to create similar testing capabilities
  - Consider using community collections that provide similar functionality

- **Compliance Reporting**: Chef InSpec provides built-in compliance reporting that needs to be replicated
  - Mitigation: Implement custom reporting using Ansible callbacks or integrate with AWX/Tower

- **Self-signed Certificate Management**: Ensure the certificate generation process remains secure
  - Mitigation: Use Ansible's crypto modules (already in use) with appropriate security settings

### Migration Order

1. **website_https.yml and poodle_fix.yml** (already in Ansible format, low risk)
   - Review and optimize existing playbooks
   - Add documentation and improve variable usage

2. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions
   - Convert ssh_profile.rb to Ansible assertions
   - Implement reporting mechanism

3. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace deploy-automate.sh and deploy-chef-server.sh
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary goal is to move all testing and deployment to Ansible-native solutions
2. Compliance reporting is a critical requirement that must be maintained
3. The current setup is used for demonstration/educational purposes rather than production
4. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
5. No external dependencies or integrations beyond what's visible in the repository
6. The security requirements (particularly SSL/TLS and SSH hardening) must be maintained
7. User management and organization setup from Chef scripts needs to be replicated in Ansible