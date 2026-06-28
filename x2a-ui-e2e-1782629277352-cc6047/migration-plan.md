# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components that demonstrate how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, focusing on:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all configuration management.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Ansible playbook that configures Apache web server with HTTPS, self-signed certificates, and a basic website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **https-compliance-tests**:
    - Description: Chef InSpec tests that verify HTTPS configuration and SSL security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL protocol verification

- **ssh-security-compliance**:
    - Description: Chef InSpec profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (STIG)

- **chef-automate-deployment**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework
- `index.html`: Sample HTML file used in the website deployment - can be preserved as a template in Ansible

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace deployment scripts with Ansible playbooks that can:
  - Option 1: Deploy alternative compliance platforms like Ansible Tower/AWX
  - Option 2: Deploy open-source alternatives for compliance reporting

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Approach: Create an Ansible role for Apache SSL hardening that implements the same security controls

- **SSH Security**: The SSH compliance checks must be preserved
  - Approach: Convert the InSpec SSH profile to Ansible assertions or maintain as a standalone InSpec profile

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **Compliance Testing**: The primary challenge is replacing Chef InSpec's testing capabilities
  - Mitigation: Evaluate whether to keep InSpec as a standalone tool or replace with Ansible-native testing
  - Consider using Ansible's assert module combined with uri module to perform similar checks

- **Test Kitchen Integration**: The current setup uses Test Kitchen to orchestrate Ansible and InSpec
  - Mitigation: Replace with Molecule for testing Ansible roles, which provides similar functionality

- **Chef Automate Functionality**: If compliance reporting from Chef Automate is being used
  - Mitigation: Evaluate alternative compliance reporting solutions compatible with Ansible

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they're already in Ansible format
   - Convert to proper Ansible roles with variables, templates, and handlers
   - Implement idempotency improvements where needed

2. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Medium complexity
   - Convert to Ansible playbooks with proper variable handling and Ansible Vault for secrets

3. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Highest complexity
   - Decide on testing strategy (keep InSpec or migrate to Ansible-native testing)
   - Implement the chosen approach while maintaining the same level of compliance verification

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being production infrastructure code
2. The compliance tests are the most valuable components to preserve in the migration
3. There is no dependency on Chef-specific features beyond InSpec testing
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions
5. The deployment scripts for Chef Automate/Infra Server are for demonstration purposes and not critical production components
6. There are no external dependencies or integrations not visible in the repository
7. The security requirements represented in the InSpec profiles must be maintained in the migrated solution