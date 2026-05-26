# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing rather than being a pure Chef cookbook repository. The migration scope is relatively small, as most of the actual infrastructure code is already in Ansible format, with Chef being used primarily for compliance testing via InSpec.

Estimated timeline: 1-2 weeks for a complete migration, with the main effort focused on replacing InSpec tests with equivalent Ansible-native testing solutions.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

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
    - Description: Chef InSpec control that verifies SSH root login is disabled for security compliance
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance check

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash scripts
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration file that uses Ansible as the provisioner and InSpec as the verifier
- `index.html`: Simple HTML file used as a test page for the web server

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the setup scripts suggest they could be used in cloud environments

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Molecule with testinfra for infrastructure testing
  - Option 2: Ansible Test modules for compliance testing
  - Option 3: Continue using InSpec but invoke it directly rather than through Chef

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role and playbook testing
  - Or continue using Test Kitchen with the Ansible provisioner

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Ensure TLSv1.2 is enforced and older protocols are disabled
  - Maintain proper certificate generation and configuration

- **SSH Security**: The SSH root login compliance check must be preserved
  - Migrate the InSpec control to equivalent Ansible assertions or testinfra tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible-native testing solutions will require careful mapping of assertions
  - Mitigation: Create a mapping document for InSpec resources to Ansible/testinfra equivalents

- **Compliance Reporting**: If InSpec was being used for compliance reporting, ensure the Ansible solution provides equivalent reporting capabilities
  - Mitigation: Consider integrating with compliance tools like Ansible Tower/AWX or external reporting systems

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): These are already in Ansible format and require minimal changes
2. **Test Infrastructure** (kitchen.yml): Convert to Molecule or update to use Ansible-native testing
3. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible-native testing solutions
4. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible playbooks with proper secret management

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production infrastructure management
2. The InSpec tests are used for compliance validation rather than as part of a larger Chef-based infrastructure
3. The target environment is Ubuntu 20.04 running on Vagrant VMs
4. The deployment scripts are used for setting up test environments rather than production systems
5. There are no additional Chef cookbooks or recipes beyond what is visible in the repository
6. The primary goal is to maintain the same functionality and compliance testing capabilities while moving to a pure Ansible solution
7. No external integrations or dependencies beyond what is explicitly referenced in the code
8. The hardcoded credentials in the deployment scripts are for demonstration purposes only