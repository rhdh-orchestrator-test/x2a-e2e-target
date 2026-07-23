# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more structured Ansible format and integrating Chef InSpec testing capabilities into the Ansible workflow. The estimated timeline for migration is 1-2 weeks given the limited number of playbooks and scripts.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **automate-deploy**:
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

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Static HTML content for the website. No migration needed, can be used as-is in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible Molecule with testinfra for infrastructure testing
  - Option 2: Maintain InSpec as a testing tool but invoke it from Ansible
  - Option 3: Convert InSpec tests to equivalent Ansible assert tasks

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL configuration for Apache. Migration should maintain or improve the security posture:
  - Ensure TLS 1.2+ is enforced (currently done in poodle_fix.yml)
  - Consider upgrading to TLS 1.3 if target systems support it
  - Maintain self-signed certificate generation or improve with Let's Encrypt integration

- **SSH Hardening**: The InSpec tests verify SSH security configurations. Migration should:
  - Incorporate SSH hardening into Ansible roles
  - Maintain compliance with security standards referenced in the InSpec tests (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - No other credentials were detected in the repository

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible testing mechanisms will require careful mapping of InSpec resources to Ansible modules or testinfra.
  - Mitigation: Create a mapping document for InSpec resources to Ansible/testinfra equivalents

- **Chef Automate/Server Deployment**: The bash scripts for Chef Automate and Chef Infra Server deployment need to be converted to Ansible roles.
  - Mitigation: Create dedicated Ansible roles for Chef server deployment if still needed, or replace with Ansible AWX/Tower for similar functionality

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
   - Convert to Ansible role structure
   - Add proper variable handling
   - Improve idempotence

2. **poodle_fix.yml** (low risk, already in Ansible format)
   - Convert to Ansible role structure
   - Consider merging with website_https role as a security enhancement option

3. **InSpec Tests** (moderate complexity)
   - Convert to Ansible Molecule tests or maintain as InSpec tests with Ansible integration

4. **Chef Deployment Scripts** (high complexity)
   - Convert to Ansible roles if Chef infrastructure is still needed
   - Or replace with Ansible AWX/Tower deployment if moving away from Chef entirely

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production, as indicated by the README.md mentioning "working examples" and "how-tos".

2. The Chef InSpec tests are intended to validate the configurations applied by the Ansible playbooks, suggesting a hybrid approach where Ansible is used for configuration and InSpec for validation.

3. The setup-automate scripts are used to deploy Chef infrastructure, which may or may not be needed after migration to Ansible.

4. The security standards referenced in the InSpec tests (SRG-OS-000112, V-38607) are still relevant and should be maintained in the Ansible implementation.

5. The target environment is Ubuntu 20.04 as specified in kitchen.yml, but the playbooks may need to support other distributions in the future.

6. The self-signed certificates generated in the website_https.yml playbook are for testing purposes and may need to be replaced with proper certificates in production.