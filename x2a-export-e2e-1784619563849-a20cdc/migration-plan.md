# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more structured Ansible format and migrating Chef InSpec tests to Ansible-compatible testing frameworks. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

**CRITICAL PATH VERIFICATION:**
I have verified that there are no Puppet modules (no manifests/init.pp files), no Chef cookbooks (no recipes/default.rb files), and no PowerShell modules (no .psd1 files) in this repository.

The repository primarily contains:
1. Ansible playbooks (.yml files)
2. Chef InSpec test files (.rb files)
3. Bash deployment scripts (.sh files)

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS configuration, including self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec profile that checks SSH security configurations
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

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/index.html`: Simple HTML file used as a template for website deployment

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Migrate to Ansible Molecule for testing
  - Option 2: Use ansible-test framework
  - Option 3: Integrate with pytest-ansible for more complex testing scenarios

- **Test Kitchen with Vagrant**: Replace with:
  - Ansible Molecule for testing infrastructure
  - GitHub Actions or other CI/CD pipeline for automated testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open source upstream of Ansible Tower) for smaller deployments
  - GitLab CI/CD or GitHub Actions for pipeline orchestration

### Security Considerations

- **SSL Configuration**: The playbooks handle SSL security configurations that need to be preserved:
  - Self-signed certificate generation should be maintained or improved
  - TLS protocol restrictions (disabling SSLv3) must be preserved
  - Consider enhancing with more modern cipher suites

- **SSH Hardening**: The SSH security tests check for root login restrictions:
  - Ensure these security checks are converted to Ansible-compatible tests
  - Consider expanding SSH hardening with Ansible security roles

- **Vault/secrets management**: 
  - Hardcoded credentials in deploy scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deployment scripts (username/password pairs)

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to Ansible-compatible testing frameworks:
  - Challenge: InSpec has specific syntax for compliance testing that doesn't directly map to Ansible
  - Mitigation: Use Ansible assert modules or integrate with Molecule verification

- **Chef Server Deployment**: Replacing Chef Server deployment with Ansible management:
  - Challenge: Chef Server provides specific functionality for node management
  - Mitigation: Implement Ansible Automation Platform or AWX for similar capabilities

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Low risk, already in Ansible format, just need restructuring
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Moderate complexity, requires conversion to Ansible testing framework
3. **Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Higher complexity, requires complete replacement with Ansible roles

### Assumptions

1. The primary purpose of this repository is for demonstration/examples rather than production use
2. The InSpec tests are used for validation of the Ansible playbook results
3. The deployment scripts are used for setting up a test environment
4. No external dependencies or integrations beyond what's visible in the repository
5. No specific compliance requirements beyond what's tested in the InSpec profiles
6. The target environment is Ubuntu 20.04 as specified in the kitchen.yml file
7. The Apache configuration is for a basic web server with SSL and doesn't include complex configurations
8. The Chef Automate and Chef Infra Server deployment is for testing/demonstration purposes
9. No database or application tier configurations are present
10. No specific network or firewall configurations are required beyond default settings