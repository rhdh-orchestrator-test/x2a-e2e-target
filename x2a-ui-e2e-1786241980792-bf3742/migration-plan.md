# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef automation scripts that need to be migrated to a unified Ansible approach. The repository appears to be a demonstration of how Chef InSpec can be used alongside Ansible for compliance automation, along with some Chef server deployment scripts. The migration scope is relatively small, with only a few Ansible playbooks and bash scripts to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef-related scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website functionality and security
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's built-in testing capabilities or integrate with Molecule for testing
- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
- **Chef Automate/Server**: Evaluate if these components are needed or if they can be replaced with Ansible Tower/AWX

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache with self-signed certificates. Migration should maintain or improve this security practice.
- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. This security check should be maintained in the Ansible migration.
- **Vault/secrets management**:
  - Hardcoded credentials in deploy scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated on the fly, but in production should be managed securely

### Technical Challenges

- **InSpec Tests**: The repository uses Chef InSpec for compliance testing. These tests need to be converted to Ansible-compatible testing frameworks like Molecule or maintained as separate InSpec tests.
- **Chef Server Deployment**: The bash scripts for deploying Chef Server need to be converted to Ansible playbooks that can achieve the same functionality.

### Migration Order

1. **website_https.yml** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Add idempotency improvements if needed
   - Update to use Ansible best practices and newer modules if applicable

2. **poodle_fix.yml** (low risk, already Ansible)
   - Review and optimize the existing Ansible playbook
   - Consider merging with website_https.yml as a role or included task

3. **InSpec Tests** (moderate complexity)
   - Convert InSpec tests to Ansible Molecule tests or maintain as separate InSpec tests
   - Ensure all compliance checks are preserved

4. **Chef Server Deployment Scripts** (high complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement proper secret management with Ansible Vault
   - Create roles for Chef server deployment if still needed

### Assumptions

1. The repository is primarily for demonstration purposes showing how Chef InSpec can work with Ansible
2. The actual Chef server deployment may not be needed in the final Ansible implementation
3. The security compliance testing is a key component that needs to be preserved
4. No actual Chef cookbooks or recipes are present in the repository
5. The Ansible playbooks are already well-structured and may need minimal changes
6. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file
7. The deployment is intended for testing/lab environments given the self-signed certificates and simple configurations