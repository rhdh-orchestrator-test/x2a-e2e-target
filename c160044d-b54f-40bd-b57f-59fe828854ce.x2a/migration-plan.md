# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on compliance automation and infrastructure deployment. The primary migration scope involves:

1. Chef InSpec tests that need to be converted to Ansible-compatible testing frameworks
2. Chef Automate and Chef Infra Server deployment scripts that need to be replaced with Ansible automation
3. Existing Ansible playbooks that need to be reviewed and potentially refactored

The migration complexity is relatively low as the repository contains minimal Chef-specific code and already includes Ansible playbooks. The estimated timeline for migration is 1-2 weeks, with the main effort focused on replacing the Chef InSpec tests with equivalent Ansible-compatible testing solutions and converting the Chef server deployment scripts to Ansible playbooks.

## Module Migration Plan

This repository contains a mix of Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-inspec-tests**:
    - Description: Chef InSpec tests for SSH profile and HTTPS website verification
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, HTTPS/TLS configuration testing

- **website-https-playbook**:
    - Description: Ansible playbook for deploying a secure HTTPS website with Apache
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle-fix-playbook**:
    - Description: Ansible playbook for fixing SSL vulnerabilities in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: SSL protocol configuration, service restart handlers

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `chef-and-ansible/README.md`: Documentation for using Chef InSpec with Ansible. Will need to be updated to reflect the new all-Ansible approach.
- `setup-automate/deploy-automate.sh`: Chef Automate deployment script. Will need to be converted to an Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Chef Server deployment script. Will need to be converted to an Ansible playbook or removed if Chef Server is no longer needed.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-compatible testing frameworks like:
  - Ansible's built-in `assert` module for basic testing
  - Molecule for comprehensive playbook testing
  - ansible-lint for static code analysis
  - ServerSpec or TestInfra for infrastructure testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - Ansible Galaxy for role/collection management
  - Git repositories for version control

### Security Considerations

- **SSL/TLS Configuration**: The existing playbooks configure Apache with TLS 1.2 and disable older protocols. This security practice should be maintained in the migrated Ansible playbooks.
  - Migration approach: Use the `community.crypto` collection for certificate management and the `apache2_module` module for Apache configuration.

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. This security check should be maintained.
  - Migration approach: Create an Ansible playbook that configures SSH according to security best practices and use Ansible's assert module or TestInfra to verify compliance.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically but should use Ansible Vault for any pre-existing keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing frameworks may require learning new testing approaches.
  - Mitigation: Use TestInfra which has a similar syntax to InSpec and integrates well with Ansible.

- **Chef Server Functionality**: If the organization relies on Chef Server features, equivalent functionality needs to be implemented in Ansible.
  - Mitigation: Evaluate which Chef Server features are actually being used and implement them using Ansible Tower/AWX or other tools in the Ansible ecosystem.

### Migration Order

1. **website-https-playbook** and **poodle-fix-playbook** (low risk, already Ansible)
   - Review and refactor existing Ansible playbooks for best practices
   - Update any deprecated syntax or modules

2. **chef-inspec-tests** (moderate complexity)
   - Convert InSpec tests to TestInfra or Ansible assert statements
   - Integrate with Molecule for comprehensive testing

3. **chef-automate-deployment** and **chef-server-deployment** (high complexity)
   - Create Ansible playbooks to replace the Chef Automate and Chef Server deployment scripts
   - Implement secure credential management using Ansible Vault

### Assumptions

1. The repository is primarily used for demonstration and educational purposes rather than production, based on the README description.
2. The Chef InSpec tests are used for compliance verification of infrastructure deployed by Ansible, not for testing Chef cookbooks.
3. The Chef Automate and Chef Server deployment scripts are used for setting up a Chef environment, which may be replaced entirely by Ansible Tower/AWX.
4. The existing Ansible playbooks are functional and follow best practices, requiring minimal changes.
5. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.
6. The security requirements include TLS 1.2 support and SSH hardening, which must be maintained in the migrated solution.
7. The migration will be performed by a team familiar with both Chef and Ansible concepts.