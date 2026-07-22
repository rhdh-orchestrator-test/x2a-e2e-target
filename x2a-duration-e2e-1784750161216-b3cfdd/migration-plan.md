# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef deployment scripts and Ansible playbooks. The migration scope is relatively small, focusing on two main components:

1. Chef server and Automate deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks that need to be reviewed and potentially refactored to follow best practices

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a single developer. The repository appears to be a collection of examples rather than a production infrastructure codebase, which simplifies the migration process.

## Module Migration Plan

This repository contains both Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

- **website-https**:
    - Description: Ansible playbook for configuring Apache with HTTPS
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Ansible playbook for fixing SSL vulnerabilities in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **inspec-tests**:
    - Description: InSpec tests for SSH configuration and HTTPS website verification
    - Path: chef-and-ansible/tests
    - Technology: InSpec (Chef)
    - Key Features: SSH security compliance checks, HTTPS website validation

### Infrastructure Files

- `README.md`: Basic repository description indicating this is an example repository for Chef-related content.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu (indicated by apt package manager in Ansible playbooks and Apache version 2.4.41-4ubuntu3.10)
- **Virtual Machine Technology**: Not specified, but scripts are designed for on-prem or cloud VMs
- **Cloud Platform**: Not specified, appears to be cloud-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management platform deployment
- **Chef Server CLI**: Replace with Ansible roles for configuration management platform deployment
- **InSpec**: Replace with Ansible-compatible testing frameworks like Molecule or TestInfra

### Security Considerations

- **SSH Security Configuration**: The InSpec tests check for SSH root login being disabled. This security check should be maintained in the Ansible migration.
- **SSL/TLS Configuration**: Both Ansible playbooks handle SSL/TLS configuration:
  - `poodle_fix.yml` enforces TLSv1.2 and disables older protocols
  - `website_https.yml` sets up SSL certificates and HTTPS configuration
- **Vault/secrets management**:
  - Hardcoded credentials in `deploy-automate.sh` and `deploy-chef-server.sh` (username, password)
  - Self-signed certificates in `website_https.yml`
  - These should be migrated to Ansible Vault or another secrets management solution

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment scripts to Ansible will require creating roles and playbooks that can handle the installation and configuration of Chef Automate or an alternative configuration management platform.
- **InSpec Tests**: Converting InSpec tests to an Ansible-compatible testing framework will require mapping InSpec resources to equivalent constructs in the target framework.
- **SSL Certificate Management**: The current implementation generates self-signed certificates. Consider integrating with Ansible's certificate management modules or external certificate authorities.

### Migration Order

1. **poodle_fix.yml** (low risk, already in Ansible format, just needs review)
2. **website_https.yml** (low risk, already in Ansible format, just needs review)
3. **chef-automate-deployment** (moderate complexity, requires conversion from Bash to Ansible)
4. **inspec-tests** (moderate complexity, requires conversion to Ansible-compatible testing framework)

### Assumptions

1. The repository is primarily for demonstration purposes rather than production use, as indicated by the README.
2. The hardcoded credentials in the deployment scripts are example values and not actual production credentials.
3. The target environment is Ubuntu-based, as indicated by the package manager and Apache version in the Ansible playbooks.
4. The migration will maintain the same functionality but convert all components to Ansible.
5. The InSpec tests will need to be converted to an Ansible-compatible testing framework.
6. The Chef Automate and Chef Infra Server deployment scripts will be replaced with Ansible playbooks that either deploy the same tools or equivalent alternatives.