# MIGRATION FROM CHEF INSPEC AND BASH SCRIPTS TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks used for compliance automation, along with bash scripts for Chef Automate and Chef Infra Server deployment. The migration scope is relatively small, focusing on two main components:

1. Chef InSpec tests used alongside Ansible for compliance verification
2. Bash scripts for Chef infrastructure deployment

The migration complexity is low to moderate, as most of the repository already contains Ansible playbooks. The primary focus will be on replacing Chef InSpec tests with Ansible-native solutions and converting the Chef server deployment scripts to Ansible playbooks.

**Estimated Timeline**: 1-2 weeks for a single developer to complete the migration.

## Module Migration Plan

This repository contains Chef InSpec tests and bash scripts that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance automation
    - Path: chef-and-ansible/
    - Technology: Chef InSpec and Ansible
    - Key Features: HTTPS website deployment, SSL/TLS compliance testing, SSH security compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Automated deployment of Chef infrastructure, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Will need to be replaced with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website. Can be kept as-is or refactored to follow Ansible best practices.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be kept as-is or refactored.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Will need to be converted to an Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Will need to be converted to an Ansible playbook.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For compliance testing: Use Ansible's `assert` module or the community.general.assert_cmd module
  - For system state verification: Use Ansible's built-in modules like `stat`, `command`, `shell` with `register` and `assert`
  - Consider integrating with Ansible Lint for static analysis

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality for testing Ansible roles and playbooks
  - Supports multiple drivers including Vagrant, Docker, and cloud providers

- **Chef Automate/Infra Server**: Replace with Ansible alternatives:
  - Consider using AWX/Ansible Tower for web UI and job scheduling
  - Use Ansible Vault for secrets management
  - Use Git repositories for configuration management

### Security Considerations

- **SSL/TLS Configuration**: The current implementation ensures TLS 1.2 is enabled and SSL3 is disabled. Migration should maintain these security standards.
  - Migration approach: Keep the same security configurations in the Ansible playbooks

- **SSH Security**: The InSpec profile checks for secure SSH configuration (disabled root login).
  - Migration approach: Convert InSpec tests to Ansible assertions or use ansible-lint rules

- **Vault/secrets management**:
  - Hardcoded credentials in bash scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically in the playbook, which is a good practice to maintain

### Technical Challenges

- **Compliance Testing**: Converting InSpec tests to Ansible assertions while maintaining the same level of compliance verification.
  - Mitigation: Create custom Ansible modules or use the assert module with detailed conditions

- **Test Framework**: Replacing Test Kitchen with Molecule requires learning a new testing framework.
  - Mitigation: Start with simple test scenarios and gradually add complexity

- **Chef Server Deployment**: Converting bash scripts to idempotent Ansible playbooks.
  - Mitigation: Break down the scripts into logical tasks and use Ansible's idempotent modules

### Migration Order

1. **InSpec Tests** (Low risk, high value)
   - Convert InSpec tests to Ansible assertions or custom modules
   - Integrate with existing Ansible playbooks

2. **Test Kitchen Configuration** (Moderate complexity)
   - Replace with Molecule for testing Ansible roles and playbooks
   - Set up equivalent test scenarios

3. **Chef Deployment Scripts** (High complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment.

2. The bash scripts for Chef Automate and Chef Infra Server deployment are examples and may contain simplified configurations not suitable for production.

3. The hardcoded credentials in the bash scripts are for demonstration purposes only.

4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the actual deployment could be on any cloud or on-premises infrastructure.

5. The migration to Ansible aims to replace both the Chef InSpec tests and the Chef infrastructure deployment, not just one component.

6. The current implementation does not use complex Chef-specific features that would be difficult to replicate in Ansible.

7. There are no external dependencies or integrations not visible in the repository that would complicate the migration.