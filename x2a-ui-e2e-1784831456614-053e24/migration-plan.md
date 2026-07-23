# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef-related deployment scripts that need to be migrated to a unified Ansible approach. The repository appears to be a demonstration of using Chef InSpec for compliance testing alongside Ansible playbooks, with additional scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and bash scripts to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible playbooks (which can be directly reused) and moderate complexity for the Chef server deployment scripts (which need to be reimplemented as Ansible roles).

## Module Migration Plan

This repository contains Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerability by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test profile for verifying HTTPS website configuration
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test profile for verifying SSH security configuration
- `chef-and-ansible/index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but the deployment scripts appear to be designed for both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec as a testing tool but invoke it from Ansible

- **Test Kitchen with Vagrant**: Replace with:
  - Molecule for Ansible role testing
  - Ansible-specific CI/CD pipelines

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for web UI and job scheduling
  - GitLab/GitHub for version control and CI/CD
  - Ansible Collections for role management

### Security Considerations

- **SSL Configuration**: The playbooks include SSL hardening that must be preserved:
  - Disabling SSLv3 protocol (POODLE vulnerability mitigation)
  - Enabling only TLSv1.2
  - Self-signed certificate generation

- **SSH Hardening**: The InSpec tests verify SSH security configurations:
  - Root login restrictions
  - These tests should be converted to Ansible assertions or maintained as separate compliance checks

- **Vault/secrets management**:
  - Hardcoded credentials in the Chef deployment scripts (username, password)
  - These should be migrated to Ansible Vault or another secrets management solution

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-native testing:
  - Challenge: InSpec provides a domain-specific language for compliance testing that doesn't directly map to Ansible
  - Mitigation: Use a combination of Ansible assert modules and custom modules where needed, or keep InSpec as a separate tool called from Ansible

- **Chef Server Functionality**: Replacing Chef Server functionality:
  - Challenge: Chef Server provides organization management, policy-based configuration, and a centralized API
  - Mitigation: Use AWX/Ansible Tower for similar functionality, with GitLab/GitHub for version control

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml):
   - Low risk, can be directly reused with minimal changes
   - Update to use Ansible best practices (roles, collections)

2. **Testing Framework**:
   - Moderate complexity
   - Convert InSpec tests to Ansible assertions or Molecule tests
   - Update CI/CD pipeline to use Ansible-native testing

3. **Chef Deployment Scripts**:
   - High complexity
   - Create Ansible roles to replace Chef Automate and Chef Server deployment
   - Implement secrets management for credentials

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are essential and need to be preserved in some form
3. The Chef deployment scripts are used for setting up infrastructure rather than application deployment
4. There are no external dependencies or integrations not visible in the repository
5. The target environment will continue to be Ubuntu 20.04 or similar Linux distributions
6. The migration will maintain the same level of security hardening present in the original code
7. No specific performance requirements are needed for the migrated solution