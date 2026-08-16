# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests that are used for compliance automation. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance validation. Additionally, there are shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The complexity is low to moderate, as the existing Ansible playbooks can be largely reused, while the InSpec tests need to be converted to Ansible-compatible testing frameworks. The estimated timeline for this migration is 1-2 weeks, with most of the effort focused on converting the InSpec tests to an Ansible-compatible testing framework.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server setup, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Static HTML content for the website. Migration consideration: Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Use Molecule for more comprehensive testing
  - Option 3: Consider integrating with other testing frameworks like Serverspec or TestInfra

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL configuration is maintained during migration.
  - Migration approach: Preserve the SSL protocol restrictions (TLSv1.2 only) in the migrated Ansible playbooks.

- **Self-signed Certificates**: The playbooks generate self-signed certificates.
  - Migration approach: Use Ansible's `openssl_*` modules as already implemented in the existing playbooks.

- **SSH Security**: InSpec tests verify SSH security configurations.
  - Migration approach: Convert InSpec tests to Ansible assertions or Molecule tests that verify the same SSH security controls.

- **Vault/secrets management**:
  - No encrypted secrets were detected in the repository
  - Hardcoded credentials were found in the deployment scripts (username, password)
  - Migration approach: Replace hardcoded credentials with Ansible Vault

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks.
  - Mitigation strategy: Map InSpec resources to equivalent Ansible modules or Molecule verifiers. For example, the `port` and `http` resources in InSpec can be tested using Ansible's `wait_for` and `uri` modules.

- **Chef Automate Deployment**: Converting Chef Automate deployment scripts to Ansible.
  - Mitigation strategy: Create Ansible roles that perform the same steps as the bash scripts, using Ansible modules like `command`, `lineinfile`, and `template`.

### Migration Order

1. **website_https.yml** (low risk, already Ansible): Minimal changes needed, just format and structure improvements
2. **poodle_fix.yml** (low risk, already Ansible): Minimal changes needed, just format and structure improvements
3. **InSpec Tests** (moderate complexity): Convert to Ansible assertions or Molecule tests
4. **Deployment Scripts** (high complexity): Convert to Ansible roles and playbooks

### Assumptions

1. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
2. The migration is focused on converting all components to pure Ansible without any Chef dependencies.
3. There is no requirement to maintain backward compatibility with Chef InSpec.
4. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure credential management in the migrated solution.
5. The Test Kitchen setup is primarily for development and testing, not for production deployment.
6. The self-signed certificates are acceptable for the use case and don't need to be replaced with CA-signed certificates.