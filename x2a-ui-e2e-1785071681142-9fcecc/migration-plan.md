# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef Automate/Infra Server setup scripts. The migration scope is relatively small, focusing on converting the existing Ansible playbooks to a more standardized Ansible structure and migrating the Chef server setup scripts to Ansible playbooks. The complexity is low to moderate, with an estimated timeline of 1-2 weeks for a complete migration.

## Module Migration Plan

This repository contains Ansible playbooks and Chef setup scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website functionality and security
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `index.html`: Sample HTML file used in the website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management
- **Test Kitchen with Ansible**: Migrate to Ansible Molecule for testing
- **InSpec**: Consider migrating to Ansible's built-in assert module or maintaining InSpec as a testing tool

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and SSLv3 is disabled
  - Maintain proper certificate generation and management

- **SSH Hardening**: The SSH security profile in tests/ssh_profile.rb indicates SSH hardening requirements
  - Ensure root login is disabled
  - Implement as Ansible tasks with appropriate assertions

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration should use Ansible Vault for securing these credentials

### Technical Challenges

- **InSpec Testing**: The current setup uses InSpec for compliance testing. The migration will need to either:
  - Maintain InSpec as a testing tool alongside Ansible
  - Convert InSpec tests to Ansible assertions or another testing framework

- **Chef Server Migration**: The Chef server setup scripts need to be converted to Ansible roles
  - Challenge: Ensuring all Chef server functionality is properly replicated
  - Mitigation: Create dedicated Ansible roles for Chef server setup or consider migrating to AWX/Tower

### Migration Order

1. **website_https.yml** (Priority 1, low risk): Already an Ansible playbook, needs minimal restructuring
2. **poodle_fix.yml** (Priority 1, low risk): Already an Ansible playbook, needs minimal restructuring
3. **Chef deployment scripts** (Priority 2, moderate complexity): Convert bash scripts to Ansible roles

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments
2. The InSpec tests are essential for compliance verification and should be maintained
3. The Chef server setup is intended for on-premises or cloud VM deployment
4. No external dependencies or integrations beyond what's visible in the repository
5. No specific CI/CD pipeline integration requirements
6. The migration target is a standard Ansible structure with roles and playbooks
7. No specific inventory management requirements beyond what's in the kitchen.yml file