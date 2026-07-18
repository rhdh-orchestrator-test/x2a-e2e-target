# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on compliance automation and Chef server deployment. The migration scope is relatively small, with a primary focus on:

1. Chef InSpec tests that need to be migrated to Ansible-compatible testing frameworks
2. Chef Automate and Chef Server deployment scripts that need to be converted to Ansible playbooks
3. Existing Ansible playbooks that need to be reviewed and potentially refactored

The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components and the fact that some components are already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook for deploying a secure Apache web server with SSL/TLS
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook for fixing SSL POODLE vulnerability in Apache
    - Path: chef-and-ansible
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

- **inspec-website-tests**:
    - Description: Chef InSpec tests for verifying HTTPS website functionality
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: Port listening tests, HTTPS content verification, SSL protocol verification

- **inspec-ssh-profile**:
    - Description: Chef InSpec profile for SSH security compliance
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `chef-and-ansible/index.html`: Simple HTML file used for testing web server deployment. No migration needed, can be used as-is in Ansible templates.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic testing
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing

- **Chef Automate/Server**: Replace deployment scripts with Ansible roles:
  - Create Ansible roles for Chef server deployment (if still needed)
  - Consider migrating to pure Ansible infrastructure management instead of deploying Chef

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook:
  - Ensure TLSv1.2 is enforced
  - Disable vulnerable SSL protocols
  
- **SSH Security**: Maintain the SSH security controls verified by the InSpec profile:
  - Disable root login via SSH
  - Maintain compliance with security standards (SRG-OS-000112, V-38607, etc.)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault or external secret management

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to Ansible-compatible testing will require careful mapping of InSpec resources to Ansible modules:
  - Challenge: InSpec's declarative testing style differs from Ansible's procedural approach
  - Mitigation: Use Ansible assert module with appropriate conditionals or integrate with Molecule

- **Chef Server Deployment**: If Chef Server is still needed in the environment:
  - Challenge: Converting bash-based deployment to idempotent Ansible tasks
  - Mitigation: Use Ansible's package, command, and file modules with appropriate conditionals

### Migration Order

1. **Existing Ansible Playbooks** (chef-and-ansible): Low risk, review and refactor for best practices
2. **InSpec Tests** (chef-and-ansible/tests): Moderate complexity, convert to Ansible-compatible testing
3. **Chef Deployment Scripts** (setup-automate): High complexity, convert to Ansible roles

### Assumptions

1. The primary purpose of this repository is for demonstration/examples rather than production use (based on README.md content)
2. The Chef InSpec tests are used alongside Ansible for compliance verification, not as part of a larger Chef ecosystem
3. The deployment scripts are examples and may contain simplified configurations not suitable for production
4. The hardcoded credentials in the deployment scripts are for demonstration purposes only
5. The repository does not contain complete Chef cookbooks, only InSpec tests and deployment scripts
6. The target environment is Ubuntu 20.04 running on Vagrant VMs
7. The migration will maintain the same functionality but using Ansible-native approaches
8. The existing Ansible playbooks in chef-and-ansible directory are already in the target format but may need review