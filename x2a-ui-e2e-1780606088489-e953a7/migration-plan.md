# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. Additionally, there are Chef Automate and Chef Infra Server deployment scripts.

The migration scope is relatively small, focusing on:
1. Preserving the existing Ansible playbooks
2. Converting Chef InSpec tests to Ansible-native testing solutions
3. Replacing Chef Automate/Infra Server deployment scripts with Ansible equivalents

Estimated timeline: 1-2 weeks for a single engineer, with minimal complexity due to the limited scope and clear separation of concerns.

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
    - Description: Chef InSpec test that validates HTTPS server configuration and content
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS content verification, SSL protocol validation

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH server security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file for web server testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but deployment scripts suggest on-premises or generic cloud VM usage

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Implement Molecule for Ansible role testing
  - Option 3: Use pytest-ansible for more complex test scenarios

- **Test Kitchen**: Replace with Molecule for Ansible role testing and validation

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for orchestration and management
  - GitLab CI/CD or Jenkins for pipeline automation
  - Compliance scanning tools like OpenSCAP or Ansible's built-in security roles

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the POODLE fix playbook
  - Approach: Maintain the same configuration parameters in Ansible tasks

- **SSH Hardening**: The SSH security controls tested by InSpec need to be implemented in Ansible
  - Approach: Create an Ansible role that applies the same SSH security configurations

- **Vault/secrets management**:
  - Hardcoded credentials in deployment scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated on the fly, but in production environments, certificate management should use Ansible Vault or external secret management

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach
  - Mitigation: Use Ansible's assert module with appropriate conditionals to achieve similar validation

- **Compliance Reporting**: InSpec provides rich compliance reporting that needs to be replicated
  - Mitigation: Implement custom reporting using Ansible's json_query filter and jinja2 templates, or integrate with tools like OpenSCAP

- **Chef Server Functionality**: Replacing Chef Server's node management capabilities
  - Mitigation: Implement Ansible inventory management with dynamic inventories and AWX/Tower

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk as they can remain largely unchanged
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Convert to Ansible assertions or Molecule tests
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh) - Replace with Ansible playbooks for AWX/Tower deployment

### Assumptions

1. The primary goal is to move away from Chef InSpec while maintaining the same level of compliance validation
2. The existing Ansible playbooks are functioning correctly and don't require significant changes
3. There's no requirement to maintain backward compatibility with Chef tools
4. The target environment will continue to be Ubuntu 20.04 or similar Debian-based systems
5. The deployment is for testing/demonstration purposes, as indicated by the use of self-signed certificates and simple configurations
6. The hardcoded credentials in deployment scripts are for demonstration only and would be replaced with secure alternatives in production