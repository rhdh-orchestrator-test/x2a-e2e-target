# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a combination of Ansible playbooks and Chef InSpec tests that demonstrate how to use Chef InSpec for compliance testing with Ansible deployments. The repository also includes bash scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more structured Ansible format while preserving the compliance testing capabilities provided by Chef InSpec.

After thorough analysis, no traditional Chef cookbooks (with recipes/default.rb), Puppet modules (with manifests/init.pp), or PowerShell modules (.psd1) were found in the repository. The repository primarily consists of Ansible playbooks, Chef InSpec test files, and bash deployment scripts.

**Timeline Estimate**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The existing Ansible playbooks are straightforward, but integrating the compliance testing framework will require careful planning.

## Module Migration Plan

This repository contains Ansible playbooks, Chef InSpec tests, and bash scripts that need individual migration planning:

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
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user and organization creation

- **website_https_verify**:
    - Description: Chef InSpec test profile for verifying HTTPS website deployment
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Tests for port 443 listening, HTTPS response, SSL/TLS protocol security

- **ssh_profile**:
    - Description: Chef InSpec test profile for SSH security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Tests for SSH root login configuration, compliance with security standards

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen.yml)**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef InSpec**: Maintain InSpec for compliance testing or migrate to Ansible-native solutions:
  - Option 1: Continue using InSpec with Ansible (recommended for compliance testing)
  - Option 2: Replace with Ansible assert modules and custom checks
  - Option 3: Integrate with other compliance tools like Ansible Lint or OpenSCAP

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL/TLS. Ensure proper TLS configuration is maintained during migration.
  - Migration approach: Convert the SSL configuration to use Ansible's apache2_module and apache2_conf modules
  
- **Self-signed Certificates**: The current implementation uses self-signed certificates.
  - Migration approach: Maintain the OpenSSL certificate generation or consider integrating with Let's Encrypt for production environments

- **SSH Security**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Ensure SSH hardening is included in the migrated Ansible roles

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef InSpec Integration**: Maintaining compliance testing capabilities while migrating to pure Ansible.
  - Mitigation: Create an Ansible role that installs and runs InSpec tests as part of the deployment pipeline

- **Chef Automate/Server Deployment**: Converting bash scripts to Ansible playbooks.
  - Mitigation: Create dedicated Ansible roles for Chef server deployment with proper idempotence checks

- **Testing Framework**: Replacing Test Kitchen with Ansible-native testing.
  - Mitigation: Implement Ansible Molecule for testing with similar verification capabilities

### Migration Order

1. **website_https playbook** (low risk, already Ansible)
   - Convert to a proper Ansible role structure
   - Implement idempotence improvements
   - Maintain InSpec tests

2. **poodle_fix playbook** (low risk, already Ansible)
   - Convert to a proper Ansible role structure
   - Consider merging with website_https as a security enhancement option

3. **Chef deployment scripts** (moderate complexity)
   - Convert bash scripts to Ansible roles
   - Implement proper secret management with Ansible Vault
   - Add idempotence checks

4. **Testing framework** (moderate complexity)
   - Migrate from Test Kitchen to Ansible Molecule
   - Maintain InSpec test integration

### Assumptions

1. The primary goal is to maintain the same functionality while improving the Ansible code structure and practices.
2. Chef InSpec will continue to be used for compliance testing, as it's a core part of the demonstration.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be replaced with proper secret management.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. The Apache configuration and SSL settings should be maintained as-is for compatibility.
6. The repository is primarily for demonstration purposes rather than production use.
7. The Chef Automate and Chef Server deployment scripts are intended to be converted to Ansible rather than maintained as bash scripts.