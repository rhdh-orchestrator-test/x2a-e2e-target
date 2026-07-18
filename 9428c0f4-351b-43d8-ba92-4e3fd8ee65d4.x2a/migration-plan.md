# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Chef InSpec tests and Ansible playbooks that demonstrate how to use Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, focusing on converting Chef InSpec tests to Ansible-native testing solutions while preserving the existing Ansible playbooks. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited scope of Chef components.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-inspec-tests**:
    - Description: Chef InSpec tests for validating HTTPS website configuration and SSH security settings
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS validation, SSL/TLS protocol verification, SSH configuration compliance checks

- **ansible-https-website**:
    - Description: Ansible playbook for configuring a secure HTTPS website with Apache
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec. Migration considerations include replacing with Ansible Molecule for testing.
- `chef-and-ansible/index.html`: Simple HTML file used as a template. Can be directly used in Ansible without modification.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for remediating SSL POODLE vulnerability in Apache.
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring a secure HTTPS website with Apache.
- `setup-automate/deploy-automate.sh`: Script to deploy Chef Automate and Chef Infra Server. Will need to be replaced with Ansible AWX/Tower deployment.
- `setup-automate/deploy-chef-server.sh`: Script to deploy Chef Infra Server. Will need to be replaced with Ansible AWX/Tower deployment.

### Target Details

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml configuration)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible's assert module for basic compliance checks
  - Option 2: Integration with Ansible Lint for static analysis
  - Option 3: Molecule with testinfra for infrastructure testing
  - Option 4: Continue using InSpec as a standalone tool called from Ansible

- **Test Kitchen (latest)**: Replace with Ansible Molecule for testing infrastructure

- **Apache2 (2.4.41-4ubuntu3.10)**: Continue using Ansible's apt module for installation

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2. This can be directly preserved in the existing Ansible playbooks.

- **SSH Security Hardening**: The InSpec profile for SSH security (disabling root login) should be converted to Ansible security tasks or integrated with Ansible security roles from Ansible Galaxy.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates are generated on the fly; consider using Ansible Vault for storing pre-generated certificates in production environments
  - Count of credentials detected: 2 (username/password in deployment scripts)

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible testing mechanisms will require careful mapping of InSpec resources to Ansible modules or testinfra methods.
  - Mitigation: Create a mapping document for each InSpec resource used and its Ansible equivalent.

- **Chef Automate Replacement**: The Chef Automate and Chef Server deployment scripts need to be replaced with equivalent Ansible AWX/Tower setup.
  - Mitigation: Evaluate Ansible AWX/Tower requirements and create equivalent deployment playbooks.

### Migration Order

1. **Ansible Playbooks** (low risk, already in Ansible): Preserve existing playbooks with minimal changes to improve idempotence and follow best practices.

2. **InSpec Tests** (moderate complexity): Convert InSpec tests to Ansible-native testing solutions, ensuring all compliance checks are maintained.

3. **Chef Automate/Server Deployment** (high complexity): Replace Chef infrastructure deployment scripts with Ansible AWX/Tower deployment playbooks.

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment.

2. The Chef components are limited to InSpec tests and deployment scripts, with no Chef cookbooks or recipes to migrate.

3. The existing Ansible playbooks can be preserved with minimal modifications.

4. The target environment will continue to be Ubuntu 20.04 or compatible systems.

5. The deployment scripts contain default/example credentials that would be replaced in a production environment.

6. The self-signed certificates are for demonstration purposes and would be replaced with proper certificates in production.

7. Test Kitchen is used for development/testing only and not for production deployments.