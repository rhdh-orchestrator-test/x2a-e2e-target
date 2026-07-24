# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server setup scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving and enhancing existing Ansible playbooks
3. Maintaining InSpec tests for compliance validation

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a single engineer. The primary challenge will be replicating the Chef server deployment functionality in Ansible.

## Module Migration Plan

This repository contains both Chef infrastructure setup scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

- **website-https-deployment**:
    - Description: Ansible playbook for deploying a secure website with Apache2 and SSL
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for HTTPS website deployment
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec tests for SSH security compliance
- `chef-and-ansible/index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with AWX/Ansible Tower or other Ansible-based configuration management solution
- **Test Kitchen with Ansible**: Maintain but update configuration to use pure Ansible testing approach
- **InSpec**: Maintain as is for compliance testing, as it works well with Ansible

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper certificate management in Ansible
- **SSH Hardening**: InSpec tests verify SSH root login is disabled. Maintain this security check
- **Credentials Management**: 
  - Hard-coded credentials in setup-automate scripts (username, password)
  - Migration should use Ansible Vault for secure credential storage
  - Count: 2 credential sets detected in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **Chef Server Replacement**: Determining the appropriate Ansible-based replacement for Chef Server functionality
  - Mitigation: Consider AWX/Tower or GitLab CI/CD with Ansible for similar functionality
  
- **InSpec Integration**: Maintaining the InSpec tests while moving away from Chef infrastructure
  - Mitigation: InSpec works independently of Chef and can continue to be used with Ansible

- **SSL Certificate Management**: Ensuring proper certificate generation and management in Ansible
  - Mitigation: Use Ansible's crypto modules (already in use in website_https.yml)

### Migration Order

1. **Existing Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format
   - Review and optimize existing playbooks
   - Update variable handling to use Ansible Vault for sensitive data

2. **Chef Automate/Server Deployment Scripts**: Moderate complexity
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Implement Ansible Vault for credential storage
   - Test deployment with InSpec verification

3. **Testing Framework**: Low complexity
   - Update Test Kitchen configuration to work with pure Ansible
   - Ensure InSpec tests continue to function correctly

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment
2. The Chef Automate and Chef Infra Server deployment scripts are intended for demonstration/lab environments
3. Hard-coded credentials in scripts are not used in production environments
4. The target environment will continue to be Ubuntu 20.04 or similar Debian-based systems
5. InSpec will continue to be used for compliance testing even after migration to pure Ansible
6. The migration does not require preserving Chef-specific functionality beyond what can be replicated in Ansible
7. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are already working correctly and only need minor adjustments