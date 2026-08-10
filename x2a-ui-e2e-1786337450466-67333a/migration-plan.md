# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Consolidating existing Ansible playbooks into a proper Ansible project structure
3. Preserving the Chef InSpec tests for compliance validation

Given the limited scope and small number of files, this migration is estimated to be **LOW COMPLEXITY** with an estimated timeline of **1-2 WEEKS**.

## Module Migration Plan

This repository contains a mix of technologies that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

- **apache-https-website**:
    - Description: Ansible playbook for deploying an Apache web server with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **ssl-poodle-fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance
- `chef-and-ansible/index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for deploying Chef Automate if still needed, or migrate completely to Ansible AWX/Tower
- **Test Kitchen with Ansible**: Replace with Ansible Molecule for testing
- **InSpec**: Retain InSpec for compliance testing or migrate to Ansible's built-in assert module and custom modules

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve the security posture:
  - Self-signed certificates are generated in the playbook
  - SSL protocol is hardened to disable SSLv3 (POODLE vulnerability fix)
  - Migration should implement proper certificate management
  
- **SSH Hardening**: InSpec tests verify SSH root login is disabled
  - Migration should maintain this security control
  
- **Credentials Management**: 
  - Hardcoded credentials in deploy scripts (username, password)
  - Migration should use Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible requires understanding of Chef Automate architecture
  - Mitigation: Create dedicated Ansible roles for Chef Automate deployment or consider migrating to Ansible AWX/Tower completely
  
- **InSpec Test Integration**: Maintaining InSpec tests while migrating to pure Ansible
  - Mitigation: Use Ansible's assert module for basic tests and keep InSpec for complex compliance testing

### Migration Order

1. **apache-https-website** (Priority 1): Already an Ansible playbook, just needs restructuring
2. **ssl-poodle-fix** (Priority 1): Already an Ansible playbook, just needs restructuring
3. **chef-automate-deployment** (Priority 2): Convert bash scripts to Ansible roles

### Assumptions

1. The repository appears to be a demonstration/example repository rather than production code
2. The Chef Automate deployment is still required after migration (if not, this component can be dropped)
3. InSpec tests should be preserved for compliance validation
4. The target environment will continue to be Ubuntu 20.04 or similar
5. No external dependencies or integrations beyond what's visible in the code
6. No complex state management or database migrations required