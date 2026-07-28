# MIGRATION FROM ANSIBLE AND CHEF SCRIPTS TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef server setup scripts that need to be migrated to a standardized Ansible structure. The repository appears to be a collection of examples rather than a full production infrastructure codebase. The migration scope is relatively small, with only a few Ansible playbooks and bash scripts for Chef server setup. The estimated timeline for migration is 1-2 days given the limited scope.

## Module Migration Plan

This repository contains Ansible playbooks and Chef server setup scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling older protocols
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with Vagrant
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for verifying the HTTPS website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server**: Replace with Ansible AWX/Tower or other Ansible-based configuration management solution
- **Test Kitchen with Ansible**: Migrate to Molecule for Ansible role testing
- **InSpec**: Can be retained for compliance testing with Ansible, as the repository already demonstrates this integration

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache, which should be preserved in the migration
  - Migration approach: Create an Ansible role for Apache SSL configuration
- **Self-signed Certificates**: The playbooks generate self-signed certificates
  - Migration approach: Create an Ansible role for certificate management, potentially adding support for Let's Encrypt
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef Server Deployment**: The bash scripts for Chef server deployment need to be converted to Ansible roles
  - Mitigation: Create an Ansible role that performs the same server setup steps
- **InSpec Integration**: Ensuring that InSpec tests continue to work with the new Ansible structure
  - Mitigation: Maintain the InSpec tests and integrate them into the CI/CD pipeline

### Migration Order

1. `website_https.yml` (low risk, already Ansible)
2. `poodle_fix.yml` (low risk, already Ansible)
3. Chef server deployment scripts (moderate complexity, requires conversion from bash to Ansible)

### Assumptions

1. The repository is primarily for demonstration purposes and not a production environment
2. The InSpec tests should be preserved as they demonstrate compliance automation
3. The Chef server deployment scripts are intended to be replaced with Ansible equivalents
4. No external dependencies or integrations beyond what's visible in the repository
5. No complex state management or data persistence requirements
6. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions

## Migration Implementation Plan

### Phase 1: Restructure Ansible Content (0.5 days)

1. Create a standard Ansible project structure:
   ```
   ansible/
     roles/
       apache_https/
         tasks/
         templates/
         handlers/
         defaults/
       ssl_hardening/
         tasks/
         handlers/
     playbooks/
       website_https.yml
       poodle_fix.yml
     inventory/
     group_vars/
     host_vars/
   ```

2. Refactor existing Ansible playbooks into roles:
   - Move Apache installation and configuration to `apache_https` role
   - Move SSL hardening to `ssl_hardening` role
   - Update playbooks to use the new roles

### Phase 2: Convert Chef Server Scripts to Ansible (0.5 days)

1. Create an Ansible role for Chef server deployment:
   ```
   ansible/
     roles/
       chef_server/
         tasks/
         templates/
         defaults/
         vars/
   ```

2. Convert the bash script logic to Ansible tasks
3. Use Ansible Vault for storing sensitive information (passwords, etc.)
4. Create playbooks that use the Chef server role

### Phase 3: Testing and Documentation (1 day)

1. Set up Molecule for testing the new Ansible roles
2. Integrate existing InSpec tests with the new structure
3. Create comprehensive documentation for the new Ansible structure
4. Create a migration guide for users of the original repository

## Conclusion

This migration is relatively straightforward as part of the content is already in Ansible format. The main work involves restructuring the existing Ansible playbooks into a more maintainable format with roles, and converting the Chef server deployment scripts to Ansible roles. The InSpec tests can be preserved to maintain the compliance automation capabilities demonstrated in the original repository.