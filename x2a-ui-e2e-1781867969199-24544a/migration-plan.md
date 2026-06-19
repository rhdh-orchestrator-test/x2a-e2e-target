# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus is on compliance automation using Chef InSpec alongside Ansible deployments. The repository also includes Chef Automate and Chef Infra Server setup scripts.

The migration scope is relatively small, as most of the configuration is already in Ansible format. The primary migration effort will involve converting the Chef InSpec tests to Ansible-native testing solutions. The estimated timeline for this migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS website deployment and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol security verification

- **ssh_profile**:
    - Description: Chef InSpec control that validates SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used for testing web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use the ansible-lint tool for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible-native testing framework
  - Molecule provides similar functionality for testing Ansible roles with various drivers

- **Chef Automate/Infra Server**: These deployment scripts can be replaced with:
  - Ansible playbooks for deploying alternative compliance solutions
  - Consider migrating to Ansible Tower/AWX for enterprise automation platform

### Security Considerations

- **SSL/TLS Configuration**: The current implementation focuses on security hardening:
  - Maintain the same security posture by ensuring TLSv1.2 is enforced
  - Ensure self-signed certificate generation is properly implemented in Ansible
  
- **SSH Hardening**: The SSH security controls need to be preserved:
  - Implement equivalent SSH hardening in Ansible using the openssh_config module
  - Maintain compliance with referenced security standards (STIG)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **Compliance Testing**: The primary challenge is replacing Chef InSpec tests with equivalent Ansible testing:
  - InSpec provides specialized resources for testing security controls
  - Ansible's testing capabilities are more limited for compliance validation
  - Solution: Consider using a combination of Ansible assert, custom modules, and external tools like OpenSCAP

- **Test Kitchen to Molecule Migration**: 
  - Test Kitchen configuration needs to be translated to Molecule
  - Solution: Create equivalent Molecule scenarios that match the current Test Kitchen setup

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format, may need minor updates for best practices
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity to convert to Ansible-native testing
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity, requires replacing with alternative compliance platform deployment

### Assumptions

1. The primary goal is to eliminate Chef dependencies while maintaining the same functionality
2. Security compliance testing is a critical requirement that must be preserved
3. The target environment will continue to be Ubuntu 20.04 on Vagrant VMs
4. No additional Chef cookbooks or resources are being used beyond what's visible in the repository
5. The hardcoded credentials in the deployment scripts are for testing purposes only
6. The repository is primarily used for demonstration/educational purposes rather than production deployment
7. The migration should maintain the same level of security validation currently provided by InSpec