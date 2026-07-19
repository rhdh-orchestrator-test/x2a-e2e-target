# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec testing that need to be consolidated into a pure Ansible solution

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks, as the repository contains a limited number of scripts and playbooks with straightforward functionality.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

- **ansible-apache-https**:
    - Description: Ansible playbook for deploying an Apache web server with HTTPS
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **inspec-compliance-tests**:
    - Description: Chef InSpec tests for verifying HTTPS website and SSH security
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH root login testing

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML file for website deployment
- `chef-and-ansible/website_https.yml`: Main Ansible playbook for HTTPS website deployment
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for SSL security hardening
- `setup-automate/deploy-automate.sh`: Bash script for Chef Automate deployment
- `setup-automate/deploy-chef-server.sh`: Bash script for Chef Infra Server deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible's `assert` module for basic testing
  - Option 2: Use Molecule for Ansible role testing
  - Option 3: Integrate with other testing frameworks like Serverspec or Testinfra

### Security Considerations

- **SSL Configuration**: The migration must maintain the SSL hardening present in the poodle_fix.yml playbook
  - Approach: Create an Ansible role for Apache SSL hardening that enforces TLSv1.2
  
- **SSH Security**: The InSpec tests check for SSH root login restrictions
  - Approach: Create an Ansible role that configures SSH security according to the same standards

- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
    - Migration approach: Move credentials to Ansible Vault
  - Self-signed SSL certificates in website_https.yml
    - Migration approach: Maintain the same OpenSSL certificate generation or integrate with Ansible's crypto modules

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment process to Ansible
  - Mitigation: Create an Ansible role that performs the same system preparation and installation steps
  - Research required: Determine if there are existing Ansible roles for Chef Automate deployment or if a custom role needs to be developed

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Evaluate Molecule, Testinfra, or other Ansible-compatible testing frameworks
  - Consider maintaining InSpec tests if they provide value and can be integrated into the Ansible workflow

### Migration Order

1. **ansible-apache-https** (low risk, already in Ansible)
   - Consolidate the website_https.yml and poodle_fix.yml playbooks into a proper Ansible role structure
   - Update any deprecated syntax or modules

2. **inspec-compliance-tests** (medium complexity)
   - Convert to Ansible-native testing or integrate with Molecule
   - Ensure all compliance checks are maintained

3. **chef-automate-deployment** (high complexity)
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment, based on the README.md description mentioning "working examples" and "how-tos".

2. The Chef InSpec tests are used for compliance verification of infrastructure deployed with Ansible, suggesting a hybrid approach that will be consolidated to pure Ansible.

3. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with proper secret management in a production environment.

4. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration, though the deployment scripts don't explicitly specify an OS.

5. The migration will maintain the same functionality but improve security practices by eliminating hardcoded credentials.

6. The existing Ansible playbooks (website_https.yml and poodle_fix.yml) are already functional and will require minimal changes beyond restructuring into proper roles.

7. There are no external dependencies or integrations beyond what's explicitly mentioned in the repository files.