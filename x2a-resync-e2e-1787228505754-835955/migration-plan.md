# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts (Bash)
2. Ansible playbooks with Chef InSpec testing integration

The migration complexity is **LOW to MEDIUM** with an estimated timeline of **1-2 weeks** for a complete migration. The main effort will involve converting the Chef server deployment scripts to Ansible roles and ensuring the existing InSpec tests continue to work with the new Ansible implementation.

## Module Migration Plan

This repository contains Ansible playbooks and Bash scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache with HTTPS using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3, enables TLSv1.2 only

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, user creation, organization setup

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Infra Server installation, user creation, organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test to verify HTTPS website configuration
- `tests/ssh_profile.rb`: InSpec test to verify SSH security configuration
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Continue using InSpec with Ansible (current approach)
  - Option 2: Migrate to Ansible Molecule for testing
  - Option 3: Use ansible-test framework

- **Test Kitchen**: Replace with:
  - Option 1: Ansible Molecule for testing
  - Option 2: Continue using Test Kitchen with Ansible provisioner

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: Ansible Automation Platform
  - Option 2: AWX (open-source Ansible Tower)
  - Option 3: GitLab CI/CD with Ansible

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook
  - Approach: Convert the existing Ansible task to an Ansible role with proper documentation
  - Ensure TLSv1.2 is enforced and SSLv3 is disabled

- **SSH Security**: The InSpec tests verify SSH root login is disabled
  - Approach: Create an Ansible role for SSH hardening that implements the same controls
  - Add Ansible assertions or continue using InSpec to verify compliance

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts:
    - Username: jtonello
    - Password: password (plaintext)
    - Email: jtonello@chef.lab
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **Chef InSpec Integration**: The current setup uses Chef InSpec for compliance testing with Ansible
  - Mitigation: Either maintain this hybrid approach or migrate to Ansible-native testing
  - If maintaining InSpec, ensure it's properly installed and configured in the Ansible environment

- **Self-signed Certificates**: The current implementation generates self-signed certificates
  - Mitigation: Create an Ansible role for certificate management that can handle both self-signed and proper CA-signed certificates
  - Consider integrating with Let's Encrypt for production environments

- **System Tuning**: The Chef deployment scripts set specific kernel parameters
  - Mitigation: Create an Ansible role for system tuning that implements the same parameters
  - Use Ansible's sysctl module instead of direct commands

### Migration Order

1. **website_https playbook** (low risk, already in Ansible)
   - Convert to a proper Ansible role structure
   - Add documentation and parameterization

2. **poodle_fix playbook** (low risk, already in Ansible)
   - Integrate into the website_https role as a security enhancement
   - Add conditional logic for applying the fix

3. **Chef deployment scripts** (moderate complexity)
   - Create Ansible roles for Chef Automate and Chef Infra Server deployment
   - Implement Ansible Vault for credential storage
   - Add idempotency checks

4. **Testing framework** (moderate complexity)
   - Decide on testing strategy (keep InSpec or migrate to Ansible-native testing)
   - Update documentation and CI/CD pipeline

### Assumptions

1. The repository is primarily for demonstration purposes, as indicated by the README.md stating it provides "working examples of Chef related to content created by the Technical Product Marketing and Developer Relations teams."

2. The Chef InSpec tests are intended to work alongside Ansible, as indicated by the chef-and-ansible/README.md mentioning "Using Chef InSpec to Achieve Compliance Automation with Ansible."

3. The deployment scripts contain default/example credentials that would be changed in a production environment.

4. The target environment is Ubuntu 20.04 based on the kitchen.yml configuration.

5. The Apache configuration is basic and doesn't include complex customizations that might be challenging to migrate.

6. The repository doesn't contain actual Chef cookbooks or recipes, only Chef InSpec tests and Chef server deployment scripts.

7. The migration will maintain the compliance testing capabilities currently provided by InSpec.