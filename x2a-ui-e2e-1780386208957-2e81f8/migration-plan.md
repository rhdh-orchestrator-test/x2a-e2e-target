# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for validating configurations
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while consolidating all infrastructure provisioning into Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling older SSL protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website-https-verify**:
    - Description: Chef InSpec profile for validating HTTPS website configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening tests, HTTPS content verification, SSL protocol security checks

- **ssh-security**:
    - Description: Chef InSpec profile for validating SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login security check with STIG compliance metadata

- **chef-automate-deploy**:
    - Description: Shell script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Shell script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Maintain InSpec tests but integrate with Ansible using the ansible_inspec module
  - Option 3: Convert InSpec tests to equivalent Ansible assert tasks

- **Test Kitchen**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for infrastructure testing
  - Option 2: Use simple Vagrant or Docker-based testing with Ansible directly

- **Chef Automate/Infra Server**: Replace with Ansible automation platform:
  - Option 1: Migrate to AWX/Ansible Tower for web UI and job scheduling
  - Option 2: Use Ansible Automation Platform for enterprise features

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should preserve:
  - Self-signed certificate generation
  - TLS 1.2 enforcement (POODLE vulnerability mitigation)
  - Proper file permissions for certificates (mode 0640)

- **SSH Hardening**: The InSpec profile checks for SSH root login restrictions. Migration should:
  - Maintain SSH hardening checks
  - Preserve STIG compliance metadata
  - Consider expanding SSH hardening to include additional controls

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy scripts (username/password)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification methods
  - Mitigation: Use Ansible's assert module or consider maintaining InSpec for testing while using Ansible for provisioning

- **Compliance Metadata**: Preserving STIG and CCI compliance metadata from InSpec tests
  - Mitigation: Document compliance requirements and map to Ansible controls or maintain as separate documentation

- **Test Kitchen Integration**: Replacing Test Kitchen workflow for developers
  - Mitigation: Implement equivalent workflow using Ansible Molecule or document manual testing procedures

### Migration Order

1. **website-https** playbook (low risk, already Ansible)
   - Review and optimize existing Ansible code
   - Add documentation and variable parameterization

2. **poodle-fix** playbook (low risk, already Ansible)
   - Review and optimize existing Ansible code
   - Consider merging with website-https as a role or include

3. **InSpec Tests** (moderate complexity)
   - Decide on testing strategy (keep InSpec or migrate to Ansible testing)
   - Implement chosen testing approach

4. **Chef Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace Chef Automate/Server deployment
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is demonstrating Chef InSpec with Ansible rather than production deployment
2. The target environment is Ubuntu 20.04 running on Vagrant VMs
3. Self-signed certificates are acceptable (no need for Let's Encrypt or commercial certificates)
4. The deployment scripts are examples and not used in production (contain hardcoded credentials)
5. The compliance requirements (STIG, CCI) need to be preserved in the migration
6. Test Kitchen is used for development workflow and needs an equivalent in the Ansible migration