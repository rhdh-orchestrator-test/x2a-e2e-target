# MIGRATION FROM CHEF INSPEC AND BASH TO ANSIBLE

This repository contains Chef InSpec tests integrated with Ansible playbooks for compliance automation, along with Bash scripts for Chef server deployment. The migration scope is focused on converting Chef InSpec tests to Ansible-compatible testing frameworks and converting Bash deployment scripts to Ansible playbooks. The estimated timeline is 1-2 weeks for a single developer due to the limited scope and complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Bash scripts that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing of a web server with HTTPS
    - Path: chef-and-ansible
    - Technology: Chef InSpec (for testing) and Ansible (for configuration)
    - Key Features: SSL/TLS compliance testing, web server configuration verification, POODLE vulnerability remediation

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef server deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible Molecule for testing.
- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Migration consideration: Keep as is, it's already Ansible.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Migration consideration: Keep as is, it's already Ansible.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Migration consideration: Convert to Ansible Molecule tests or another Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Migration consideration: Convert to Ansible Molecule tests or another Ansible-compatible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate. Migration consideration: Convert to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration consideration: Convert to Ansible playbook or remove if not needed.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not explicitly specified, but the setup scripts mention they work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (testing framework)**: Replace with Ansible-native testing solutions:
  - Ansible Molecule for infrastructure testing
  - Ansible-lint for static code analysis
  - testinfra for Python-based infrastructure testing

- **Test Kitchen with Vagrant**: Replace with:
  - Ansible Molecule for testing infrastructure
  - Keep Vagrant as the driver if needed

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the POODLE fix playbook:
  - Ensure TLSv1.2 is enforced
  - Disable older SSL/TLS protocols
  - Maintain certificate generation and configuration

- **SSH Security**: The SSH security profile tests must be converted to equivalent Ansible tests:
  - Root login restrictions (as specified in ssh_profile.rb)
  - SSH protocol security settings

- **Vault/secrets management**: For each module, identified credential patterns:
  - setup-automate: Hardcoded credentials in deployment scripts (username, password, email) should be moved to Ansible Vault
  - chef-and-ansible: SSL certificates are generated dynamically but should be managed securely

### Technical Challenges

- **Testing Framework Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks:
  - Challenge: InSpec has specific syntax for compliance testing that may not directly map to Ansible testing tools
  - Mitigation: Use Ansible Molecule with testinfra or goss for similar functionality

- **Chef Server Deployment**: Replacing Chef server deployment with alternative solutions:
  - Challenge: Determining if Chef server is still needed or can be replaced entirely with Ansible
  - Mitigation: If Chef is still required for some components, use Ansible to deploy Chef; otherwise, replace Chef functionality with Ansible roles

### Migration Order

1. **Ansible Playbooks** (Low risk, high value): Verify and optimize existing Ansible playbooks (website_https.yml, poodle_fix.yml)
2. **InSpec Tests** (Moderate complexity): Convert InSpec tests to Ansible Molecule or equivalent
3. **Chef Deployment Scripts** (High complexity, dependencies): Convert Chef deployment scripts to Ansible playbooks or replace with alternative solutions

### Assumptions

1. The primary purpose of this repository is to demonstrate compliance automation using Chef InSpec with Ansible, as indicated in the README.
2. The Chef components (Automate, Infra Server) are used for demonstration purposes and may not be required in the final Ansible-only solution.
3. The existing Ansible playbooks (website_https.yml, poodle_fix.yml) are functioning correctly and can be preserved.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. There are no additional Chef cookbooks or recipes beyond what is visible in the repository.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production.
7. The migration will maintain the same level of security compliance testing currently provided by InSpec.