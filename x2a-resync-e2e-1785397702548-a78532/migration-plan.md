# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting the existing Ansible playbooks to a more structured Ansible format and migrating the Chef InSpec tests to Ansible's testing capabilities. The estimated timeline for this migration is 1-2 weeks, with low complexity due to the limited number of components.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
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
    - Description: Chef InSpec profile that checks SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Simple HTML file used as a template for website deployment. Can be directly used in Ansible.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible's native testing capabilities or integrate with Ansible using ansible-test
- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure
- **Chef Automate/Infra Server**: Evaluate if these components are needed or if they can be replaced with Ansible Tower/AWX

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Ensure proper SSL configuration is maintained during migration.
- **SSH Security**: The InSpec tests verify SSH security configurations. Ensure these checks are maintained in the Ansible implementation.
- **Vault/secrets management**:
  - Hardcoded credentials in deploy scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbook and should be handled securely

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible testing mechanisms may require additional tooling or custom solutions.
- **Compliance Automation**: Maintaining the compliance automation capabilities currently provided by InSpec when moving to pure Ansible.

### Migration Order

1. Ansible Playbooks (website_https.yml, poodle_fix.yml) - Low risk, direct conversion to improved Ansible structure
2. Deployment Scripts (deploy-automate.sh, deploy-chef-server.sh) - Moderate complexity, requires deciding on Chef Automate replacement
3. InSpec Tests (website_https_verify.rb, ssh_profile.rb) - Higher complexity, requires finding Ansible testing equivalents

### Assumptions

1. The repository is primarily used for demonstration purposes as indicated by the README.md mentioning "working examples" and "how-tos".
2. The Chef InSpec tests are used alongside Ansible for compliance testing rather than as part of a larger Chef implementation.
3. The deployment scripts for Chef Automate and Chef Infra Server are standalone examples and not part of a larger Chef infrastructure.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs as specified in the kitchen.yml file.
5. There are no external dependencies or integrations beyond what is explicitly defined in the repository.
6. The migration goal is to consolidate on Ansible rather than maintain a hybrid Chef/Ansible approach.
7. The security requirements represented in the InSpec tests need to be maintained in the Ansible implementation.