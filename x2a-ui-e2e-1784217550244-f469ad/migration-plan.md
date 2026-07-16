# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for compliance verification
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks to fully migrate all components to pure Ansible. The primary focus will be on replacing Chef InSpec tests with Ansible-native testing solutions while preserving the existing Ansible playbooks.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook that configures Apache with HTTPS, self-signed certificates, and deploys a simple website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle-ssl-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **https-compliance-tests**:
    - Description: Chef InSpec tests that verify HTTPS configuration, port status, and SSL protocol security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing

- **ssh-compliance-profile**:
    - Description: Chef InSpec profile that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH security compliance checks with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework
- `index.html`: Sample HTML file for website deployment - can be preserved as-is or converted to a template

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for integration testing
  - Option 2: ansible-test for unit testing
  - Option 3: Maintain InSpec as a standalone tool but invoke it through Ansible

- **Test Kitchen**: Replace with:
  - Ansible Molecule for test orchestration
  - Alternatively, use ansible-navigator for playbook testing

- **Chef Automate/Server**: Replace deployment scripts with:
  - Ansible roles for configuration management platform deployment
  - Consider migrating to AWX/Ansible Tower as the central management platform

### Security Considerations

- **SSL Configuration**: The migration must preserve the SSL hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains enabled and older protocols disabled
  - Maintain security compliance with current standards

- **SSH Security**: Preserve the SSH security controls from the InSpec profile
  - Implement equivalent checks using Ansible assert modules or Ansible Molecule verifiers

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup scripts (username: jtonello, password: password)
  - Replace with Ansible Vault for secure credential storage
  - Consider implementing lookup plugins for dynamic credential retrieval

### Technical Challenges

- **Compliance Testing**: The primary challenge is replacing Chef InSpec tests with equivalent Ansible testing mechanisms
  - Solution: Use Ansible assert modules combined with uri module for HTTP testing
  - For SSL verification, use openssl_certificate_info module with assert

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate Ansible and InSpec
  - Solution: Migrate to Ansible Molecule which provides similar functionality in an Ansible-native way

- **Chef Server Deployment**: The deployment scripts for Chef infrastructure will need complete replacement
  - Solution: Create Ansible roles for deploying alternative configuration management or use AWX/Tower

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml) - Low risk, already in Ansible format
   - Review and optimize existing playbooks
   - Convert any hardcoded variables to use Ansible Vault

2. **Testing Framework** - Moderate complexity
   - Set up Ansible Molecule testing framework
   - Create equivalent tests for the InSpec functionality

3. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb) - Moderate complexity
   - Convert InSpec tests to Ansible assert statements or Molecule verifiers
   - Ensure all compliance checks are preserved

4. **Chef Deployment Scripts** - High complexity
   - Replace Chef Automate/Server deployment scripts with Ansible roles
   - Consider implementing AWX/Tower deployment if needed

### Assumptions

1. The primary goal is to eliminate Chef dependencies while maintaining the same functionality
2. The existing Ansible playbooks are working correctly and don't require functional changes
3. The target environment will continue to be Ubuntu 20.04 or compatible systems
4. The deployment will continue to use Vagrant for development/testing
5. The hardcoded credentials in the deployment scripts are for demonstration purposes only
6. The InSpec tests represent the compliance requirements that must be preserved
7. No additional functionality beyond what's in the current repository is required