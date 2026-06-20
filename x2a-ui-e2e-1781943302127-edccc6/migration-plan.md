# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on compliance automation and server deployment. The migration scope is relatively small, consisting primarily of Chef InSpec tests used alongside Ansible playbooks, and Chef Automate/Chef Infra Server deployment scripts. The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a single developer to complete the migration.

## Module Migration Plan

This repository contains Chef InSpec tests and Chef server deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance automation
    - Path: chef-and-ansible/
    - Technology: Chef InSpec + Ansible
    - Key Features: HTTPS website deployment, SSL/TLS compliance testing, SSH security compliance testing

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts for Chef server deployment
    - Key Features: User creation, organization setup, server configuration

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration considerations include replacing with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying HTTPS website. No migration needed as it's already in Ansible format.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. No migration needed as it's already in Ansible format.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration considerations include replacing with Ansible roles for server deployment.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations include replacing with Ansible roles for server deployment.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use Ansible's built-in assert module for basic compliance checks
  - Option 2: Integrate with OpenSCAP using the ansible-openscap role
  - Option 3: Use Ansible Lint for static code analysis
  - Option 4: Keep InSpec as a standalone tool and call it from Ansible using the command module

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - GitLab/GitHub for version control
  - Ansible Collections for role management

### Security Considerations

- **SSL/TLS Configuration**: The repository includes SSL configuration and testing for POODLE vulnerability. Migration should maintain these security controls.
  - Approach: Preserve the existing Ansible playbooks (website_https.yml and poodle_fix.yml) as they already implement proper SSL/TLS configurations.

- **SSH Security**: The repository includes SSH security compliance testing.
  - Approach: Convert the InSpec SSH profile to Ansible assertions or OpenSCAP checks.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates are generated dynamically in the playbook, which is a good practice to maintain

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible assertions or OpenSCAP checks.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules. For complex tests, consider keeping InSpec and invoking it from Ansible.

- **Chef Server Replacement**: Determining the appropriate Ansible-based replacement for Chef Automate/Infra Server functionality.
  - Mitigation: Evaluate AWX/Tower features against Chef Automate requirements. Document gaps and develop custom solutions as needed.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): No migration needed, already in Ansible format.
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible assertions or OpenSCAP checks.
3. **Chef Server Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible roles for server deployment.

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec integration with Ansible, not to provide production-ready infrastructure code.
2. The Chef Automate and Chef Infra Server deployment scripts are intended for demonstration or development environments, given the hardcoded credentials.
3. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the code should be adaptable to other environments.
4. The migration will maintain the same level of security compliance testing currently provided by InSpec.
5. There are no external dependencies or integrations beyond what is visible in the repository.
6. The migration will not require changes to the underlying application (the simple "Hello World" website).