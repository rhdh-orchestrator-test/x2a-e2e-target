# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together for compliance automation. The repository appears to be a demonstration or example repository showing how Chef InSpec can be used alongside Ansible for compliance testing. The migration scope is relatively small, focusing on:

1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Ensuring the existing Ansible playbooks follow best practices
3. Migrating Chef Automate/Chef Server deployment scripts to Ansible

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks for a single developer to complete the migration.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

No traditional modules (Puppet modules with manifests/init.pp, Chef cookbooks with recipes/default.rb, or PowerShell modules with .psd1 files) were found in the repository. The repository contains:

- Ansible playbooks in chef-and-ansible directory
- Chef InSpec tests in chef-and-ansible/tests directory
- Bash scripts for Chef server deployment in setup-automate directory

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability.
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec test that verifies SSH root login is disabled.
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test that verifies HTTPS is properly configured.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests.
- `chef-and-ansible/index.html`: Static HTML file.
- `chef-and-ansible/README.md`: Documentation file explaining the purpose of the examples.
- `setup-automate/deploy-automate.sh`: Bash script that deploys Chef Automate and Chef Infra Server.
- `setup-automate/deploy-chef-server.sh`: Bash script that deploys Chef Infra Server without Automate.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be designed for on-premises or any cloud environment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for more comprehensive testing
  - Option 4: Consider integrating with OpenSCAP or DISA STIG tools

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives:
  - AWX (open-source upstream of Ansible Tower)
  - Ansible Automation Platform
  - GitLab CI/CD with Ansible

### Security Considerations

- **SSL/TLS Configuration**: The current implementation enforces TLSv1.2 and disables vulnerable protocols. Migration should maintain or enhance this security posture.
  - Migration approach: Use Ansible's `openssl_*` modules with the same or stronger security parameters.

- **SSH Hardening**: The InSpec test verifies SSH root login is disabled.
  - Migration approach: Create an Ansible role for SSH hardening that applies the same security controls and includes tests.

- **Self-signed Certificates**: The current implementation uses self-signed certificates.
  - Migration approach: Maintain the same approach for testing environments, but consider integrating with Let's Encrypt for production environments.

- **Vault/secrets management**:
  - Hardcoded credentials in the deployment scripts (username, password)
  - Migration approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions will require understanding the compliance requirements and implementing equivalent checks.
  - Mitigation strategy: Map each InSpec control to an equivalent Ansible assert or custom module.

- **Chef Server Deployment**: Replacing the Chef Server deployment scripts with Ansible playbooks.
  - Mitigation strategy: Create an Ansible role that performs the same system configuration and application deployment steps.

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk as they are already in Ansible format. Review and refactor to follow Ansible best practices.
2. **InSpec Tests** (ssh_profile.rb, website_https_verify.rb): Convert to Ansible-native testing solutions.
3. **Chef Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Create Ansible roles to replace these bash scripts.

### Assumptions

1. The repository is primarily for demonstration purposes and may not represent a production environment.
2. The InSpec tests are used for compliance verification rather than extensive functional testing.
3. The hardcoded credentials in the deployment scripts are for demonstration purposes only.
4. The target environment is Ubuntu 20.04, but the solution should be adaptable to other Linux distributions.
5. The current implementation uses self-signed certificates for SSL/TLS, which may not be suitable for production environments.
6. The repository does not contain actual Chef cookbooks or recipes, only InSpec tests and Ansible playbooks.
7. The migration goal is to consolidate on Ansible as the single automation tool rather than using a hybrid approach.